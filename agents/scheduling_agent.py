from datetime import datetime, timedelta
import random

def scheduling_agent(vehicle_state: dict, user_preferences: dict = None):
    risk = vehicle_state.get("risk_level") or "LOW"

    raw_prob = vehicle_state.get("failure_probability")
    try:
        prob = float(raw_prob)
    except (TypeError, ValueError):
        prob = 0.0

    today = datetime.utcnow().date()

    if prob >= 0.75:
        urgency = "HIGH"
        window = (0, 2)
        confidence = min(0.95, prob + 0.1)
        reasoning = (
            f"High predicted failure probability ({prob:.0%}). "
            "Immediate service strongly recommended."
        )

    elif prob >= 0.45:
        urgency = "MEDIUM"
        window = (
            int(3 + (1 - prob) * 2),
            int(7 + (1 - prob) * 3),
        )
        confidence = min(0.9, prob + 0.15)
        reasoning = (
            f"Moderate failure probability ({prob:.0%}). "
            "Scheduling within this window reduces escalation risk."
        )

    else:
        urgency = "LOW"
        window = (
            int(10 + (1 - prob) * 5),
            int(25 + (1 - prob) * 10),
        )
        confidence = max(0.6, prob + 0.25)
        reasoning = (
            f"Low failure probability ({prob:.0%}). "
            "Routine maintenance recommended."
        )

    jitter = random.randint(0, 2)
    suggested_date = today + timedelta(days=window[0] + jitter)

    return {
        "urgency": urgency,
        "recommended_window_days": list(window),
        "suggested_date": suggested_date.isoformat(),
        "reasoning": reasoning,
        "confidence": round(confidence, 2),
        "agent": "SchedulingAgent_v2_probabilistic"
    }
