from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from backend.session import get_db
from backend.models.vehicle import Vehicle
from backend.auth.dependencies import get_current_user
from backend.models.user import User
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary/me")
def dashboard_summary_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    total_vehicles = db.query(func.count(Vehicle.id))\
        .filter(Vehicle.user_id == user.id).scalar()

    avg_mileage = db.query(func.avg(Vehicle.mileage))\
        .filter(Vehicle.user_id == user.id).scalar()

    low_fuel_count = db.query(func.count(Vehicle.id))\
        .filter(Vehicle.user_id == user.id, Vehicle.fuel_level < 25).scalar()

    recent_vehicles = (
        db.query(Vehicle)
        .filter(Vehicle.user_id == user.id)
        .order_by(Vehicle.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_vehicles": total_vehicles or 0,
        "avg_mileage": int(avg_mileage or 0),
        "low_fuel_count": low_fuel_count or 0,
        "recent_vehicles": recent_vehicles,
    }
