from __future__ import annotations
import json
import re
from datetime import date, timedelta
from typing import Any, Dict, List

from langchain_core.tools import tool

from agents.llm import call_llm
from agents.failure_prediction.predict import predict_failure


MAX_DIAGNOSTIC_QUESTIONS = 3

@tool
def get_diagnostic_question(symptom: str, answers_so_far: List[Dict]) -> Dict:
    """Generate the next diagnostic question based on symptom and answers collected so far."""
    # Hard limit — never ask more than MAX_DIAGNOSTIC_QUESTIONS
    if len(answers_so_far) >= MAX_DIAGNOSTIC_QUESTIONS:
        return {"question": "", "enough_context": True}

    n = len(answers_so_far)
    prompt = f"""You are a vehicle diagnostic expert. Ask ONE short follow-up question.
Symptom: {symptom}
Answers so far ({n} of {MAX_DIAGNOSTIC_QUESTIONS}): {json.dumps(answers_so_far)}

Return ONLY valid JSON: {{"question": "your question here", "enough_context": false}}"""

    try:
        raw = call_llm(prompt)
        cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        return json.loads(match.group() if match else cleaned)
    except Exception:
        return {
            "question": "When does this problem happen most often?",
            "enough_context": False
        }


@tool
def predict_engine_failure(sensor_data: Dict[str, Any]) -> Dict:
    """Run the ML failure prediction model directly with sensor readings to get failure probability and risk level."""
    try:
        return predict_failure(sensor_data)
    except Exception as e:
        return {
            "error": str(e),
            "failureProbability": 0.5,
            "riskLevel": "UNKNOWN",
            "component": "Engine"
        }


@tool
def generate_service_recommendation(issue_context: Dict, risk_level: str) -> Dict:
    """Generate a service recommendation based on diagnostic findings and ML risk level."""
    prompt = f"""You are a senior automotive service advisor.
Issue context from diagnosis: {json.dumps(issue_context)}
ML risk level from sensors: {risk_level}

Return ONLY valid JSON:
{{
  "likely_issue": "probable root cause",
  "recommended_service": "specific service name",
  "urgency": "HIGH or MEDIUM or LOW",
  "estimated_cost": "$X-$Y",
  "timeframe": "when to service",
  "reasoning": "one sentence explanation"
}}"""

    try:
        raw = call_llm(prompt)
        cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        return json.loads(match.group() if match else cleaned)
    except Exception:
        return {
            "likely_issue": "Requires inspection",
            "recommended_service": "Full diagnostic inspection",
            "urgency": risk_level or "MEDIUM",
            "estimated_cost": "$80-$200",
            "timeframe": "Within 3-5 days",
            "reasoning": "Based on reported symptoms and sensor readings."
        }


@tool
def find_appointment_slots(urgency: str, user_preference: str) -> Dict:
    """Find available appointment slots based on urgency level and user time preferences."""
    days_map = {"HIGH": 1, "MEDIUM": 4, "LOW": 10}
    days = days_map.get(urgency.upper(), 4)

    pref = user_preference.lower()
    if "today" in pref:
        days = 0
    elif "tomorrow" in pref:
        days = 1
    elif "next week" in pref:
        days = 7

    appt_time = "10:00"
    if "afternoon" in pref:
        appt_time = "14:00"
    elif "morning" in pref:
        appt_time = "09:00"
    elif "evening" in pref:
        appt_time = "17:00"

    slot_date = date.today() + timedelta(days=days)
    backup_date = date.today() + timedelta(days=days + 1)

    return {
        "suggested_slots": [
            {"date": slot_date.isoformat(), "time": appt_time, "label": "Primary slot"},
            {"date": backup_date.isoformat(), "time": appt_time, "label": "Backup slot"},
        ],
        "selected_slot": {"date": slot_date.isoformat(), "time": appt_time},
        "urgency": urgency.upper(),
    }
