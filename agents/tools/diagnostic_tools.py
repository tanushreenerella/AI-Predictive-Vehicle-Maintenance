import json
import re
from typing import Any, Dict, List, Optional

from agents.llm import call_llm


SYMPTOM_KEYWORDS = {
    "noise": {"noise", "rattle", "rattling", "knock", "knocking", "grind", "grinding", "squeal", "clunk"},
    "overheating": {"overheat", "overheating", "hot", "temperature", "coolant", "radiator"},
    "brakes": {"brake", "brakes", "braking", "pedal", "rotor", "pads"},
    "starting": {"start", "starting", "crank", "battery", "ignition", "alternator"},
    "leak": {"leak", "fluid", "oil", "coolant dripping", "puddle"},
    "vibration": {"vibration", "vibrating", "shake", "shaking", "wobble"},
}


def diagnostic_questions_tool(symptom: str, answers: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Return the next 1-2 diagnostic questions and a structured context summary.

    The tool is intentionally turn-based: callers pass the symptom and answers
    collected so far, then display only the returned question(s) in chat.
    """
    answers = answers or []
    issue_context = _build_issue_context(symptom, answers)
    if len(answers) >= 2:
        return {
            "questions": [],
            "enough_context": True,
            "issue_context": issue_context,
        }

    try:
        prompt = f"""You are a vehicle diagnostic question generator.
Ask the next most useful follow-up question for the reported issue.

Reported symptom: {symptom}
Answers already collected:
{json.dumps(answers, indent=2)}

Return ONLY JSON:
{{
  "questions": ["one concise question"],
  "enough_context": false,
  "issue_context": {{
    "symptom": "short symptom label",
    "component": "likely affected system",
    "severity_signals": ["short signal"]
  }}
}}

Rules:
- Ask exactly one question unless the two questions are tightly related.
- Do not repeat questions already answered.
- Prefer questions about when it happens, warning lights, smells, leaks, heat, and driveability.
"""
        data = _extract_json(call_llm(prompt))
        questions = data.get("questions") if isinstance(data, dict) else None
        if questions:
            return {
                "questions": [str(q) for q in questions[:2]],
                "enough_context": False,
                "issue_context": data.get("issue_context") or issue_context,
            }
    except Exception as exc:
        print(f"[diagnostic_questions_tool] LLM fallback: {exc}")

    return {
        "questions": [_fallback_question(symptom, answers)],
        "enough_context": False,
        "issue_context": issue_context,
    }


def service_recommendation_tool(
    issue_context: Dict[str, Any],
    vehicle_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Produce a structured recommendation from collected diagnostic context.
    """
    vehicle_state = vehicle_state or {}
    try:
        prompt = f"""You are a senior automotive service advisor.
Create a concise service recommendation from the diagnostic context.

Issue context:
{json.dumps(issue_context, indent=2)}

Vehicle health state:
{json.dumps(vehicle_state, default=str, indent=2)}

Return ONLY JSON:
{{
  "likely_issue": "probable root cause",
  "recommended_service": "service name",
  "urgency": "HIGH | MEDIUM | LOW",
  "estimated_cost": "$80-$150 or local equivalent/range",
  "timeframe": "when to service",
  "reasoning": "one sentence"
}}

Use HIGH for safety-critical brakes, overheating, oil pressure warnings, smoke, or severe drivability loss.
"""
        data = _extract_json(call_llm(prompt))
        if isinstance(data, dict) and data.get("recommended_service"):
            return _normalise_recommendation(data)
    except Exception as exc:
        print(f"[service_recommendation_tool] LLM fallback: {exc}")

    return _fallback_recommendation(issue_context, vehicle_state)


def _build_issue_context(symptom: str, answers: List[Dict[str, str]]) -> Dict[str, Any]:
    text = " ".join([symptom] + [a.get("answer", "") for a in answers]).lower()
    categories = [name for name, words in SYMPTOM_KEYWORDS.items() if any(word in text for word in words)]
    component = "Engine"
    if "brakes" in categories:
        component = "Brake system"
    elif "starting" in categories:
        component = "Battery/starting system"
    elif "vibration" in categories:
        component = "Wheels/suspension"
    elif "leak" in categories:
        component = "Fluid system"

    red_flags = []
    for flag in ["warning light", "smoke", "burning", "overheat", "oil light", "brake", "grinding", "loss of power"]:
        if flag in text and f"no {flag}" not in text and f"no {flag}s" not in text:
            red_flags.append(flag)

    return {
        "symptom": symptom,
        "component": component,
        "category": categories[0] if categories else "general",
        "answers": answers,
        "severity_signals": red_flags,
    }


def _fallback_question(symptom: str, answers: List[Dict[str, str]]) -> str:
    text = symptom.lower()
    asked = " ".join(a.get("question", "") for a in answers).lower()
    if not answers:
        if any(w in text for w in ["noise", "rattle", "knock", "grind", "squeal"]):
            return "Does the noise happen while accelerating, while idling, when braking, or only at startup?"
        if any(w in text for w in ["overheat", "hot", "temperature", "coolant"]):
            return "Does the temperature rise while idling, while driving, or only after longer trips?"
        if "brake" in text:
            return "Do you feel the issue in the brake pedal, hear a sound, or notice the car pulling to one side?"
        if any(w in text for w in ["start", "battery", "crank"]):
            return "When you try to start it, do you hear clicking, slow cranking, or no sound at all?"
        return "When does the problem happen most often: startup, idling, accelerating, braking, or after a long drive?"
    if "warning" not in asked:
        return "Have you noticed any warning lights, unusual smells, fluid leaks, or smoke?"
    return "Has the problem changed recently, and is the car still driving normally?"


def _fallback_recommendation(issue_context: Dict[str, Any], vehicle_state: Dict[str, Any]) -> Dict[str, Any]:
    answer_text = " ".join(a.get("answer", "") for a in issue_context.get("answers", []) if isinstance(a, dict))
    text = " ".join([
        str(issue_context.get("symptom") or ""),
        str(issue_context.get("category") or ""),
        str(issue_context.get("component") or ""),
        answer_text,
        " ".join(issue_context.get("severity_signals") or []),
    ]).lower()
    risk = str(vehicle_state.get("risk_level") or "").upper()
    urgency = "HIGH" if risk == "HIGH" else "MEDIUM"
    likely_issue = "Mechanical issue requiring inspection"
    service = "Full vehicle diagnostic inspection"
    cost = "$80-$180"
    timeframe = "Within 3-5 days"

    if any(w in text for w in ["brake", "grinding"]):
        likely_issue = "Possible brake pad, rotor, or caliper wear"
        service = "Brake system inspection and repair"
        urgency = "HIGH"
        cost = "$120-$450"
        timeframe = "As soon as possible"
    elif any(w in text for w in ["overheat", "coolant", "temperature", "smoke"]):
        likely_issue = "Possible cooling system fault"
        service = "Cooling system pressure test and inspection"
        urgency = "HIGH"
        cost = "$100-$350"
        timeframe = "Within 24 hours"
    elif any(w in text for w in ["rattle", "noise", "knock"]):
        likely_issue = "Possible loose exhaust/heat shield, mount wear, or engine accessory issue"
        service = "Noise diagnosis and underbody/engine bay inspection"
        urgency = "MEDIUM" if urgency != "HIGH" else "HIGH"
        cost = "$80-$250"
        timeframe = "Within 3-7 days"
    elif any(w in text for w in ["battery", "start", "crank"]):
        likely_issue = "Possible weak battery, alternator, or starter issue"
        service = "Battery, alternator, and starter test"
        urgency = "MEDIUM"
        cost = "$40-$220"
        timeframe = "Within 2-5 days"

    return {
        "likely_issue": likely_issue,
        "recommended_service": service,
        "urgency": urgency,
        "estimated_cost": cost,
        "timeframe": timeframe,
        "reasoning": "Based on the symptom pattern and answers collected in chat.",
    }


def _normalise_recommendation(data: Dict[str, Any]) -> Dict[str, Any]:
    urgency = str(data.get("urgency", "MEDIUM")).upper()
    if urgency not in {"HIGH", "MEDIUM", "LOW"}:
        urgency = "MEDIUM"
    return {
        "likely_issue": str(data.get("likely_issue") or "Vehicle issue requiring inspection"),
        "recommended_service": str(data.get("recommended_service") or "Diagnostic inspection"),
        "urgency": urgency,
        "estimated_cost": str(data.get("estimated_cost") or "Estimate after inspection"),
        "timeframe": str(data.get("timeframe") or "Soon"),
        "reasoning": str(data.get("reasoning") or ""),
    }


def _extract_json(raw: str) -> Dict[str, Any]:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    return json.loads(match.group() if match else cleaned)
