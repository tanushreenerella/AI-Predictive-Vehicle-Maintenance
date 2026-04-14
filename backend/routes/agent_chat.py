from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.session import get_db
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.models.vehicle import Vehicle
from backend.models.appointment import Appointment
from agents.agentic_chat_agent import agentic_chat_agent

router = APIRouter(prefix="/agent", tags=["Agent Chat"])

@router.post("/chat")
def agent_chat(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    message = payload.get("message")
    vehicle_id = payload.get("vehicle_id")
    appointment_id = payload.get("appointment_id")

    vehicle = None
    appointment = None

    if vehicle_id:
        vehicle = db.query(Vehicle).filter(
            Vehicle.id == vehicle_id,
            Vehicle.user_id == user.id
        ).first()

    if appointment_id:
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.user_id == user.id
        ).first()

    response = agentic_chat_agent(
        user_message=message,
        vehicle=vehicle,
        appointment=appointment,
    )

    return {
        "reply": response
    }
