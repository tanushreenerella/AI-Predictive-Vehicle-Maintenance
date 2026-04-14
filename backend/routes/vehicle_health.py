from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.session import get_db
from backend.models.vehicle import Vehicle
from backend.auth.dependencies import get_current_user
from backend.models.user import User
router = APIRouter(prefix="/vehicles", tags=["Vehicle Health"])

def calculate_health(vehicle: Vehicle):
    """
    Translate AI health into UI-compatible fields
    """

    if vehicle.ai_risk_level == "HIGH":
        return 30, "critical"

    if vehicle.ai_risk_level == "MEDIUM":
        return 60, "warning"

    if vehicle.ai_risk_level == "LOW":
        return 90, "optimal"

    # fallback (before AI runs)
    return 80, "optimal"

@router.get("/health/me")
def vehicle_health_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    print("LOGGED IN USER:", user.id)
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == user.id).all()
    print("VEHICLES FOUND:", len(vehicles))
    result = []
    for v in vehicles:
        health, status = calculate_health(v)
        result.append({
            "id": v.id,
            "name": v.name,
            "model": v.model,
            "registration_number": v.registration_number,
            "health": health,
            "status": status,
            "mileage": v.mileage,
            "fuel_level": v.fuel_level,
        })

    return result
