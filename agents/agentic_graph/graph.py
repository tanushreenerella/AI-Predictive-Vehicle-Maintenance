from __future__ import annotations
import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from agents.agentic_graph.state import VehicleAgentState
from agents.agentic_graph.tools import (
    MAX_DIAGNOSTIC_QUESTIONS,
    find_appointment_slots,
    generate_service_recommendation,
    get_diagnostic_question,
    predict_engine_failure,
)

load_dotenv()

MIN_DIAGNOSTIC_ANSWERS = 2


# ── Supervisor ────────────────────────────────────────────────────────────────

def supervisor_node(state: VehicleAgentState) -> Dict[str, Any]:
    phase = state.get("phase", "general")
    answers_count = len(state.get("diagnostic_answers", []))
    has_recommendation = bool(state.get("recommendation"))
    has_sensor = bool(state.get("sensor_data"))
    has_scheduling = bool(state.get("scheduling"))
    has_risk = bool(state.get("risk_level"))

    if phase in {"scheduling", "confirmed"} or has_scheduling:
        next_agent = "end"
    elif has_sensor and not has_risk:
        next_agent = "sensor_ml"
    elif phase == "recommended":
        next_agent = "recommendation"
    elif phase in {"general", "diagnosing"} and answers_count < MAX_DIAGNOSTIC_QUESTIONS:
        next_agent = "diagnostic"
    elif phase in {"general", "diagnosing"}:
        next_agent = "recommendation"
    elif phase == "awaiting_booking" and has_recommendation:
        next_agent = "end"
    else:
        next_agent = "diagnostic"

    return {"next_agent": next_agent}


# ── Agent nodes — each calls its tool directly ────────────────────────────────
def diagnostic_node(state: VehicleAgentState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    symptom = state.get("symptom") or (messages[-1].content if messages else "")
    answers = list(state.get("diagnostic_answers", []))

    if state.get("phase") == "diagnosing" and messages:
        last_msg = messages[-1]
        if isinstance(last_msg, HumanMessage):
            answers.append({"answer": last_msg.content})

    # Hard limit — force move to recommendation once max answers reached
    if len(answers) >= MAX_DIAGNOSTIC_QUESTIONS:
        return {
            "messages": [],
            "symptom": symptom,
            "diagnostic_answers": answers,
            "issue_context": {
                "symptom": symptom,
                "answers": answers,
                "summary": f"{symptom}. " + "; ".join([a.get("answer", "") for a in answers]),
            },
            "phase": "recommended",
        }

    tool_result = get_diagnostic_question.invoke({
        "symptom": symptom,
        "answers_so_far": answers,
    })

    question = tool_result.get("question", "Can you describe when the problem happens most often?")
    enough = bool(tool_result.get("enough_context", False)) and len(answers) >= MIN_DIAGNOSTIC_ANSWERS
    if not enough and not question:
        question = "Can you describe when this problem happens most often?"

    return {
        "messages": [AIMessage(content=question)] if not enough else [],
        "symptom": symptom,
        "diagnostic_answers": answers,
        "issue_context": {
            "symptom": symptom,
            "answers": answers,
            "summary": f"{symptom}. " + "; ".join([a.get("answer", "") for a in answers])
        } if enough else None,
        "phase": "recommended" if enough else "diagnosing",
    }

def route_from_diagnostic(state: VehicleAgentState) -> str:
    if state.get("phase") == "recommended":
        return "recommendation_agent"
    return END

def sensor_node(state: VehicleAgentState) -> Dict[str, Any]:
    sensor_data = state.get("sensor_data") or {}

    tool_result = predict_engine_failure.invoke({"sensor_data": sensor_data})

    prob = tool_result.get("failureProbability")
    risk = tool_result.get("riskLevel", "UNKNOWN")
    summary = (
        f"ML analysis complete. Risk: {risk}, Failure probability: {prob:.1%}"
        if isinstance(prob, float) else "ML analysis complete."
    )

    return {
        "messages": [AIMessage(content=summary)],
        "failure_probability": prob,
        "risk_level": risk,
        "phase": "analyzed",
        "next_agent": "supervisor",
    }


def recommendation_node(state: VehicleAgentState) -> Dict[str, Any]:
    issue_context = state.get("issue_context") or {
        "symptom": state.get("symptom", "unknown"),
        "answers": state.get("diagnostic_answers", []),
        "summary": state.get("symptom", "unknown"),
    }
    risk_level = state.get("risk_level") or "MEDIUM"

    tool_result = generate_service_recommendation.invoke({
        "issue_context": issue_context,
        "risk_level": risk_level,
    })

    service = tool_result.get("recommended_service", "Diagnostic inspection")
    urgency = tool_result.get("urgency", "MEDIUM")
    cost = tool_result.get("estimated_cost", "Contact service center")
    reply = f"Recommendation: {service} ({urgency} urgency, est. {cost}). Would you like me to book an appointment?"

    return {
        "messages": [AIMessage(content=reply)],
        "recommendation": tool_result,
        "phase": "awaiting_booking",
        "next_agent": "supervisor",
    }


def scheduling_node(state: VehicleAgentState) -> Dict[str, Any]:
    urgency = (state.get("recommendation") or {}).get("urgency", "MEDIUM")
    last_msg = state["messages"][-1].content if state["messages"] else ""

    tool_result = find_appointment_slots.invoke({
        "urgency": urgency,
        "user_preference": last_msg,
    })

    slot = tool_result.get("selected_slot", {})
    reply = f"I found a slot on {slot.get('date', 'TBD')} at {slot.get('time', '10:00')}. Reply 'confirm' to book it."

    return {
        "messages": [AIMessage(content=reply)],
        "scheduling": tool_result,
        "phase": "scheduling",
        "next_agent": "supervisor",
    }


# ── Routing ───────────────────────────────────────────────────────────────────

def route_from_supervisor(state: VehicleAgentState) -> str:
    mapping = {
        "diagnostic": "diagnostic_agent",
        "sensor_ml": "sensor_agent",
        "recommendation": "recommendation_agent",
        "scheduling": "scheduling_agent",
        "end": END,
    }
    return mapping.get(state.get("next_agent", "end"), END)


# ── Build graph ───────────────────────────────────────────────────────────────

def build_vehicle_graph():
    graph = StateGraph(VehicleAgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("diagnostic_agent", diagnostic_node)
    graph.add_node("sensor_agent", sensor_node)
    graph.add_node("recommendation_agent", recommendation_node)
    graph.add_node("scheduling_agent", scheduling_node)

    graph.add_edge(START, "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "diagnostic_agent": "diagnostic_agent",
            "sensor_agent": "sensor_agent",
            "recommendation_agent": "recommendation_agent",
            "scheduling_agent": "scheduling_agent",
            END: END,
        },
    )

    graph.add_conditional_edges(
    "diagnostic_agent",
    route_from_diagnostic,
    {"recommendation_agent": "recommendation_agent", END: END},
    )
    graph.add_edge("sensor_agent", "recommendation_agent")
    graph.add_edge("recommendation_agent", END)
    graph.add_edge("scheduling_agent", END)


    return graph.compile()


vehicle_graph = build_vehicle_graph()
