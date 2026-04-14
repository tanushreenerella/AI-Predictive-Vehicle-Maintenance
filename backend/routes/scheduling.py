from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, time
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

from backend.session import get_db
from backend.models.vehicle import Vehicle
from backend.models.appointment import Appointment
from backend.models.user import User
from backend.auth.dependencies import get_current_user

from agents.agentic_scheduling_agent import agentic_scheduling_agent
from agents.reschedule_warning_agent import reschedule_warning_agent

router = APIRouter(prefix="/schedule", tags=["Scheduling"])


# -------------------------------------------------
# AI SUGGESTED SCHEDULE
# -------------------------------------------------
@router.get("/suggestion/{vehicle_id}")
def get_schedule_suggestion(
    vehicle_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.user_id == user.id
    ).first()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    vehicle_state = {
        "risk_level": vehicle.ai_risk_level,
        "failure_probability": vehicle.ai_failure_probability,
        "last_analyzed": vehicle.ai_last_analyzed,
    }
    decision = agentic_scheduling_agent(vehicle_state)

    return {
    "ai_decision": decision,
    "recommended_action": (
        "SCHEDULE_NOW"
        if decision["recommended_urgency"] == "HIGH"
        else "SCHEDULE_SOON"
    )
}



# -------------------------------------------------
# CREATE APPOINTMENT
# -------------------------------------------------
@router.post("")
def create_appointment(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == payload.get("vehicle_id"),
        Vehicle.user_id == user.id
    ).first()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    try:
        appointment = Appointment(
            user_id=user.id,
            vehicle_id=vehicle.id,
            service_type=payload["service_type"],
            appointment_date=date.fromisoformat(payload["appointment_date"]),
            appointment_time=time.fromisoformat(payload["appointment_time"]),
            urgency=payload["urgency"],
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid appointment data")

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return {
        "status": appointment.status,
        "appointment_id": str(appointment.id),
        "vehicle": vehicle.name,
        "date": appointment.appointment_date,
        "time": appointment.appointment_time,
        "urgency": appointment.urgency,
    }


# -------------------------------------------------
# GET MY APPOINTMENTS + AI WARNING
# -------------------------------------------------
@router.get("/me")
def get_my_appointments(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    appointments = (
        db.query(Appointment)
        .filter(Appointment.user_id == user.id)
        .order_by(Appointment.appointment_date, Appointment.appointment_time)
        .all()
    )

    result = []

    for a in appointments:
        vehicle = db.query(Vehicle).filter(
            Vehicle.id == a.vehicle_id
        ).first()

        ai_warning = reschedule_warning_agent(a, vehicle)

        result.append({
            "id": str(a.id),
            "vehicle_id": a.vehicle_id,
            "service_type": a.service_type,
            "appointment_date": a.appointment_date.isoformat(),
            "appointment_time": a.appointment_time.strftime("%H:%M"),
            "urgency": a.urgency,
            "status": (
                "COMPLETED"
                if a.appointment_date < date.today()
                else a.status
            ),
            "ai_warning": ai_warning,
            "created_at": a.created_at.isoformat(),
        })

    return result


# -------------------------------------------------
# CANCEL APPOINTMENT
# -------------------------------------------------
@router.delete("/{appointment_id}")
def cancel_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.user_id == user.id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(appointment)
    db.commit()

    return {
        "status": "cancelled",
        "appointment_id": appointment_id
    }


# -------------------------------------------------
# RESCHEDULE APPOINTMENT
# -------------------------------------------------
@router.patch("/{appointment_id}")
def reschedule_appointment(
    appointment_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.user_id == user.id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    try:
        appointment.appointment_date = date.fromisoformat(payload["appointment_date"])
        appointment.appointment_time = time.fromisoformat(payload["appointment_time"])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date or time")

    db.commit()
    db.refresh(appointment)

    return {
        "status": "rescheduled",
        "appointment_id": appointment.id,
        "new_date": appointment.appointment_date,
        "new_time": appointment.appointment_time,
    }


# -------------------------------------------------
# RECEIPT JSON
# -------------------------------------------------
@router.get("/receipt/{appointment_id}")
def get_receipt(
    appointment_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.user_id == user.id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    vehicle = db.query(Vehicle).filter(
        Vehicle.id == appointment.vehicle_id
    ).first()

    return {
        "receipt_id": str(appointment.id),
        "vehicle": {
            "name": vehicle.name,
            "model": vehicle.model,
            "registration": vehicle.registration_number,
        },
        "service_type": appointment.service_type,
        "appointment_date": appointment.appointment_date,
        "appointment_time": appointment.appointment_time,
        "urgency": appointment.urgency,
        "created_at": appointment.created_at,
        "status": (
            "COMPLETED"
            if appointment.appointment_date < date.today()
            else appointment.status
        ),
        "ai_warning": reschedule_warning_agent(appointment, vehicle),
    }


# -------------------------------------------------
# RECEIPT PDF
# -------------------------------------------------
@router.get("/receipt/{appointment_id}/pdf")
def download_receipt_pdf(
    appointment_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.user_id == user.id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    vehicle = db.query(Vehicle).filter(
        Vehicle.id == appointment.vehicle_id
    ).first()

    status = (
        "COMPLETED"
        if appointment.appointment_date < date.today()
        else appointment.status
    )

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, height - 50, "ProactiveAI - Appointment Receipt")

    pdf.setFont("Helvetica", 12)
    y = height - 100

    lines = [
        f"Receipt ID: {appointment.id}",
        f"Vehicle: {vehicle.name} ({vehicle.model})",
        f"Registration: {vehicle.registration_number}",
        "",
        f"Service Type: {appointment.service_type}",
        f"Date: {appointment.appointment_date}",
        f"Time: {appointment.appointment_time}",
        f"Urgency: {appointment.urgency}",
        "",
        f"Booked On: {appointment.created_at}",
        "",
        f"Status: {status}",
    ]

    for line in lines:
        pdf.drawString(50, y, line)
        y -= 20

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=appointment_{appointment.id}.pdf"
        },
    )
