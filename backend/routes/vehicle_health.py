from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.session import get_db
from backend.models.vehicle import Vehicle
from backend.auth.dependencies import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/vehicles", tags=["Vehicle Health"])


@router.get("/health/me")
def vehicle_health_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == user.id).all()
    result = []
    for v in vehicles:
        result.append({
            "id": v.id,
            "name": v.name,
            "model": v.model,
            "registration_number": v.registration_number,
            "mileage": v.mileage,
            "fuel_level": v.fuel_level,
            "last_service_date": None,
            "next_service_date": None,
            # AI fields — used by normalizer for health/status/alerts
            "ai_risk_level": v.ai_risk_level,
            "ai_failure_probability": v.ai_failure_probability,
            "ai_component": v.ai_component,
            "ai_last_analyzed": v.ai_last_analyzed.isoformat() if v.ai_last_analyzed else None,
        })
    return result
