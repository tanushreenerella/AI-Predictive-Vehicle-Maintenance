from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from backend.session import get_db
from backend.models.vehicle import Vehicle
from backend.auth.dependencies import get_current_user
from backend.models.user import User
router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


# ---------- Schemas ----------

class VehicleCreate(BaseModel):
    name: str
    model: str
    year: int
    registration_number: str
    mileage: int = 0
    fuel_level: int = 100


class VehicleResponse(VehicleCreate):
    id: str


# ---------- Routes ----------

@router.post("", response_model=VehicleResponse)
def add_vehicle(
    vehicle: VehicleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    db_vehicle = Vehicle(
        **vehicle.dict(),
        user_id=user.id,  # ✅ backend-controlled
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@router.get("/me", response_model=List[VehicleResponse])
def get_my_vehicles(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(Vehicle).filter(Vehicle.user_id == user.id).all()
