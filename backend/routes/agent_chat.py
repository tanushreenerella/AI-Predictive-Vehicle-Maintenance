from datetime import date, time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.orm import Session

from agents.agentic_graph.graph import vehicle_graph
from agents.agentic_graph.tools import find_appointment_slots
from agents.agentic_scheduling_agent import agentic_scheduling_agent
from backend.auth.dependencies import get_current_user
from backend.models.appointment import Appointment
from backend.models.user import User
from backend.models.vehicle import Vehicle
from backend.session import get_db

router = APIRouter(tags=["Agent Chat"])

_CONVERSATIONS: Dict[str, Dict[str, Any]] = {}


def _fresh_state(vehicle_label: str) -> Dict[str, Any]:
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
    }


def _to_graph_input(state: Dict[str, Any], message: str, vehicle_label: str) -> Dict[str, Any]:
    messages = []
    for m in state.get("messages", []):
        if isinstance(m, dict):
            if m.get("type") == "human":
                messages.append(HumanMessage(content=m["content"]))
            elif m.get("type") == "ai":
                messages.append(AIMessage(content=m["content"]))
        elif isinstance(m, (HumanMessage, AIMessage)):
            messages.append(m)
    messages.append(HumanMessage(content=message))

    return {
        "messages": messages,
        "phase": state.get("phase", "general"),
        "symptom": state.get("symptom"),
        "sensor_data": state.get("sensor_data"),
        "diagnostic_answers": state.get("diagnostic_answers", []),
        "issue_context": state.get("issue_context"),
        "recommendation": state.get("recommendation"),
        "scheduling": state.get("scheduling"),
        "vehicle_label": vehicle_label,
        "failure_probability": state.get("failure_probability"),
        "risk_level": state.get("risk_level"),
        "next_agent": state.get("next_agent", ""),
    }


def _serialize_state(result: Dict[str, Any]) -> Dict[str, Any]:
    messages = []
    for m in result.get("messages", []):
        if isinstance(m, HumanMessage):
            messages.append({"type": "human", "content": m.content})
        elif isinstance(m, AIMessage):
            messages.append({"type": "ai", "content": m.content})
        elif isinstance(m, dict):
            messages.append(m)
    return {
        "messages": messages,
        "phase": result.get("phase", "general"),
        "symptom": result.get("symptom"),
        "sensor_data": result.get("sensor_data"),
        "diagnostic_answers": result.get("diagnostic_answers", []),
        "issue_context": result.get("issue_context"),
        "recommendation": result.get("recommendation"),
        "scheduling": result.get("scheduling"),
        "vehicle_label": result.get("vehicle_label", ""),
        "failure_probability": result.get("failure_probability"),
        "risk_level": result.get("risk_level"),
        "next_agent": result.get("next_agent", ""),
    }


def _infer_tool_calls(prev_state: Dict[str, Any], result: Dict[str, Any]) -> list:
    """Determine which agents ran by comparing state before and after graph invoke."""
    tool_calls = ["supervisor"]
    if result.get("recommendation") and not prev_state.get("recommendation"):
        tool_calls.append("generate_service_recommendation")
    if result.get("scheduling") and not prev_state.get("scheduling"):
        tool_calls.append("find_appointment_slots")
    if len(result.get("diagnostic_answers", [])) > len(prev_state.get("diagnostic_answers", [])):
        tool_calls.append("diagnostic_questions_tool")
    if result.get("failure_probability") is not None and prev_state.get("failure_probability") is None:
        tool_calls.append("predict_engine_failure")
    return tool_calls


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
    state = payload.get("state") or _CONVERSATIONS.get(state_key) or _fresh_state(_vehicle_label(vehicle))

    # Scheduling intent — user said yes to a recommendation, find a slot
    if _is_scheduling_intent(message, state):
        slots = find_appointment_slots.invoke({
            "urgency": (state.get("recommendation") or {}).get("urgency", "MEDIUM"),
            "user_preference": message,
        })
        slot = slots.get("selected_slot", {})
        reply = f"I found a slot on {slot.get('date', 'TBD')} at {slot.get('time', '10:00')}. Reply 'confirm' to book it."
        state["scheduling"] = slots
        state["phase"] = "scheduling"
        _CONVERSATIONS[state_key] = state
        return {
            "reply": reply,
            "step": "scheduling",
            "phase": "scheduling",
            "state": state,
            "recommendation": state.get("recommendation"),
            "scheduling": slots,
            "appointment": None,
            "tool_calls": ["supervisor", "find_appointment_slots"],
        }

    # Booking confirmation is handled outside the graph (requires DB access)
    if _is_booking_confirmation(message, state):
        appointment_data = _create_appointment_from_state(db, user, vehicle, state)
        state["phase"] = "confirmed"
        _CONVERSATIONS[state_key] = state
        return {
            "reply": (
                f"Done. I've booked {appointment_data['service_type']} for "
                f"{appointment_data['vehicle']} on {appointment_data['date']} at {appointment_data['time']}."
            ),
            "step": "booking_confirmation",
            "phase": "confirmed",
            "state": state,
            "recommendation": state.get("recommendation"),
            "scheduling": state.get("scheduling"),
            "appointment": appointment_data,
            "tool_calls": ["supervisor", "agentic_scheduling_agent"],
        }

    try:
        graph_input = _to_graph_input(state, message, _vehicle_label(vehicle))
        result = vehicle_graph.invoke(graph_input)

        ai_messages = [m for m in result.get("messages", []) if isinstance(m, AIMessage)]
        reply = ai_messages[-1].content if ai_messages else "I'm here to help. Could you describe your vehicle's issue?"

        tool_calls = _infer_tool_calls(state, result)
        serialized = _serialize_state(result)
        _CONVERSATIONS[state_key] = serialized

        return {
            "reply": reply,
            "step": result.get("phase", "general"),
            "phase": result.get("phase", "general"),
            "state": serialized,
            "recommendation": result.get("recommendation"),
            "scheduling": result.get("scheduling"),
            "appointment": None,
            "tool_calls": tool_calls,
        }

    except Exception:
        return {
            "reply": "I'm having trouble processing that right now. Please try again.",
            "step": "error",
            "phase": state.get("phase", "general"),
            "state": state,
            "recommendation": None,
            "scheduling": None,
            "appointment": None,
            "tool_calls": [],
        }


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


def _is_scheduling_intent(message: str, state: Dict[str, Any]) -> bool:
    msg = (message or "").lower()
    return (
        state.get("recommendation") is not None
        and state.get("scheduling") is None
        and state.get("phase") in ("awaiting_booking", "recommended")
        and any(w in msg for w in ["yes", "ok", "okay", "sure", "book", "schedule", "please", "go ahead", "yep", "yeah"])
    )


def _is_booking_confirmation(message: str, state: Dict[str, Any]) -> bool:
    msg = (message or "").lower()
    return (
        state.get("phase") == "scheduling"
        and bool((state.get("scheduling") or {}).get("selected_slot"))
        and any(token in msg for token in [
            "confirm", "book it", "yes", "go ahead", "please do",
            "book", "ok", "okay", "sure", "yep", "yeah", "do it",
        ])
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
