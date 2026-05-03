from datetime import date, time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agents.agentic_scheduling_agent import agentic_scheduling_agent
from agents.conversation_orchestrator import fresh_state, route_chat_turn
from backend.auth.dependencies import get_current_user
from backend.models.appointment import Appointment
from backend.models.user import User
from backend.models.vehicle import Vehicle
from backend.session import get_db

router = APIRouter(tags=["Agent Chat"])

_CONVERSATIONS: Dict[str, Dict[str, Any]] = {}


@router.post("/chat")
@router.post("/agent/chat")
def chat(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    message = payload.get("message", "")
    vehicle = _resolve_vehicle(db, user, payload.get("vehicle_id"))
    state_key = _state_key(user.id, vehicle.id if vehicle else "none", payload.get("session_id"))
    state = payload.get("state") or _CONVERSATIONS.get(state_key) or fresh_state()

    if _is_booking_confirmation(message, state):
        appointment_data = _create_appointment_from_state(db, user, vehicle, state)
        state["phase"] = "confirmed"
        _CONVERSATIONS[state_key] = state
        return {
            "reply": (
                f"Done. I booked {appointment_data['service_type']} for "
                f"{appointment_data['vehicle']} on {appointment_data['date']} at {appointment_data['time']}."
            ),
            "step": "booking_confirmation",
            "phase": "confirmed",
            "state": state,
            "recommendation": state.get("recommendation"),
            "scheduling": state.get("scheduling"),
            "appointment": appointment_data,
            "tool_calls": ["agentic_scheduling_agent"],
        }

    result = route_chat_turn(
        message=message,
        state=state,
        vehicle_state=_vehicle_state(vehicle),
        vehicle_label=_vehicle_label(vehicle),
    )
    _CONVERSATIONS[state_key] = result["state"]
    return {**result, "appointment": None}


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
    if payload.get("confirm"):
        appointment_data = _create_appointment(
            db=db,
            user=user,
            vehicle=vehicle,
            service_type=decision.get("service_type") or "AI Recommended Service",
            urgency=decision.get("recommended_urgency") or "MEDIUM",
            slot=decision.get("selected_slot") or {},
        )

    return {
        "scheduling": decision,
        "appointment": appointment_data,
        "reply": (
            f"Booked {appointment_data['service_type']} for {appointment_data['date']} at {appointment_data['time']}."
            if appointment_data else decision.get("reply")
        ),
    }


def _resolve_vehicle(db: Session, user: User, vehicle_id: Optional[str]) -> Optional[Vehicle]:
    query = db.query(Vehicle).filter(Vehicle.user_id == user.id)
    vehicles = query.all()
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
    return {
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


def _is_booking_confirmation(message: str, state: Dict[str, Any]) -> bool:
    msg = (message or "").lower()
    return (
        state.get("phase") == "scheduling"
        and bool((state.get("scheduling") or {}).get("selected_slot"))
        and any(token in msg for token in ["confirm", "book it", "yes", "go ahead", "please do"])
    )


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
        appointment_date = date.fromisoformat(str(slot.get("date")))
    except Exception:
        appointment_date = date.today()
    try:
        appointment_time = time.fromisoformat(str(slot.get("time") or "10:00"))
    except Exception:
        appointment_time = time(10, 0)

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
