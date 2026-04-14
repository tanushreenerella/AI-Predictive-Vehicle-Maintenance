def fallback_schedule_decision(vehicle_state: dict):
    risk = vehicle_state.get("risk_level", "LOW")

    if risk == "HIGH":
        return {
            "recommended_urgency": "HIGH",
            "reason": "High failure risk detected (fallback logic)",
            "confidence": 0.85,
        }

    if risk == "MEDIUM":
        return {
            "recommended_urgency": "MEDIUM",
            "reason": "Moderate wear detected (fallback logic)",
            "confidence": 0.65,
        }

    return {
        "recommended_urgency": "LOW",
        "reason": "System stable (fallback logic)",
        "confidence": 0.9,
    }
