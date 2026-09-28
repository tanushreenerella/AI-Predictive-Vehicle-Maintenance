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
You decide what to do with your tools:
- Symptom described: ask ONE short follow-up question at a time (at most 2 in total), based on what they already said. Never repeat a question. Then call recommend_service.
- Asked about health/status: call get_vehicle_health and explain it. If values are null, the vehicle is not analyzed yet; suggest Run AI Analysis.
- Wants to book: if there is no recommendation yet, call recommend_service first (a general inspection is fine), then propose_appointment_slot.
- After offering a slot, wait for the user's reply. Call book_appointment(user_confirmed=true) only when the user clearly agrees to the slot you offered. Understand casual replies ("okay", "fine", "haan kar do") from context. If unclear, ask.
- If they want another time, call propose_appointment_slot again with their preference.
Never say something is booked unless book_appointment succeeded.
Current context: recommendation={rec}; proposed_slot={slot}"""


def make_tools(ctx: Dict[str, Any], vehicle_info: Dict[str, Any], book_fn):
    @tool
    def get_vehicle_health() -> dict:
        """Get the stored AI health analysis of the user's vehicle (risk level, failure probability, component, last analyzed)."""
        return json.loads(json.dumps(vehicle_info, default=str))

    @tool
    def recommend_service(symptom_summary: str, urgency_hint: str = "MEDIUM") -> dict:
        """Create a service recommendation from what the user described. urgency_hint is HIGH, MEDIUM or LOW."""
        u = urgency_hint.upper()
        rec = generate_service_recommendation.invoke({
            "issue_context": {"summary": symptom_summary},
            "risk_level": u if u in {"HIGH", "MEDIUM", "LOW"} else "MEDIUM",
        })
        ctx["recommendation"] = rec
        return rec

    @tool
    def propose_appointment_slot(time_preference: str = "") -> dict:
        """Find an appointment slot for the current recommendation. Only proposes, does NOT book."""
        rec = ctx.get("recommendation") or {}
        urgency = rec.get("urgency", "MEDIUM")
        slots = find_appointment_slots.invoke({"urgency": urgency, "user_preference": time_preference})
        slots["service_type"] = rec.get("recommended_service", "Full diagnostic inspection")
        slots["recommended_urgency"] = urgency
        ctx["scheduling"] = slots
        ctx["proposed_this_turn"] = True
        return slots

    @tool
    def book_appointment(user_confirmed: bool) -> dict:
        """Book the slot that was last proposed. user_confirmed=true ONLY if the user's latest message clearly agrees to that slot."""
        if ctx.get("proposed_this_turn"):
            return {"error": "You just proposed this slot. Show it to the user and wait for their reply before booking."}
        if not (ctx.get("scheduling") or {}).get("selected_slot"):
            return {"error": "No slot proposed yet. Call propose_appointment_slot first."}
        if not user_confirmed:
            return {"error": "User has not confirmed. Ask them to confirm the slot."}
        appt = book_fn(ctx.get("recommendation") or {}, ctx["scheduling"])
        ctx["appointment"] = appt
        ctx["scheduling"] = None  # prevents double booking
        return appt

    return [get_vehicle_health, recommend_service, propose_appointment_slot, book_appointment]


def run_turn(state: dict, message: str, vehicle_label: str, vehicle_info: dict, book_fn) -> dict:
    ctx = {
        "recommendation": state.get("recommendation"),
        "scheduling": state.get("scheduling"),
        "appointment": None,
        "proposed_this_turn": False,
    }
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

    phase = ("confirmed" if ctx["appointment"] else "scheduling" if ctx["scheduling"]
             else "recommended" if ctx["recommendation"] else "diagnosing")
    new_state = {
        **state,
        "messages": (state.get("messages", []) + [{"type": "human", "content": message},
                                                  {"type": "ai", "content": reply}])[-30:],
        "recommendation": None if ctx["appointment"] else ctx["recommendation"],
        "scheduling": ctx["scheduling"],
        "phase": phase,
        "vehicle_label": vehicle_label,
    }
    return {
        "reply": reply, "step": phase, "phase": phase, "state": new_state,
        "recommendation": ctx["recommendation"], "scheduling": ctx["scheduling"],
        "appointment": ctx["appointment"], "tool_calls": ["supervisor"] + tools_used,
    }