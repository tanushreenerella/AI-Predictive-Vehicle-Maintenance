from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.models.vehicle import Vehicle
from backend.session import get_db
from backend.services.vehicle_analysis import repair_duplicate_vehicle_analyses

router = APIRouter(prefix="/vehicles", tags=["Vehicle Health"])


@router.get("/health/me")
def vehicle_health_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == user.id).all()
    repair_duplicate_vehicle_analyses(vehicles, db)
    result = []

    for vehicle in vehicles:
        failure_probability = vehicle.ai_failure_probability
        health = (
            max(0, min(100, round(100 - failure_probability * 100)))
            if failure_probability is not None
            else None
        )
        result.append({
            "id": vehicle.id,
            "name": vehicle.name,
            "model": vehicle.model,
            "registration_number": vehicle.registration_number,
            "mileage": vehicle.mileage,
            "fuel_level": vehicle.fuel_level,
            "last_service_date": None,
            "next_service_date": None,
            "health": health,
            "failure_probability": failure_probability,
            "risk_level": vehicle.ai_risk_level,
            "ai_risk_level": vehicle.ai_risk_level,
            "ai_failure_probability": failure_probability,
            "ai_component": vehicle.ai_component,
            "ai_last_analyzed": vehicle.ai_last_analyzed.isoformat() if vehicle.ai_last_analyzed else None,
        })

    return result
