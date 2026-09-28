from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.models.vehicle import Vehicle
from backend.session import get_db

router = APIRouter(prefix="/vehicles", tags=["Vehicle Health"])


def _health_payload(vehicle: Vehicle) -> dict:
    """Return a vehicle health record without treating unanalyzed data as AI output."""
    analyzed = vehicle.ai_last_analyzed is not None
    failure_probability = vehicle.ai_failure_probability if analyzed else None
    risk_level = vehicle.ai_risk_level if analyzed else None
    health = (
        max(0, min(100, round(100 - failure_probability * 100)))
        if failure_probability is not None
        else None
    )
    return {
        "id": vehicle.id,
        "name": vehicle.name,
        "model": vehicle.model,
        "year": vehicle.year,
        "registration_number": vehicle.registration_number,
        "mileage": vehicle.mileage,
        "fuel_level": vehicle.fuel_level,
        "last_service_date": None,
        "next_service_date": None,
        "analyzed": analyzed,
        "health": health,
        "failure_probability": failure_probability,
        "risk_level": risk_level,
        "ai_risk_level": risk_level,
        "ai_failure_probability": failure_probability,
        "ai_component": vehicle.ai_component,
        "ai_last_analyzed": vehicle.ai_last_analyzed.isoformat() if vehicle.ai_last_analyzed else None,
    }


@router.get("/health/me")
def vehicle_health_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == user.id).all()
    return [_health_payload(vehicle) for vehicle in vehicles]


@router.get("/health/{vehicle_id}")
def vehicle_health_by_id(
    vehicle_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Fetch one owned vehicle, including one that has not been analyzed."""
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.user_id == user.id,
    ).first()
    if vehicle is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return _health_payload(vehicle)
