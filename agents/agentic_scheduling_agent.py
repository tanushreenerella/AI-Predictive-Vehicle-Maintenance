import json
import re
from datetime import date, timedelta
from typing import Any, Dict, Optional

from agents.fallback_logic import fallback_schedule_decision
from agents.llm import call_llm


def agentic_scheduling_agent(
    vehicle_state: dict,
    user_constraints: Optional[Dict[str, Any]] = None,
    issue_context: Optional[Dict[str, Any]] = None,
    recommendation: Optional[Dict[str, Any]] = None,
    conversation_state: Optional[Dict[str, Any]] = None,
) -> dict:
    user_constraints = user_constraints or {}
    issue_context = issue_context or {}
    recommendation = recommendation or {}
    conversation_state = conversation_state or {}

    risk = vehicle_state.get("risk_level") or "UNKNOWN"
    prob = vehicle_state.get("failure_probability")
    last = vehicle_state.get("last_analyzed")
    prob_str = f"{int(prob * 100)}%" if prob is not None else "not yet analyzed"

    prompt = f"""You are an LLM-driven vehicle service scheduling agent.

Vehicle health data:
- Risk level: {risk}
- Engine failure probability: {prob_str}
- Last ML analysis: {last}

Diagnostic issue context:
{json.dumps(issue_context, default=str, indent=2)}

Service recommendation:
{json.dumps(recommendation, default=str, indent=2)}

Conversation state:
{json.dumps(conversation_state, default=str, indent=2)}

User constraints/current message:
{json.dumps(user_constraints, default=str, indent=2)}

Today is {date.today().isoformat()}.

Suggest appointment slots conversationally. Respect urgency first, then user time preferences.

Respond ONLY with valid JSON:
{{
  "recommended_urgency": "HIGH | MEDIUM | LOW",
  "reason": "short explanation referencing the actual data and constraints",
  "confidence": 0.85,
  "service_type": "specific service name",
  "suggested_slots": [
    {{"date": "YYYY-MM-DD", "time": "HH:MM", "label": "short human label"}}
  ],
  "selected_slot": {{"date": "YYYY-MM-DD", "time": "HH:MM", "label": "short human label"}},
  "reply": "one concise chat message asking for confirmation or acknowledging the best slot"
}}

Urgency rules:
- HIGH if failure probability > 70% or risk level is HIGH
- MEDIUM if failure probability 40-70% or risk level is MEDIUM
- LOW if failure probability < 40% or risk level is LOW / not analyzed
- HIGH slots should be today/tomorrow if possible
- MEDIUM slots should be within 3-7 days
- LOW slots can be 8-14 days out"""

    try:
        raw = call_llm(prompt)
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(match.group() if match else raw)
        return _normalise(data, vehicle_state, recommendation, user_constraints)
    except Exception as exc:
        print(f"[agentic_scheduling_agent] LLM fallback: {exc}")
        return _fallback_agentic_schedule(vehicle_state, recommendation, user_constraints)


def _normalise(
    data: Dict[str, Any],
    vehicle_state: Dict[str, Any],
    recommendation: Dict[str, Any],
    user_constraints: Dict[str, Any],
) -> Dict[str, Any]:
    fallback = _fallback_agentic_schedule(vehicle_state, recommendation, user_constraints)
    urgency = str(data.get("recommended_urgency") or fallback["recommended_urgency"]).upper()
    if urgency not in {"HIGH", "MEDIUM", "LOW"}:
        urgency = fallback["recommended_urgency"]

    slots = data.get("suggested_slots") if isinstance(data.get("suggested_slots"), list) else fallback["suggested_slots"]
    slots = [_normalise_slot(slot, fallback["selected_slot"]) for slot in slots[:3]]
    selected = _normalise_slot(data.get("selected_slot") or (slots[0] if slots else None), slots[0] if slots else fallback["selected_slot"])

    return {
        "recommended_urgency": urgency,
        "reason": str(data.get("reason") or fallback["reason"]),
        "confidence": float(data.get("confidence") or fallback["confidence"]),
        "service_type": str(data.get("service_type") or fallback["service_type"]),
        "suggested_slots": slots or fallback["suggested_slots"],
        "selected_slot": selected,
        "reply": str(data.get("reply") or fallback["reply"]),
        "agent": "agentic_scheduling_agent",
    }


def _fallback_agentic_schedule(
    vehicle_state: Dict[str, Any],
    recommendation: Dict[str, Any],
    user_constraints: Dict[str, Any],
) -> Dict[str, Any]:
    legacy = fallback_schedule_decision(vehicle_state)
    urgency = str(recommendation.get("urgency") or legacy.get("recommended_urgency") or "MEDIUM").upper()
    if urgency not in {"HIGH", "MEDIUM", "LOW"}:
        urgency = "MEDIUM"

    message = str(user_constraints.get("message") or "").lower()
    days = 1 if urgency == "HIGH" else 5 if urgency == "MEDIUM" else 10
    if "today" in message:
        days = 0
    elif "tomorrow" in message:
        days = 1
    elif "next week" in message:
        days = 7

    appt_date = date.today() + timedelta(days=days)
    appt_time = "10:00"
    if "afternoon" in message:
        appt_time = "14:00"
    elif "evening" in message:
        appt_time = "17:00"
    elif "morning" in message:
        appt_time = "09:30"

    service = recommendation.get("recommended_service") or "AI Recommended Service"
    slot = {
        "date": appt_date.isoformat(),
        "time": appt_time,
        "label": _slot_label(days, appt_time),
    }
    return {
        "recommended_urgency": urgency,
        "reason": recommendation.get("reasoning") or legacy.get("reason") or "Based on vehicle risk and chat constraints.",
        "confidence": float(legacy.get("confidence") or 0.75),
        "service_type": service,
        "suggested_slots": [
            slot,
            {
                "date": (appt_date + timedelta(days=1)).isoformat(),
                "time": appt_time,
                "label": "Backup slot",
            },
        ],
        "selected_slot": slot,
        "reply": (
            f"I found a {urgency.lower()} priority slot for {service}: "
            f"{slot['date']} at {slot['time']}. Reply 'confirm' and I will book it."
        ),
        "agent": "agentic_scheduling_agent",
    }


def _normalise_slot(slot: Any, fallback: Dict[str, str]) -> Dict[str, str]:
    if not isinstance(slot, dict):
        return fallback
    return {
        "date": str(slot.get("date") or fallback["date"]),
        "time": str(slot.get("time") or fallback["time"]),
        "label": str(slot.get("label") or fallback.get("label") or "Recommended slot"),
    }


def _slot_label(days: int, appt_time: str) -> str:
    if days == 0:
        day = "Today"
    elif days == 1:
        day = "Tomorrow"
    else:
        day = f"In {days} days"
    return f"{day} at {appt_time}"
