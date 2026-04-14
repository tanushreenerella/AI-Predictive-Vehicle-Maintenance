from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from backend.session import get_db
from backend.models.vehicle import Vehicle
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.services.orchestrator_service import run_vehicle_ai
router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


class VehicleCreate(BaseModel):
    user_id: str
    name: str
    model: str
    year: int
    registration_number: str
    mileage: int = 0
    fuel_level: int = 100


class VehicleResponse(VehicleCreate):
    id: str


@router.post("", response_model=VehicleResponse)
def add_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@router.get("/{user_id}", response_model=List[VehicleResponse])
def get_user_vehicles(user_id: str, db: Session = Depends(get_db)):
    return db.query(Vehicle).filter(Vehicle.user_id == user_id).all()

@router.post("/run/{vehicle_id}")
def run_analysis(
    vehicle_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id, Vehicle.user_id == user.id)
        .first()
    )

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    sensor_data = {
        "engine_rpm": 3200,
        "lub_oil_pressure": 1.8,
        "fuel_pressure": 2.4,
        "coolant_pressure": 1.2,
        "lub_oil_temp": 98,
        "coolant_temp": 92
    }

    result = run_vehicle_ai(vehicle, sensor_data, db)

    return {
        "status": "success",
        "vehicle_id": vehicle.id,
        "ai_state": result["health_update"],
        "report": result["ai_report"]
    }
