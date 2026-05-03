from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from backend.session import get_db
from backend.models.vehicle import Vehicle
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from agents.failure_prediction.predict import predict_failure
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


class SensorData(BaseModel):
    engine_rpm: float
    lub_oil_pressure: float
    fuel_pressure: float
    coolant_pressure: float
    lub_oil_temp: float
    coolant_temp: float


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
    sensor_data: SensorData,
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

    result = predict_failure(sensor_data.dict())
    vehicle.ai_risk_level = result["riskLevel"]
    vehicle.ai_failure_probability = result["failureProbability"]
    vehicle.ai_component = result.get("component")
    vehicle.ai_last_analyzed = datetime.utcnow()
    db.commit()

    return {
        "status": "success",
        "vehicle_id": vehicle.id,
        "ai_state": {
            "risk_level": vehicle.ai_risk_level,
            "failure_probability": vehicle.ai_failure_probability,
            "critical_component": vehicle.ai_component,
            "confidence": result.get("confidence"),
            "estimated_failure_window": result.get("estimatedFailureWindow"),
            "model_status": result.get("model_status"),
            "input_features": result.get("input_features"),
        },
        "report": result,
    }
