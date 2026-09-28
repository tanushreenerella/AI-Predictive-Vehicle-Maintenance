from __future__ import annotations
import json
import logging
import time
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

log = logging.getLogger("chat_agent")
MODEL = "openai/gpt-oss-120b"

SYSTEM = """You are the assistant of a predictive vehicle-maintenance app. Vehicle: {vehicle}.
Reply ONLY in {language}; never detect or switch language. Be concise.

Tools: get_vehicle_health, log_diagnostic_question, recommend_service,
propose_appointment_slot, book_appointment. YOU decide which to use.
- Symptom described: ask ONE short relevant diagnostic question per turn
  (call log_diagnostic_question each time, max 2, never repeat). Then call
  recommend_service and ask if they want an appointment slot.
- Health / maintenance-due question: call get_vehicle_health and answer from it.
  If values are null, the vehicle is not analyzed yet; suggest Run AI Analysis.
- Booking is ONE step per turn: recommend -> user agrees -> propose slot ->
  user confirms -> book. If a tool returns an error, do not retry; tell the user the next step.
- If proposed_slot is set and the user's message agrees to it (yes, ok, haan,
  book it), call book_appointment(user_confirmed=true). If unclear, ask again.
- If recommendation is set and no proposed_slot, and the user agrees to a slot,
  call propose_appointment_slot. Never call recommend_service again unless the
  user describes a NEW problem. After proposing, state the date/time and ask to confirm.
- If there is no recommendation, a bare yes/ok/haan just answers your last question.
- Never say something is booked unless book_appointment succeeded.
State: recommendation={rec}; proposed_slot={slot}; diagnostic_questions_asked={dq}"""


def _get_vehicle_health(vehicle_info):
    return json.loads(json.dumps(vehicle_info, default=str))


def make_tools(ctx, vehicle_info, book_fn):
    def busy():
        if ctx["executed"]:
            return {"error": f"'{ctx['executed']}' already ran this turn. Reply to the user now."}

    @tool
    def get_vehicle_health() -> dict:
        """Stored AI health analysis: risk level, failure probability, component, last analyzed."""
        ctx["called"].append("get_vehicle_health")
        return _get_vehicle_health(vehicle_info)

    @tool
    def log_diagnostic_question(question: str) -> dict:
        """Call each time you ask the user a diagnostic question."""
        if ctx["dq"] >= 2:
            return {"error": "Enough questions asked. Call recommend_service now."}
        ctx["dq"] += 1
        ctx["called"].append("log_diagnostic_question")
        return {"asked": ctx["dq"], "remaining": 2 - ctx["dq"]}

    @tool
    def recommend_service(symptom_summary: str, urgency_hint: str = "MEDIUM") -> dict:
        """Create a service recommendation. Does not schedule anything."""
        if e := busy():
            return e
        u = urgency_hint.upper()
        rec = generate_service_recommendation.invoke({
            "issue_context": {"summary": symptom_summary},
            "risk_level": u if u in {"HIGH", "MEDIUM", "LOW"} else "MEDIUM"})
        ctx.update(recommendation=rec, scheduling=None, executed="recommend",
                   show_rec=True, dq=0)
        ctx["called"].append("recommend_service")
        return rec

    @tool
    def propose_appointment_slot(time_preference: str = "") -> dict:
        """Find a slot for the current recommendation. Proposes only, does NOT book."""
        if e := busy():
            return e
        rec = ctx["rec_prior"]  # must have been shown in an EARLIER turn
        if not rec:
            return {"error": "No recommendation from an earlier turn. Call recommend_service, then ask the user."}
        urgency = rec.get("urgency", "MEDIUM")
        slots = find_appointment_slots.invoke({"urgency": urgency, "user_preference": time_preference})
        slots["service_type"] = rec.get("recommended_service", "Full diagnostic inspection")
        slots["recommended_urgency"] = urgency
        ctx.update(scheduling=slots, executed="propose", show_slot=True)
        ctx["called"].append("propose_appointment_slot")
        return slots

    @tool
    def book_appointment(user_confirmed: bool) -> dict:
        """Book the previously proposed slot. user_confirmed=true only if the user's
        latest message clearly agrees to that specific slot."""
        if e := busy():
            return e
        prior = ctx["slot_prior"] or {}  # must have been proposed in an EARLIER turn
        if not prior.get("selected_slot"):
            return {"error": "No slot was proposed in an earlier turn. Propose one first."}
        if not user_confirmed:
            return {"error": "Not confirmed. Ask the user to confirm the slot."}
        appt = book_fn(ctx["recommendation"] or {}, prior)
        ctx.update(appointment=appt, recommendation=None, scheduling=None, executed="book", dq=0)
        ctx["called"].append("book_appointment")
        return appt

    return [get_vehicle_health, log_diagnostic_question, recommend_service,
            propose_appointment_slot, book_appointment]


def run_turn(state, message, vehicle_label, vehicle_info, book_fn, language="English"):
    ctx = {
        "recommendation": state.get("recommendation"),
        "rec_prior": state.get("recommendation"),
        "slot_prior": state.get("scheduling"),
        "scheduling": state.get("scheduling"),
        "appointment": None, "executed": None, "called": [],
        "dq": int(state.get("dq") or 0),
        "show_rec": False, "show_slot": False,
    }
    slot = (ctx["slot_prior"] or {}).get("selected_slot")
    prompt = SYSTEM.format(
        vehicle=vehicle_label, language=language,
        rec=json.dumps(ctx["recommendation"], default=str) if ctx["recommendation"] else "none",
        slot=json.dumps(slot, default=str) if slot else "none",
        dq=ctx["dq"])
    agent = _build(ChatGroq(model=MODEL, temperature=0.2),
                   make_tools(ctx, vehicle_info, book_fn), prompt)

    history = [(HumanMessage if m.get("type") == "human" else AIMessage)(content=m.get("content", ""))
               for m in state.get("messages", [])[-20:] if isinstance(m, dict)]
    history.append(HumanMessage(content=message))

    log.info("route=llm model=%s lang=%s msg=%r state(rec=%s slot=%s dq=%s)",
             MODEL, language, message[:80], bool(ctx["recommendation"]), bool(slot), ctx["dq"])
    t0 = time.time()
    for attempt in range(2):
        try:
            result = agent.invoke({"messages": history})
            break
        except Exception:
            log.exception("LLM invoke failed (attempt %d)", attempt + 1)
            if attempt == 1:
                raise

    new_msgs = result["messages"][len(history):]
    requested = [tc["name"] for m in new_msgs if isinstance(m, AIMessage) for tc in (m.tool_calls or [])]
    log.info("LLM done ms=%d requested=%s executed=%s", (time.time() - t0) * 1000, requested, ctx["called"])

    reply = next((m.content for m in reversed(new_msgs)
                  if isinstance(m, AIMessage) and m.content and not m.tool_calls),
                 "Sorry, I couldn't process that. Please try again.")
    if isinstance(reply, list):
        reply = " ".join(b.get("text", "") for b in reply if isinstance(b, dict))

    if ctx["appointment"]:
        phase = "confirmed"
    elif ctx["scheduling"]:
        phase = "scheduling"
    elif ctx["recommendation"]:
        phase = "recommended"
    elif ctx["dq"]:
        phase = "diagnosing"
    else:
        phase = "general"

    new_state = {**state,
                 "messages": (state.get("messages", []) + [{"type": "human", "content": message},
                                                           {"type": "ai", "content": reply}])[-30:],
                 "recommendation": ctx["recommendation"], "scheduling": ctx["scheduling"],
                 "dq": ctx["dq"], "phase": phase, "language": language, "vehicle_label": vehicle_label}
    return {
        "reply": reply, "step": phase, "phase": phase, "state": new_state,
        "recommendation": ctx["recommendation"] if ctx["show_rec"] else None,
        "scheduling": ctx["scheduling"] if ctx["show_slot"] else None,
        "appointment": ctx["appointment"],
        "tool_calls": ctx["called"],
    }