from __future__ import annotations
import json
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

load_dotenv()

try:
    from langchain.agents import create_agent

    def _build(model, tools, prompt):
        return create_agent(model, tools=tools, system_prompt=prompt)
except ImportError:
    from langgraph.prebuilt import create_react_agent

    def _build(model, tools, prompt):
        return create_react_agent(model, tools, prompt=prompt)

from agents.agentic_graph.tools import find_appointment_slots, generate_service_recommendation

MODEL = "openai/gpt-oss-120b"

SYSTEM = """You are the AI assistant of a predictive vehicle-maintenance app. Vehicle: {vehicle}.
Users may write English, Hindi or Hinglish; reply in the user's language. Be concise.
The server controls the booking state machine. Do not call a booking tool unless it
is explicitly allowed for this turn. For ordinary questions, answer directly.
Never say something is booked unless book_appointment succeeded.
Current context: recommendation={rec}; proposed_slot={slot}"""


def make_tools(ctx: Dict[str, Any], vehicle_info: Dict[str, Any], book_fn):
    @tool
    def get_vehicle_health() -> dict:
        """Get the stored AI health analysis of the user's vehicle (risk level, failure probability, component, last analyzed)."""
        return _get_vehicle_health(vehicle_info)

    @tool
    def recommend_service(symptom_summary: str, urgency_hint: str = "MEDIUM") -> dict:
        """Create a service recommendation from what the user described. urgency_hint is HIGH, MEDIUM or LOW."""
        if ctx.get("allowed_action") != "recommend":
            return {"error": "Recommendations are not available in this turn."}
        if ctx.get("action_executed"):
            return {"error": "Only one booking action is allowed per turn."}
        u = urgency_hint.upper()
        rec = generate_service_recommendation.invoke({
            "issue_context": {"summary": symptom_summary},
            "risk_level": u if u in {"HIGH", "MEDIUM", "LOW"} else "MEDIUM",
        })
        ctx["recommendation"] = rec
        ctx["action_executed"] = "recommend"
        return rec

    @tool
    def propose_appointment_slot(time_preference: str = "") -> dict:
        """Find an appointment slot for the current recommendation. Only proposes, does NOT book."""
        if ctx.get("allowed_action") != "propose":
            return {"error": "A slot can only be proposed after a prior recommendation is accepted."}
        if ctx.get("action_executed"):
            return {"error": "Only one booking action is allowed per turn."}
        if not ctx.get("recommendation_from_prior_turn"):
            return {"error": "A recommendation must be shown in a prior turn before proposing a slot."}
        rec = ctx.get("recommendation") or {}
        urgency = rec.get("urgency", "MEDIUM")
        slots = find_appointment_slots.invoke({"urgency": urgency, "user_preference": time_preference})
        slots["service_type"] = rec.get("recommended_service", "Full diagnostic inspection")
        slots["recommended_urgency"] = urgency
        ctx["scheduling"] = slots
        ctx["proposed_this_turn"] = True
        ctx["action_executed"] = "propose"
        return slots

    @tool
    def book_appointment(user_confirmed: bool) -> dict:
        """Book the slot that was last proposed. user_confirmed=true ONLY if the user's latest message clearly agrees to that slot."""
        if ctx.get("allowed_action") != "book":
            return {"error": "A booking requires an explicit confirmation of a previously proposed slot."}
        if ctx.get("action_executed"):
            return {"error": "Only one booking action is allowed per turn."}
        if ctx.get("proposed_this_turn"):
            return {"error": "You just proposed this slot. Show it to the user and wait for their reply before booking."}
        if not (ctx.get("scheduling") or {}).get("selected_slot"):
            return {"error": "No slot proposed yet. Call propose_appointment_slot first."}
        if not user_confirmed:
            return {"error": "User has not confirmed. Ask them to confirm the slot."}
        appt = book_fn(ctx.get("recommendation") or {}, ctx["scheduling"])
        ctx["appointment"] = appt
        ctx["scheduling"] = None  # prevents double booking
        ctx["action_executed"] = "book"
        return appt

    return [get_vehicle_health, recommend_service, propose_appointment_slot, book_appointment]


def run_turn(state: dict, message: str, vehicle_label: str, vehicle_info: dict, book_fn) -> dict:
    """Run one chat turn with exactly one possible booking-state action.

    Recommendations, slot proposals, and booking confirmations intentionally
    happen on separate user turns. The model may help with normal conversation,
    but it cannot advance this state machine by chaining tools.
    """
    ctx = {
        "recommendation": state.get("recommendation"),
        "scheduling": state.get("scheduling"),
        "appointment": None,
        "proposed_this_turn": False,
        "recommendation_from_prior_turn": bool(state.get("recommendation")),
        "allowed_action": "none",
        "action_executed": None,
    }

    if _is_health_question(message):
        return _health_turn(state, message, vehicle_label, vehicle_info)

    if state.get("phase") == "confirmed" and _is_acknowledgement(message):
        return _turn_response(
            state, message, vehicle_label,
            "You’re welcome. Your appointment is confirmed.", "confirmed",
            recommendation=None, scheduling=None, appointment=None,
            tool_calls=["supervisor"],
            expose_recommendation=False, expose_scheduling=False,
            clear_booking_state=True,
        )

    if _is_explicit_confirmation(message) and _has_proposed_slot(state):
        ctx["allowed_action"] = "book"
        appointment = _book(ctx, book_fn)
        return _turn_response(
            state, message, vehicle_label,
            reply=(
                f"Done. I've booked {appointment['service_type']} for {appointment['vehicle']} "
                f"on {appointment['date']} at {appointment['time']}."
            ),
            phase="confirmed",
            recommendation=None,
            scheduling=None,
            appointment=appointment,
            tool_calls=["supervisor", "book_appointment"],
        )

    if _is_slot_agreement(message) and ctx["recommendation"] and not _has_proposed_slot(state):
        ctx["allowed_action"] = "propose"
        scheduling = _propose(ctx, message)
        slot = scheduling["selected_slot"]
        return _turn_response(
            state, message, vehicle_label,
            reply=f"I found a slot on {slot['date']} at {slot['time']}. Reply 'confirm' to book it.",
            phase="scheduling",
            recommendation=ctx["recommendation"],
            scheduling=scheduling,
            appointment=None,
            tool_calls=["supervisor", "propose_appointment_slot"],
            expose_recommendation=False,
            expose_scheduling=True,
        )

    if _is_booking_request(message):
        # A booking request always starts (or restarts) with a recommendation.
        # It never creates a slot in the same assistant turn.
        ctx["allowed_action"] = "recommend"
        recommendation = _recommend(ctx, message, vehicle_info)
        return _turn_response(
            state, message, vehicle_label,
            reply="I recommend " + recommendation["recommended_service"] + ". Would you like me to find an available slot?",
            phase="recommended",
            recommendation=recommendation,
            scheduling=None,
            appointment=None,
            tool_calls=["supervisor", "recommend_service"],
            expose_recommendation=True,
            expose_scheduling=False,
        )

    # Normal conversation cannot surface an old slot card. The stored slot is
    # retained only to allow a later explicit confirmation.
    slot = (ctx["scheduling"] or {}).get("selected_slot")
    prompt = SYSTEM.format(
        vehicle=vehicle_label,
        rec=json.dumps(ctx["recommendation"]) if ctx["recommendation"] else "none",
        slot=json.dumps(slot) if slot else "none",
    )
    agent = _build(ChatGroq(model=MODEL, temperature=0.2), make_tools(ctx, vehicle_info, book_fn), prompt)

    history = []
    for m in state.get("messages", [])[-20:]:
        if isinstance(m, dict):
            history.append((HumanMessage if m.get("type") == "human" else AIMessage)(content=m.get("content", "")))
    history.append(HumanMessage(content=message))

    for attempt in range(2):
        try:
            result = agent.invoke({"messages": history})
            break
        except Exception:
            if attempt == 1:
                raise

    new_msgs = result["messages"][len(history):]
    tools_used = [tc["name"] for m in new_msgs if isinstance(m, AIMessage) for tc in (m.tool_calls or [])]
    reply = next(
        (m.content for m in reversed(new_msgs)
         if isinstance(m, AIMessage) and m.content and not m.tool_calls),
        "Sorry, I couldn't process that. Please try again.",
    )
    if isinstance(reply, list):
        reply = " ".join(b.get("text", "") for b in reply if isinstance(b, dict))

    phase = state.get("phase", "general")
    return _turn_response(
        state, message, vehicle_label, reply, phase,
        recommendation=ctx["recommendation"], scheduling=ctx["scheduling"],
        appointment=None, tool_calls=["supervisor"] + tools_used,
        expose_recommendation=False, expose_scheduling=False,
    )


def _recommend(ctx: Dict[str, Any], message: str, vehicle_info: Dict[str, Any]) -> Dict[str, Any]:
    """Perform the recommendation-only booking turn."""
    if ctx.get("allowed_action") != "recommend" or ctx.get("action_executed"):
        raise RuntimeError("recommendation is not allowed in this turn")
    risk = str(vehicle_info.get("risk_level") or "MEDIUM").upper()
    if risk not in {"HIGH", "MEDIUM", "LOW"}:
        risk = "MEDIUM"
    recommendation = generate_service_recommendation.invoke({
        "issue_context": {"summary": message or "Requested service appointment"},
        "risk_level": risk,
    })
    ctx["recommendation"] = recommendation
    ctx["scheduling"] = None
    ctx["action_executed"] = "recommend"
    return recommendation


def _propose(ctx: Dict[str, Any], message: str) -> Dict[str, Any]:
    """Perform the slot-proposal-only booking turn."""
    if (
        ctx.get("allowed_action") != "propose"
        or ctx.get("action_executed")
        or not ctx.get("recommendation_from_prior_turn")
    ):
        raise RuntimeError("slot proposal is not allowed in this turn")
    recommendation = ctx.get("recommendation") or {}
    slots = find_appointment_slots.invoke({
        "urgency": recommendation.get("urgency", "MEDIUM"),
        "user_preference": message,
    })
    slots["service_type"] = recommendation.get("recommended_service", "Full diagnostic inspection")
    slots["recommended_urgency"] = recommendation.get("urgency", "MEDIUM")
    slots["reason"] = recommendation.get("reasoning", "Based on the service recommendation.")
    ctx["scheduling"] = slots
    ctx["proposed_this_turn"] = True
    ctx["action_executed"] = "propose"
    return slots


def _book(ctx: Dict[str, Any], book_fn) -> Dict[str, Any]:
    """Perform the confirmation-only booking turn for a previously proposed slot."""
    if (
        ctx.get("allowed_action") != "book"
        or ctx.get("action_executed")
        or ctx.get("proposed_this_turn")
        or not (ctx.get("scheduling") or {}).get("selected_slot")
    ):
        raise RuntimeError("booking is not allowed without a prior proposed slot")
    appointment = book_fn(ctx.get("recommendation") or {}, ctx["scheduling"])
    ctx["appointment"] = appointment
    ctx["recommendation"] = None
    ctx["scheduling"] = None
    ctx["action_executed"] = "book"
    return appointment


def _health_turn(state: dict, message: str, vehicle_label: str, vehicle_info: Dict[str, Any]) -> dict:
    """Return stored health only, deliberately discarding stale booking UI state."""
    health = _get_vehicle_health(vehicle_info)
    analyzed = bool(health.get("analyzed"))
    if not analyzed:
        reply = f"{vehicle_label} has not been analyzed yet. Run AI Analysis to get its health status."
    else:
        risk = health.get("risk_level") or "unavailable"
        probability = health.get("failure_probability")
        probability_text = f"{float(probability) * 100:.0f}%" if isinstance(probability, (int, float)) else "unavailable"
        reply = f"{vehicle_label} is currently {risk} risk with a {probability_text} predicted failure probability."
    return _turn_response(
        state, message, vehicle_label, reply, "general",
        recommendation=None, scheduling=None, appointment=None,
        tool_calls=["supervisor", "get_vehicle_health"],
        expose_recommendation=False, expose_scheduling=False,
        clear_booking_state=True,
    )


def _get_vehicle_health(vehicle_info: Dict[str, Any]) -> Dict[str, Any]:
    """The shared implementation behind the health tool and health-only turn."""
    return json.loads(json.dumps(vehicle_info, default=str))


def _turn_response(
    state: dict,
    message: str,
    vehicle_label: str,
    reply: str,
    phase: str,
    recommendation: Any,
    scheduling: Any,
    appointment: Any,
    tool_calls: list,
    expose_recommendation: bool = False,
    expose_scheduling: bool = False,
    clear_booking_state: bool = False,
) -> dict:
    """Preserve the response contract while exposing cards only for this turn."""
    stored_recommendation = None if clear_booking_state or appointment else recommendation
    stored_scheduling = None if clear_booking_state or appointment else scheduling
    new_state = {
        **state,
        "messages": (state.get("messages", []) + [
            {"type": "human", "content": message},
            {"type": "ai", "content": reply},
        ])[-30:],
        "recommendation": stored_recommendation,
        "scheduling": stored_scheduling,
        "phase": phase,
        "vehicle_label": vehicle_label,
    }
    return {
        "reply": reply,
        "step": phase,
        "phase": phase,
        "state": new_state,
        "recommendation": recommendation if expose_recommendation else None,
        "scheduling": scheduling if expose_scheduling else None,
        "appointment": appointment,
        "tool_calls": tool_calls,
    }


def _is_booking_request(message: str) -> bool:
    msg = (message or "").lower()
    return any(token in msg for token in ("book", "schedule", "appointment", "service appointment"))


def _is_slot_agreement(message: str) -> bool:
    msg = (message or "").lower().strip()
    return msg in {"yes", "yes, find a slot", "find a slot", "okay", "ok", "sure", "go ahead", "haan"} or "find a slot" in msg


def _is_explicit_confirmation(message: str) -> bool:
    msg = (message or "").lower()
    return "confirm" in msg or "book it" in msg


def _has_proposed_slot(state: dict) -> bool:
    slot = ((state.get("scheduling") or {}).get("selected_slot")) if isinstance(state, dict) else None
    return isinstance(slot, dict) and bool(slot.get("date")) and bool(slot.get("time"))


def _is_health_question(message: str) -> bool:
    msg = (message or "").lower()
    return (
        "health" in msg
        or "status" in msg
        or "next maintenance" in msg
        or "maintenance due" in msg
        or "when is my next service" in msg
    )


def _is_acknowledgement(message: str) -> bool:
    return (message or "").lower().strip() in {"thanks", "thank you", "thankyou", "thx", "okay thanks"}
