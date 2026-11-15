import logging
from datetime import date, time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agents.agentic_scheduling_agent import agentic_scheduling_agent
from agents.chat_agent import run_turn
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.models.vehicle import Vehicle
from backend.rate_limit import EXPENSIVE_LIMIT, limiter
from backend.services.availability import (
    URGENCY_WINDOWS,
    InvalidSlot,
    SlotUnavailable,
    book_slot,
    free_slots_for_urgency,
    to_http,
)
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


MAX_CHAT_MESSAGE = 1000
CHAT_FAILED_REPLY = "Sorry, I couldn't finish that. Please try again."


class ChatRequest(BaseModel):
    message: str = Field(default="", max_length=MAX_CHAT_MESSAGE)
    vehicle_id: Optional[str] = None
    session_id: Optional[str] = None
    language: str = "English"
    reset: bool = False
    # Set only by the frontend's "Confirm booking" button. The agent can book
    # on this request only; a typed "yes" never books on its own.
    confirm_booking: bool = False


@router.post("/chat")
@router.post("/agent/chat")
@limiter.limit(EXPENSIVE_LIMIT)  # one bucket shared by both paths: they are the same endpoint
def chat(request: Request, payload: ChatRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    vehicle = _resolve_vehicle(db, user, payload.vehicle_id)
    state_key = _state_key(user.id, vehicle.id if vehicle else "none", payload.session_id)
    language = payload.language if payload.language in _SUPPORTED_LANGUAGES else "English"

    if payload.reset:
        _CONVERSATIONS.pop(state_key, None)
        state = _fresh_state(_vehicle_label(vehicle), language)
        return {"reply": "", "step": "general", "phase": "general", "state": state,
                "recommendation": None, "scheduling": None, "appointment": None,
                "confirm_required": False, "tool_calls": []}

    # server memory is the only source of truth (client state is ignored)
    stored = _CONVERSATIONS.get(state_key)
    state = {**(stored or _fresh_state(_vehicle_label(vehicle), language)), "language": language}

    try:
        result = run_turn(
            state, payload.message, _vehicle_label(vehicle), _vehicle_state(vehicle),
            book_fn=lambda rec, sched: _book_from_agent_state(
                db, user, vehicle, {"recommendation": rec, "scheduling": sched}),
            language=language,
            confirm_booking=payload.confirm_booking,
        )
        _CONVERSATIONS[state_key] = result["state"]
        return result
    except Exception:
        # Timeout, recursion limit or LLM error: answer 200 and keep the stored
        # conversation exactly as it was, so the user can simply retry.
        logging.exception("agent turn failed")
        return {"reply": CHAT_FAILED_REPLY,
                "step": "error", "phase": state.get("phase", "general"), "state": stored or state,
                "recommendation": None, "scheduling": None, "appointment": None,
                "confirm_required": False, "tool_calls": []}
@router.post("/schedule-agentic")
def schedule_agentic(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicle = _resolve_vehicle(db, user, payload.get("vehicle_id"))
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    message = payload.get("message", "")
    decision = agentic_scheduling_agent(
        vehicle_state=_vehicle_state(vehicle),
        user_constraints=payload.get("constraints") or {"message": message},
        issue_context=payload.get("issue_context"),
        recommendation=payload.get("recommendation"),
        conversation_state=payload.get("state"),
    )
    urgency = decision.get("recommended_urgency") or "MEDIUM"
    service_type = decision.get("service_type") or "AI Recommended Service"

    if payload.get("confirm"):
        slot = _proposed_slot(payload.get("state"))
        if not slot:
            return {"scheduling": decision, "appointment": None,
                    "reply": "I need to propose a slot before I can book it. "
                             "Ask me to find a slot, then confirm that proposed time."}
        # The slot comes from the client, so it is only a request: book_slot
        # re-validates it and re-checks bay availability before writing.
        appointment_data = _create_appointment(db, user, vehicle, service_type, urgency, slot)
        return {"scheduling": decision, "appointment": appointment_data,
                "reply": f"Booked {appointment_data['service_type']} for "
                         f"{appointment_data['date']} at {appointment_data['time']}."}

    # Never pass on slots the LLM made up: offer only real free slots.
    free = free_slots_for_urgency(db, urgency, message)
    decision["suggested_slots"] = free[:3]
    decision["selected_slot"] = free[0] if free else None
    if free:
        decision["reply"] = (f"The earliest free {urgency.lower()} priority slot is "
                             f"{free[0]['date']} at {free[0]['time']}. Reply 'confirm' to book it.")
    else:
        first, last = URGENCY_WINDOWS.get(urgency.upper(), URGENCY_WINDOWS["MEDIUM"])
        decision["reply"] = (f"There are no free slots {first}-{last} days from now. "
                             "Please contact the service center.")
    return {"scheduling": decision, "appointment": None, "reply": decision["reply"]}


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


def _book_from_agent_state(
    db: Session,
    user: User,
    vehicle: Optional[Vehicle],
    state: Dict[str, Any],
) -> Dict[str, Any]:
    """book_fn for the chat agent: returns {"error": ...} instead of raising,
    so the agent can tell the user and propose another slot."""
    if not vehicle:
        return {"error": "No vehicle found. Add a vehicle before booking."}
    scheduling = state.get("scheduling") or {}
    recommendation = state.get("recommendation") or {}
    try:
        return _create_appointment(
            db, user, vehicle,
            service_type=scheduling.get("service_type") or recommendation.get("recommended_service") or "AI Recommended Service",
            urgency=scheduling.get("recommended_urgency") or recommendation.get("urgency") or "MEDIUM",
            slot=scheduling.get("selected_slot") or {},
        )
    except HTTPException as exc:
        return {"error": exc.detail}


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
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=422, detail="Invalid appointment slot")

    urgency = str(urgency).upper()
    if urgency not in URGENCY_WINDOWS:
        urgency = "MEDIUM"

    try:
        appointment = book_slot(
            db,
            user_id=user.id,
            vehicle_id=vehicle.id,
            service_type=service_type,
            urgency=urgency,
            day=appointment_date,
            start=appointment_time,
        )
    except (InvalidSlot, SlotUnavailable) as exc:
        raise to_http(exc)

    return {
        "appointment_id": str(appointment.id),
        "vehicle": vehicle.name,
        "date": appointment.appointment_date.isoformat(),
        "time": appointment.appointment_time.strftime("%H:%M"),
        "bay": appointment.bay,
        "urgency": appointment.urgency,
        "service_type": appointment.service_type,
    }
