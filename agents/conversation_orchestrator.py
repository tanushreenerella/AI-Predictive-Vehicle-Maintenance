import json
import re
from copy import deepcopy
from typing import Any, Dict, Optional

from agents.agentic_scheduling_agent import agentic_scheduling_agent
from agents.llm import call_llm
from agents.tools.diagnostic_tools import diagnostic_questions_tool, service_recommendation_tool


INITIAL_STATE: Dict[str, Any] = {
    "phase": "general",
    "symptom": None,
    "pending_question": None,
    "diagnostic_answers": [],
    "issue_context": None,
    "recommendation": None,
    "scheduling": None,
}


def fresh_state() -> Dict[str, Any]:
    return deepcopy(INITIAL_STATE)


def route_chat_turn(
    message: str,
    state: Optional[Dict[str, Any]] = None,
    vehicle_state: Optional[Dict[str, Any]] = None,
    vehicle_label: str = "your vehicle",
) -> Dict[str, Any]:
    """
    Router agent for diagnosis -> recommendation -> scheduling.

    It keeps orchestration deterministic at the state boundary, while using the
    LLM to classify intent and the tools/agents to decide content.
    """
    state = _merge_state(state)
    vehicle_state = vehicle_state or {}
    message = (message or "").strip()

    if not message:
        return _response("Please describe what is happening with your vehicle.", state, "general")

    intent = _classify_intent(message, state)

    if state["phase"] == "diagnosing" and state.get("pending_question"):
        return _handle_diagnostic_answer(message, state, vehicle_state)

    if intent == "diagnosis":
        return _start_diagnosis(message, state, vehicle_state)

    if intent == "scheduling" or (state["phase"] in {"recommended", "scheduling"} and _is_affirmative(message)):
        return _handle_scheduling(message, state, vehicle_state, vehicle_label)

    if state["phase"] == "scheduling":
        return _handle_scheduling(message, state, vehicle_state, vehicle_label)

    reply = _general_reply(message, vehicle_state, vehicle_label)
    return _response(reply, state, "general")


def _start_diagnosis(message: str, state: Dict[str, Any], vehicle_state: Dict[str, Any]) -> Dict[str, Any]:
    state.update({
        "phase": "diagnosing",
        "symptom": message,
        "pending_question": None,
        "diagnostic_answers": [],
        "issue_context": None,
        "recommendation": None,
        "scheduling": None,
    })
    tool_result = diagnostic_questions_tool(message, [])
    state["issue_context"] = tool_result.get("issue_context")
    question = _first_question(tool_result)
    state["pending_question"] = question
    return _response(question, state, "diagnostic_question", tool_calls=["diagnostic_questions_tool"])


def _handle_diagnostic_answer(message: str, state: Dict[str, Any], vehicle_state: Dict[str, Any]) -> Dict[str, Any]:
    state["diagnostic_answers"].append({
        "question": state.get("pending_question") or "",
        "answer": message,
    })
    state["pending_question"] = None

    tool_result = diagnostic_questions_tool(state.get("symptom") or message, state["diagnostic_answers"])
    state["issue_context"] = tool_result.get("issue_context") or state.get("issue_context")

    if not tool_result.get("enough_context"):
        question = _first_question(tool_result)
        state["pending_question"] = question
        state["phase"] = "diagnosing"
        return _response(question, state, "diagnostic_question", tool_calls=["diagnostic_questions_tool"])

    recommendation = service_recommendation_tool(state["issue_context"] or {}, vehicle_state)
    state["recommendation"] = recommendation
    state["phase"] = "recommended"
    reply = (
        "Based on what you described, here is the recommendation. "
        "Would you like me to book a service appointment for you?"
    )
    return _response(
        reply,
        state,
        "recommendation",
        recommendation=recommendation,
        tool_calls=["diagnostic_questions_tool", "service_recommendation_tool"],
    )


def _handle_scheduling(
    message: str,
    state: Dict[str, Any],
    vehicle_state: Dict[str, Any],
    vehicle_label: str,
) -> Dict[str, Any]:
    decision = agentic_scheduling_agent(
        vehicle_state=vehicle_state,
        user_constraints={"message": message},
        issue_context=state.get("issue_context"),
        recommendation=state.get("recommendation"),
        conversation_state=state,
    )
    state["phase"] = "scheduling"
    state["scheduling"] = decision
    slot = decision.get("selected_slot") or (decision.get("suggested_slots") or [{}])[0]
    reply = decision.get("reply")
    if not reply:
        date_text = slot.get("date", "the recommended date")
        time_text = slot.get("time", "10:00")
        reply = (
            f"I found a suitable slot for {vehicle_label}: {date_text} at {time_text}. "
            "Reply 'confirm' and I will book it."
        )
    return _response(
        reply,
        state,
        "scheduling",
        scheduling=decision,
        tool_calls=["agentic_scheduling_agent"],
    )


def _classify_intent(message: str, state: Dict[str, Any]) -> str:
    msg = message.lower()
    if _is_affirmative(msg) and state.get("phase") in {"recommended", "scheduling"}:
        return "scheduling"
    if any(w in msg for w in ["book", "schedule", "appointment", "slot", "service visit", "confirm"]):
        return "scheduling"
    complaint_words = [
        "noise", "rattle", "knock", "grind", "squeal", "overheat", "hot", "leak",
        "smoke", "warning", "light", "brake", "vibrat", "shake", "start", "battery",
        "power", "stall", "engine", "oil", "coolant",
    ]
    if any(w in msg for w in complaint_words):
        return "diagnosis"

    try:
        prompt = f"""Classify the user's vehicle assistant intent.
Current state: {json.dumps(state, default=str)}
User message: {message}

Return ONLY JSON: {{"intent":"diagnosis|follow_up_answer|scheduling|general"}}
"""
        data = _extract_json(call_llm(prompt))
        intent = str(data.get("intent", "general"))
        return intent if intent in {"diagnosis", "follow_up_answer", "scheduling", "general"} else "general"
    except Exception:
        return "general"


def _general_reply(message: str, vehicle_state: Dict[str, Any], vehicle_label: str) -> str:
    risk = vehicle_state.get("risk_level") or "unknown"
    prob = vehicle_state.get("failure_probability")
    prob_text = f"{int(float(prob) * 100)}%" if isinstance(prob, (int, float)) else "not analyzed"
    try:
        prompt = f"""You are ProactiveAI, a concise vehicle service assistant.
Vehicle: {vehicle_label}
Risk level: {risk}
Failure probability: {prob_text}
User message: {message}

Answer directly in under 90 words. If the user describes a symptom, tell them you can diagnose it and ask them to describe it.
"""
        return call_llm(prompt)
    except Exception:
        return (
            f"I can help with diagnostics, service recommendations, and booking for {vehicle_label}. "
            "Tell me the symptom you are noticing, or say you want to schedule service."
        )


def _response(
    reply: str,
    state: Dict[str, Any],
    step: str,
    recommendation: Optional[Dict[str, Any]] = None,
    scheduling: Optional[Dict[str, Any]] = None,
    tool_calls: Optional[list] = None,
) -> Dict[str, Any]:
    return {
        "reply": reply,
        "step": step,
        "phase": state.get("phase", "general"),
        "state": state,
        "recommendation": recommendation,
        "scheduling": scheduling,
        "tool_calls": tool_calls or [],
    }


def _merge_state(state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    merged = fresh_state()
    if isinstance(state, dict):
        merged.update({k: v for k, v in state.items() if k in merged})
    return merged


def _first_question(tool_result: Dict[str, Any]) -> str:
    questions = tool_result.get("questions") or []
    return questions[0] if questions else "Can you describe when the problem happens most often?"


def _is_affirmative(message: str) -> bool:
    msg = message.lower().strip()
    return any(token in msg for token in ["yes", "yeah", "sure", "ok", "okay", "go ahead", "book it", "confirm", "please do"])


def _extract_json(raw: str) -> Dict[str, Any]:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    return json.loads(match.group() if match else cleaned)
