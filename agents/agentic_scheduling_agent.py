import json
import re
from agents.llm import call_llm
from agents.fallback_logic import fallback_schedule_decision


def agentic_scheduling_agent(vehicle_state: dict) -> dict:
    risk = vehicle_state.get("risk_level") or "UNKNOWN"
    prob = vehicle_state.get("failure_probability")
    last = vehicle_state.get("last_analyzed")

    prob_str = f"{int(prob * 100)}%" if prob is not None else "not yet analyzed"

    prompt = f"""You are a vehicle maintenance scheduling AI agent.

Vehicle health data:
- Risk level: {risk}
- Engine failure probability: {prob_str}
- Last ML analysis: {last}

Based on this data, recommend when the vehicle should be serviced.

Respond ONLY with valid JSON (no extra text, no markdown):
{{
  "recommended_urgency": "HIGH",
  "reason": "short explanation referencing the actual data",
  "confidence": 0.85
}}

Urgency rules:
- HIGH if failure probability > 70% or risk level is HIGH
- MEDIUM if failure probability 40-70% or risk level is MEDIUM
- LOW if failure probability < 40% or risk level is LOW / not analyzed"""

    try:
        raw = call_llm(prompt)

        # Strip markdown code fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip()

        # Extract first JSON object
        match = re.search(r"\{.*?\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())

        return json.loads(raw)

    except Exception as e:
        print(f"⚠️ Scheduling agent LLM failed: {e}")
        return fallback_schedule_decision(vehicle_state)
