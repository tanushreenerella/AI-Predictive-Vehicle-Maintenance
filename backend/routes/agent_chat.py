import logging
from datetime import date, time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agents.agentic_scheduling_agent import agentic_scheduling_agent
from agents.chat_agent import run_turn
from backend.auth.dependencies import get_current_user
from backend.models.appointment import Appointment
from backend.models.user import User
from backend.models.vehicle import Vehicle
from backend.session import get_db

router = APIRouter(tags=["Agent Chat"])

_CONVERSATIONS: Dict[str, Dict[str, Any]] = {}
_SUPPORTED_LANGUAGES = {"English", "Hindi", "Hinglish"}


def _fresh_state(vehicle_label: str, language: str = "English") -> Dict[str, Any]:
    return {
        "messages": [],
        "phase": "general",
        "symptom": None,
        "sensor_data": None,
        "diagnostic_answers": [],
        "issue_context": None,
        "recommendation": None,
        "scheduling": None,
        "vehicle_label": vehicle_label,
        "failure_probability": None,
        "risk_level": None,
        "next_agent": "",
        "language": language,
    }


@router.post("/chat")
@router.post("/agent/chat")
def chat(payload: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    message = payload.get("message", "")
    vehicle = _resolve_vehicle(db, user, payload.get("vehicle_id"))
    state_key = _state_key(user.id, vehicle.id if vehicle else "none", payload.get("session_id"))
    language = payload.get("language", "English")
    language = language if language in _SUPPORTED_LANGUAGES else "English"

    if payload.get("reset"):
        _CONVERSATIONS.pop(state_key, None)
        state = _fresh_state(_vehicle_label(vehicle), language)
        return {"reply": "", "step": "general", "phase": "general", "state": state,
                "recommendation": None, "scheduling": None, "appointment": None, "tool_calls": []}

    # server memory is the only source of truth (client state is ignored)
    state = _CONVERSATIONS.get(state_key) or _fresh_state(_vehicle_label(vehicle), language)
    state["language"] = language

    try:
        result = run_turn(
            state, message, _vehicle_label(vehicle), _vehicle_state(vehicle),
            book_fn=lambda rec, sched: _create_appointment_from_state(
                db, user, vehicle, {"recommendation": rec, "scheduling": sched}),
            language=language,
        )
        _CONVERSATIONS[state_key] = result["state"]
        return result
    except Exception:
        logging.exception("agent turn failed")
        return {"reply": "I'm having trouble processing that right now. Please try again.",
                "step": "error", "phase": state.get("phase", "general"), "state": state,
                "recommendation": None, "scheduling": None, "appointment": None, "tool_calls": []}
@router.post("/schedule-agentic")
def schedule_agentic(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicle = _resolve_vehicle(db, user, payload.get("vehicle_id"))
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    decision = agentic_scheduling_agent(
        vehicle_state=_vehicle_state(vehicle),
        user_constraints=payload.get("constraints") or {"message": payload.get("message", "")},
        issue_context=payload.get("issue_context"),
        recommendation=payload.get("recommendation"),
        conversation_state=payload.get("state"),
    )

    appointment_data = None
    proposed_slot = _proposed_slot(payload.get("state"))
    if payload.get("confirm") and proposed_slot:
        appointment_data = _create_appointment(
            db=db,
            user=user,
            vehicle=vehicle,
            service_type=decision.get("service_type") or "AI Recommended Service",
            urgency=decision.get("recommended_urgency") or "MEDIUM",
            slot=proposed_slot,
        )

    return {
        "scheduling": decision,
        "appointment": appointment_data,
        "reply": (
            f"Booked {appointment_data['service_type']} for {appointment_data['date']} at {appointment_data['time']}."
            if appointment_data
            else (
                "I need to propose a slot before I can book it. "
                "Ask me to find a slot, then confirm that proposed time."
                if payload.get("confirm") else decision.get("reply")
            )
        ),
    }


def _resolve_vehicle(db: Session, user: User, vehicle_id: Optional[str]) -> Optional[Vehicle]:
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == user.id).all()
    if vehicle_id:
        selected = next((v for v in vehicles if str(v.id) == str(vehicle_id)), None)
        if selected:
            return selected
    if not vehicles:
        return None
    return sorted(vehicles, key=lambda v: v.ai_failure_probability or 0, reverse=True)[0]


def _vehicle_state(vehicle: Optional[Vehicle]) -> Dict[str, Any]:
    if not vehicle:
        return {}
    if vehicle.ai_last_analyzed is None:
        return {"analyzed": False, "risk_level": None, "failure_probability": None,
                "component": None, "last_analyzed": None}
    return {
        "analyzed": True,
        "risk_level": vehicle.ai_risk_level,
        "failure_probability": vehicle.ai_failure_probability,
        "component": vehicle.ai_component,
        "last_analyzed": vehicle.ai_last_analyzed,
    }


def _vehicle_label(vehicle: Optional[Vehicle]) -> str:
    if not vehicle:
        return "your vehicle"
    model = f" {vehicle.model}" if vehicle.model else ""
    return f"{vehicle.name}{model}"


def _state_key(user_id: str, vehicle_id: str, session_id: Optional[str]) -> str:
    return f"{user_id}:{vehicle_id}:{session_id or 'default'}"


def _proposed_slot(state: Any) -> Optional[Dict[str, Any]]:
    """Accept confirmation only for a slot returned in a prior scheduling turn."""
    if not isinstance(state, dict):
        return None
    scheduling = state.get("scheduling")
    slot = scheduling.get("selected_slot") if isinstance(scheduling, dict) else None
    if not isinstance(slot, dict) or not slot.get("date") or not slot.get("time"):
        return None
    return slot


def _create_appointment_from_state(
    db: Session,
    user: User,
    vehicle: Optional[Vehicle],
    state: Dict[str, Any],
) -> Dict[str, Any]:
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    scheduling = state.get("scheduling") or {}
    slot = scheduling.get("selected_slot") or {}
    return _create_appointment(
        db=db,
        user=user,
        vehicle=vehicle,
        service_type=scheduling.get("service_type") or (state.get("recommendation") or {}).get("recommended_service") or "AI Recommended Service",
        urgency=scheduling.get("recommended_urgency") or (state.get("recommendation") or {}).get("urgency") or "MEDIUM",
        slot=slot,
    )


def _create_appointment(
    db: Session,
    user: User,
    vehicle: Vehicle,
    service_type: str,
    urgency: str,
    slot: Dict[str, Any],
) -> Dict[str, Any]:
    try:
        appointment_date = date.fromisoformat(str(slot["date"]))
        appointment_time = time.fromisoformat(str(slot["time"]))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid appointment slot")

    appointment = Appointment(
        user_id=user.id,
        vehicle_id=vehicle.id,
        service_type=service_type,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        urgency=urgency,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return {
        "appointment_id": str(appointment.id),
        "vehicle": vehicle.name,
        "date": appointment.appointment_date.isoformat(),
        "time": appointment.appointment_time.strftime("%H:%M"),
        "urgency": appointment.urgency,
        "service_type": appointment.service_type,
    }
