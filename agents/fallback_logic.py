def fallback_schedule_decision(vehicle_state: dict) -> dict:
    risk = vehicle_state.get("risk_level") or "UNKNOWN"
    prob = vehicle_state.get("failure_probability")

    prob_pct = int(prob * 100) if prob is not None else None

    if risk == "HIGH" or (prob is not None and prob > 0.7):
        reason = (
            f"Engine failure probability is {prob_pct}% — immediate service required to prevent breakdown."
            if prob_pct is not None
            else "Vehicle is showing high-risk indicators. Immediate service is strongly recommended."
        )
        return {"recommended_urgency": "HIGH", "reason": reason, "confidence": 0.88}

    if risk == "MEDIUM" or (prob is not None and prob > 0.4):
        reason = (
            f"Engine failure probability is {prob_pct}% — schedule service within the week to prevent escalation."
            if prob_pct is not None
            else "Moderate wear patterns detected. Scheduling service soon is advised."
        )
        return {"recommended_urgency": "MEDIUM", "reason": reason, "confidence": 0.75}

    reason = (
        f"Engine failure probability is {prob_pct}% — vehicle is in good condition. Routine maintenance recommended."
        if prob_pct is not None
        else "Vehicle systems are stable. No immediate concerns detected. Schedule a routine checkup."
    )
    return {"recommended_urgency": "LOW", "reason": reason, "confidence": 0.90}
