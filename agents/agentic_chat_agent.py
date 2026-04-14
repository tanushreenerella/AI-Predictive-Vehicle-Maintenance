from agents.llm import call_llm
from datetime import date

def agentic_chat_agent(user_message, vehicle=None, appointment=None):
    try:
        prompt = f"""
You are an AI vehicle service assistant.

User question:
{user_message}

Vehicle info:
{vehicle}

Appointment info:
{appointment}

Give a clear, helpful, short answer.
"""

        response = call_llm(prompt)
        return response

    except Exception:
        # 🔁 FALLBACK LOGIC (VERY IMPORTANT)
        if appointment and appointment.appointment_date < date.today():
            return "This appointment is already past, so the service should be completed."

        if vehicle and vehicle.ai_risk_level == "HIGH":
            return (
                "Your vehicle shows high risk indicators. "
                "Delaying service may increase the chance of breakdown. "
                "I strongly recommend rescheduling soon."
            )

        return (
            "Based on current data, the situation does not appear critical, "
            "but timely servicing is always safer."
        )
