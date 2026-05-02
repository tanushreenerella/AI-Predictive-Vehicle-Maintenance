from agents.llm import call_llm
from datetime import date


def agentic_chat_agent(user_message, vehicle=None, vehicles_context="", appointment_data=None):
    try:
        appt_info = ""
        if appointment_data:
            appt_info = (
                f"\n\nACTION TAKEN: An appointment has been automatically booked:\n"
                f"- Vehicle: {appointment_data['vehicle']}\n"
                f"- Date: {appointment_data['date']} at {appointment_data['time']}\n"
                f"- Service: {appointment_data['service_type']}\n"
                f"- Urgency: {appointment_data['urgency']}\n"
                f"Confirm this booking enthusiastically in your reply."
            )

        vehicle_info = "No specific vehicle selected."
        if vehicle:
            prob = int((vehicle.ai_failure_probability or 0) * 100)
            vehicle_info = (
                f"{vehicle.name}: risk level={vehicle.ai_risk_level or 'not analysed'}, "
                f"engine failure probability={prob}%"
                + (f", affected component: {vehicle.ai_component}" if vehicle.ai_component else "")
            )

        prompt = f"""You are an AI vehicle maintenance assistant. Be helpful, concise, and friendly.

User message: {user_message}

Selected vehicle: {vehicle_info}

All user vehicles:
{vehicles_context if vehicles_context else "No vehicles registered yet."}{appt_info}

Guidelines:
- If an appointment was booked, confirm it clearly with the date/time/vehicle.
- If the user asks about risk or health, explain it in plain language using the numbers above.
- If risk is HIGH, strongly recommend immediate servicing.
- Keep response under 150 words.
"""
        return call_llm(prompt)

    except Exception:
        if appointment_data:
            return (
                f"I've booked a service appointment for {appointment_data['vehicle']} "
                f"on {appointment_data['date']} at {appointment_data['time']}. "
                f"Urgency: {appointment_data['urgency']}. You can view it in your appointments."
            )

        if vehicle and vehicle.ai_risk_level == "HIGH":
            return (
                "Your vehicle shows HIGH risk indicators. "
                "Immediate servicing is strongly recommended to prevent breakdown."
            )

        return (
            "I'm here to help with your vehicle maintenance. "
            "Try asking about your vehicle's health, or say 'book an appointment' to schedule a service."
        )
