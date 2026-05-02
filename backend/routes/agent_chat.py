from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, time, timedelta

from backend.session import get_db
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.models.vehicle import Vehicle
from backend.models.appointment import Appointment
from agents.agentic_chat_agent import agentic_chat_agent
from agents.agentic_scheduling_agent import agentic_scheduling_agent

router = APIRouter(prefix="/agent", tags=["Agent Chat"])

SCHEDULE_KEYWORDS = {"book", "schedule", "appointment", "service", "fix", "repair", "maintenance", "inspect"}


@router.post("/chat")
def agent_chat(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    message = payload.get("message", "")
    vehicle_id = payload.get("vehicle_id")

    all_vehicles = db.query(Vehicle).filter(Vehicle.user_id == user.id).all()

    # Pick focus vehicle: explicitly requested > highest risk > first
    vehicle = None
    if vehicle_id:
        vehicle = next((v for v in all_vehicles if str(v.id) == str(vehicle_id)), None)
    if vehicle is None and all_vehicles:
        vehicle = sorted(all_vehicles, key=lambda v: v.ai_failure_probability or 0, reverse=True)[0]

    vehicles_context = "\n".join(
        f"- {v.name}: risk={v.ai_risk_level or 'not analysed'}, "
        f"failure_prob={int((v.ai_failure_probability or 0) * 100)}%"
        for v in all_vehicles
    )

    # Auto-book if user expresses scheduling intent for a high/medium risk vehicle
    appointment_data = None
    words = set(message.lower().split())
    wants_appointment = bool(words & SCHEDULE_KEYWORDS)

    if wants_appointment and vehicle and vehicle.ai_risk_level in ("HIGH", "MEDIUM"):
        vehicle_state = {
            "risk_level": vehicle.ai_risk_level,
            "failure_probability": vehicle.ai_failure_probability,
            "last_analyzed": vehicle.ai_last_analyzed,
        }
        decision = agentic_scheduling_agent(vehicle_state)
        urgency = decision.get("recommended_urgency", "MEDIUM") if isinstance(decision, dict) else "MEDIUM"

        days_ahead = 2 if urgency == "HIGH" else 5
        appt_date = date.today() + timedelta(days=days_ahead)

        appointment = Appointment(
            user_id=user.id,
            vehicle_id=vehicle.id,
            service_type="AI Recommended",
            appointment_date=appt_date,
            appointment_time=time(10, 0),
            urgency=urgency,
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        appointment_data = {
            "appointment_id": str(appointment.id),
            "vehicle": vehicle.name,
            "date": appt_date.isoformat(),
            "time": "10:00",
            "urgency": urgency,
            "service_type": "AI Recommended",
        }

    reply = agentic_chat_agent(
        user_message=message,
        vehicle=vehicle,
        vehicles_context=vehicles_context,
        appointment_data=appointment_data,
    )

    return {
        "reply": reply,
        "appointment": appointment_data,
    }
