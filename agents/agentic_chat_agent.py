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
                f"Confirm this booking enthusiastically."
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

    except Exception:
        return _smart_fallback(user_message, vehicle, appointment_data)


def _smart_fallback(message: str, vehicle, appointment_data) -> str:
    if appointment_data:
        return (
            f"I've booked a service appointment for {appointment_data['vehicle']} "
            f"on {appointment_data['date']} at {appointment_data['time']}. "
            f"Urgency: {appointment_data['urgency']}. View it in your Appointments page."
        )

    msg = message.lower()
    vehicle_summary = ""
    if vehicle:
        prob = int((vehicle.ai_failure_probability or 0) * 100)
        risk = vehicle.ai_risk_level or "unknown"
        vehicle_summary = f" Your {vehicle.name} shows {risk} risk ({prob}% failure probability)."

    if any(w in msg for w in ["heat", "hot", "overheat", "temperature", "coolant"]):
        return (
            "Engine overheating is usually caused by low coolant, a faulty thermostat, or a failing water pump. "
            "Check coolant levels immediately and avoid long drives until inspected."
            + vehicle_summary
        )
    if any(w in msg for w in ["oil", "lubric", "leak"]):
        return (
            "Oil issues are often caused by leaks, low oil level, or degraded oil. "
            "Check your oil dipstick — if it's dark or below minimum, schedule an oil change soon."
            + vehicle_summary
        )
    if any(w in msg for w in ["brake", "braking", "stopping", "pedal"]):
        return (
            "Brake problems can be serious. Common causes: worn pads, low brake fluid, or warped rotors. "
            "Schedule a brake inspection immediately for safety."
            + vehicle_summary
        )
    if any(w in msg for w in ["vibrat", "shake", "shaking", "wobble"]):
        return (
            "Vibration often indicates wheel imbalance, worn tyres, or suspension issues. "
            "Have the wheel alignment and suspension checked soon."
            + vehicle_summary
        )
    if any(w in msg for w in ["noise", "sound", "clunk", "squeak", "rattle"]):
        return (
            "Unusual sounds can indicate worn belts, loose components, or exhaust issues. "
            "A diagnostic check will pinpoint the source. Avoid ignoring knocking from the engine."
            + vehicle_summary
        )
    if any(w in msg for w in ["fuel", "gas", "petrol", "consumption", "mileage"]):
        return (
            "Poor fuel efficiency can result from a dirty air filter, low tyre pressure, or engine tuning issues. "
            "Regular servicing helps optimise fuel consumption."
            + vehicle_summary
        )
    if any(w in msg for w in ["battery", "start", "starting", "ignition"]):
        return (
            "Starting issues usually point to a weak battery, faulty alternator, or bad starter motor. "
            "Have the battery voltage tested — most garages do this for free."
            + vehicle_summary
        )
    if any(w in msg for w in ["tyre", "tire", "pressure", "flat", "puncture"]):
        return (
            "Check tyre pressure monthly — under-inflation increases fuel use and wear. "
            "For punctures, avoid driving on a flat tyre to prevent rim damage."
            + vehicle_summary
        )

    # Default: show vehicle context if available
    if vehicle and vehicle.ai_risk_level:
        prob = int((vehicle.ai_failure_probability or 0) * 100)
        return (
            f"Your {vehicle.name} currently shows {vehicle.ai_risk_level} risk with "
            f"{prob}% engine failure probability"
            + (f" in the {vehicle.ai_component} system" if vehicle.ai_component else "")
            + ". Say 'book appointment' to schedule a service, or ask me about any symptoms."
        )

    return (
        "I can help with vehicle diagnostics, maintenance advice, and booking services. "
        "Try describing a symptom (e.g. 'engine overheating') or say 'book an appointment'."
    )
