from datetime import date

def reschedule_warning_agent(appointment, vehicle):
    days_until = (appointment.appointment_date - date.today()).days

    if appointment.appointment_date < date.today():
        return {
            "level": "NONE",
            "message": "Appointment already completed",
            "recommendation": None
        }

    if vehicle.ai_risk_level == "HIGH" and days_until > 5:
        return {
            "level": "HIGH",
            "message": "High failure risk detected before scheduled service",
            "recommendation": f"Reschedule within next 3 days"
        }

    if vehicle.ai_risk_level == "MEDIUM" and days_until > 10:
        return {
            "level": "MEDIUM",
            "message": "Moderate risk detected before scheduled service",
            "recommendation": f"Consider rescheduling earlier"
        }

    return {
        "level": "NONE",
        "message": "No reschedule needed",
        "recommendation": None
    }
