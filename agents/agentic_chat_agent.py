from agents.llm import call_llm


def agentic_chat_agent(user_message, vehicle=None, vehicles_context="", appointment_data=None):
    try:
        appt_info = ""
        if appointment_data:
            appt_info = (
                f"\n\nACTION TAKEN: Appointment auto-booked:\n"
                f"- Vehicle: {appointment_data['vehicle']}\n"
                f"- Date: {appointment_data['date']} at {appointment_data['time']}\n"
                f"- Service: {appointment_data['service_type']}, Urgency: {appointment_data['urgency']}\n"
                f"Confirm this enthusiastically."
            )

        vehicle_info = "No vehicle context."
        if vehicle:
            prob = int((vehicle.ai_failure_probability or 0) * 100)
            vehicle_info = (
                f"{vehicle.name} ({getattr(vehicle, 'model', '')}): "
                f"risk={vehicle.ai_risk_level or 'not analysed'}, "
                f"engine failure probability={prob}%"
                + (f", affected component: {vehicle.ai_component}" if vehicle.ai_component else "")
            )

        prompt = f"""You are a knowledgeable AI vehicle maintenance assistant. Be helpful, clear, and concise.

User message: {user_message}

Selected vehicle: {vehicle_info}

All user vehicles:
{vehicles_context if vehicles_context else "No vehicles registered."}
{appt_info}

Guidelines:
- Answer the user's specific question directly using the vehicle data above.
- If an appointment was booked, confirm it with the date/time/vehicle.
- For mechanical symptoms (heating, noise, vibration, oil, brakes), give practical advice.
- If risk is HIGH, strongly recommend immediate service.
- Keep response under 150 words. Be friendly and direct.
"""
        return call_llm(prompt)

    except Exception as e:
        print(f"LLM failed in chat agent: {e}")
        return _smart_fallback(user_message, vehicle, appointment_data)


# ─────────────────────────────────────────────
# Smart rule-based fallback — handles any query
# ─────────────────────────────────────────────

def _vctx(vehicle) -> tuple[str, str, int, str]:
    """Returns (name, risk, prob_pct, component)."""
    if not vehicle:
        return ("your vehicle", "unknown", 0, "engine")
    name = vehicle.name
    risk = vehicle.ai_risk_level or "unknown"
    prob = int((vehicle.ai_failure_probability or 0) * 100)
    comp = vehicle.ai_component or "engine"
    return name, risk, prob, comp


def _smart_fallback(message: str, vehicle, appointment_data) -> str:
    # ── Appointment confirmation ──────────────────────────────────
    if appointment_data:
        return (
            f"Done! I've booked a {appointment_data['service_type']} appointment for "
            f"{appointment_data['vehicle']} on {appointment_data['date']} at {appointment_data['time']} "
            f"(urgency: {appointment_data['urgency']}). You can view or cancel it in the Appointments page."
        )

    msg = message.lower()
    name, risk, prob, comp = _vctx(vehicle)
    has_analysis = vehicle and vehicle.ai_risk_level

    # ── Why / cause / reason / explain ───────────────────────────
    if any(w in msg for w in ["why", "reason", "cause", "explain", "how come", "what is", "what's"]):
        if has_analysis:
            if risk == "HIGH":
                return (
                    f"The ML model flagged {name} as HIGH risk ({prob}% failure probability) "
                    f"because sensor readings in the {comp} system deviated significantly from safe thresholds — "
                    f"likely abnormal RPM patterns, low oil/coolant pressure, or elevated temperatures. "
                    f"Immediate servicing is recommended."
                )
            elif risk == "MEDIUM":
                return (
                    f"The ML model detected moderate wear in {name}'s {comp} system ({prob}% failure probability). "
                    f"This typically means gradual sensor deviations — possibly delayed maintenance, minor oil/coolant "
                    f"degradation, or early-stage component wear. Service within the week is advised."
                )
            else:
                return (
                    f"{name} shows LOW risk ({prob}% failure probability). "
                    f"Sensor readings are within normal operating ranges. No immediate concern — just keep up with regular maintenance."
                )
        return (
            "Engine failure risk is calculated from sensor readings: RPM patterns, oil pressure, "
            "coolant temperature, and fuel pressure. Run AI Analysis on your vehicle to get a personalised score."
        )

    # ── What to do / recommendations / advice ────────────────────
    if any(w in msg for w in ["what should", "what do", "what to", "should i", "advice",
                               "recommend", "suggestion", "action", "help", "next step", "what now"]):
        if has_analysis:
            if risk == "HIGH":
                return (
                    f"For {name} at {prob}% failure probability:\n"
                    f"1. Book a service appointment immediately (within 48 hours)\n"
                    f"2. Avoid highway or long-distance driving\n"
                    f"3. Check engine oil and coolant levels before each drive\n"
                    f"4. Monitor the temperature gauge closely\n"
                    f"5. View the RCA Report for a detailed root cause breakdown."
                )
            elif risk == "MEDIUM":
                return (
                    f"For {name} at {prob}% failure probability:\n"
                    f"1. Schedule a service within 5–7 days\n"
                    f"2. Get an oil and filter change if overdue\n"
                    f"3. Check tyre pressure and top up fluids\n"
                    f"4. Watch for new symptoms (noise, vibration, heating)\n"
                    f"5. Use the RCA Report page for a full analysis."
                )
            else:
                return (
                    f"{name} is in good health ({prob}% failure probability). "
                    f"Follow the manufacturer's maintenance schedule: oil change every 5,000–7,500 km, "
                    f"tyre rotation every 10,000 km, and run AI Analysis periodically."
                )
        return "Run AI Analysis on your vehicle first, then I can give personalised recommendations."

    # ── How serious / urgent / worried ───────────────────────────
    if any(w in msg for w in ["serious", "bad", "worried", "dangerous", "urgent", "critical",
                               "how bad", "how serious", "how urgent"]):
        if has_analysis:
            if risk == "HIGH":
                return (
                    f"This is serious. {name} has a {prob}% engine failure probability — "
                    f"that means a breakdown is quite likely without service. "
                    f"Please book an appointment today and avoid long drives."
                )
            elif risk == "MEDIUM":
                return (
                    f"Moderate concern. {name} has a {prob}% failure probability — "
                    f"not an emergency, but delaying service for more than a week increases the risk. "
                    f"Book a service soon to prevent escalation."
                )
            else:
                return f"No immediate concern. {name} shows only {prob}% failure probability — the vehicle is in good health."
        return "Run AI Analysis first so I can assess how serious the situation is."

    # ── When / how soon / timeline ────────────────────────────────
    if any(w in msg for w in ["when", "how soon", "deadline", "time", "days", "weeks"]):
        if has_analysis:
            if risk == "HIGH":
                return f"For {name} (HIGH risk, {prob}%): get it serviced within 48 hours. The failure window is very short."
            elif risk == "MEDIUM":
                return f"For {name} (MEDIUM risk, {prob}%): aim to service within 5–7 days to prevent the risk from escalating."
            else:
                return f"{name} is LOW risk ({prob}%). Follow your regular maintenance schedule — likely no urgency for several weeks."
        return "Run AI Analysis first to get a time estimate."

    # ── Specific component symptoms ───────────────────────────────
    if any(w in msg for w in ["heat", "hot", "overheat", "temperature", "coolant", "radiator"]):
        return (
            "Engine overheating is caused by low coolant, a failing thermostat, a blocked radiator, or a faulty water pump. "
            "Check coolant level immediately and avoid driving until inspected. "
            + (f" Your {name} is already at {prob}% failure risk — this makes it more urgent." if has_analysis and prob > 30 else "")
        )

    if any(w in msg for w in ["oil", "lubric", "oil pressure", "leak"]):
        return (
            "Oil issues are usually low oil level, leaks, degraded oil, or a failing oil pump. "
            "Check the dipstick — if it's below minimum or dark/thick, get an oil change. "
            "Low oil pressure is a serious warning: stop driving if the oil light comes on."
            + (f" {name}'s current risk is {risk} ({prob}%)." if has_analysis else "")
        )

    if any(w in msg for w in ["brake", "braking", "stopping", "pedal", "squeal"]):
        return (
            "Brake problems include worn pads, low brake fluid, warped rotors, or a stuck calliper. "
            "If the pedal feels soft or the car pulls to one side, stop driving and get it inspected immediately — brakes are safety-critical."
        )

    if any(w in msg for w in ["vibrat", "shake", "shaking", "wobble", "steering"]):
        return (
            "Vibration often means wheel imbalance, a bent rim, worn tyres, or a suspension issue. "
            "At highway speeds it could be a driveshaft problem. "
            "Have wheel alignment and balance checked — it's usually a quick fix."
        )

    if any(w in msg for w in ["noise", "sound", "clunk", "squeak", "rattle", "knock", "grinding"]):
        return (
            "Engine knocking usually means low oil or worn bearings — stop driving and check immediately. "
            "Squealing brakes = worn pads. Grinding gears = clutch or gearbox. "
            "Rattling from underneath could be a loose exhaust. Describe the noise more and I can narrow it down."
        )

    if any(w in msg for w in ["fuel", "gas", "petrol", "consumption", "mpg", "mileage efficiency"]):
        return (
            "Poor fuel efficiency is often caused by a dirty air filter, under-inflated tyres, a faulty oxygen sensor, "
            "or worn spark plugs. A simple service usually restores normal consumption."
        )

    if any(w in msg for w in ["battery", "start", "starting", "ignition", "crank", "won't start"]):
        return (
            "Starting problems point to a weak battery, faulty alternator, or bad starter motor. "
            "Most garages test battery voltage for free. If the battery is over 3–4 years old, consider replacing it proactively."
        )

    if any(w in msg for w in ["tyre", "tire", "pressure", "flat", "puncture", "tread"]):
        return (
            "Check tyre pressure monthly — under-inflation increases tyre wear and fuel consumption. "
            "For a puncture, avoid driving on a flat to protect the rim. "
            "Tread below 1.6mm is illegal in most regions."
        )

    if any(w in msg for w in ["report", "rca", "root cause", "analysis", "detail"]):
        return (
            "Head to the Reports page to generate a full Root Cause Analysis (RCA) for your vehicle. "
            "It includes root cause, contributing factors, severity rating, and step-by-step recommendations."
            + (f" {name}'s current risk is {risk} ({prob}%)." if has_analysis else "")
        )

    if any(w in msg for w in ["appointment", "book", "schedule", "service", "repair"]):
        if has_analysis and risk in ("HIGH", "MEDIUM"):
            return (
                f"To book a service for {name}, say 'book an appointment' and I'll automatically schedule one based on the {risk} risk level. "
                f"Or visit the Schedule page to pick your own date and time."
            )
        return "Head to the Schedule page to book a service, or say 'book an appointment' here and I'll handle it."

    # ── Context-aware default ─────────────────────────────────────
    if has_analysis:
        tips = {
            "HIGH": f"Immediate service is recommended — failure risk is very high at {prob}%.",
            "MEDIUM": f"Service within the week is advised — {prob}% failure probability detected.",
            "LOW": f"Vehicle is in good health at {prob}% failure probability. Keep up with routine maintenance.",
        }
        return (
            f"Regarding {name}: {tips.get(risk, f'{risk} risk, {prob}% failure probability.')} "
            f"You can ask me about specific symptoms, say 'what should I do?', "
            f"or say 'book appointment' to schedule a service."
        )

    return (
        "I can help with vehicle diagnostics, maintenance advice, and booking services. "
        "Try asking about a symptom (e.g. 'engine overheating'), ask 'what should I do?', "
        "or run AI Analysis first to get personalised insights."
    )
