from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from agents.failure_prediction.predict import predict_failure
from backend.session import get_db
from backend.models.vehicle import Vehicle
from backend.models.user import User
from backend.auth.jwt import decode_token

router = APIRouter(tags=["Predictions"])


def _optional_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    try:
        auth = request.headers.get("Authorization", "")
        token = auth.split(" ", 1)[1] if auth.startswith("Bearer ") else request.cookies.get("access_token")
        if not token:
            return None
        payload = decode_token(token)
        return db.query(User).filter(User.id == payload.get("sub")).first()
    except Exception:
        return None


class SensorData(BaseModel):
    engine_rpm: float
    lub_oil_pressure: float
    fuel_pressure: float
    coolant_pressure: float
    lub_oil_temp: float
    coolant_temp: float
    vehicle_id: Optional[str] = None


class FlexibleSensorData(BaseModel):
    engine_rpm: Optional[float] = None
    lub_oil_pressure: Optional[float] = None
    fuel_pressure: Optional[float] = None
    coolant_pressure: Optional[float] = None
    lub_oil_temp: Optional[float] = None
    coolant_temp: Optional[float] = None
    vehicle_id: Optional[str] = None


@router.post("/predict")
def predict(
    data: SensorData,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(_optional_user),
):
    sensor = data.dict(exclude={"vehicle_id"})
    result = predict_failure(sensor)

    # Save result to vehicle if vehicle_id provided and user authenticated
    if data.vehicle_id and user:
        vehicle = db.query(Vehicle).filter(
            Vehicle.id == data.vehicle_id,
            Vehicle.user_id == user.id,
        ).first()
        if vehicle:
            vehicle.ai_risk_level = result["riskLevel"]
            vehicle.ai_failure_probability = result["failureProbability"]
            vehicle.ai_component = result.get("component")
            vehicle.ai_last_analyzed = datetime.utcnow()
            db.commit()

    return result


@router.post("/predict_flex")
def predict_flex(
    data: FlexibleSensorData,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(_optional_user),
):
    defaults = {
        "engine_rpm": 3000.0, "lub_oil_pressure": 2.0,
        "fuel_pressure": 2.5, "coolant_pressure": 1.2,
        "lub_oil_temp": 90.0, "coolant_temp": 85.0,
    }
    sensor = {**defaults, **data.dict(exclude_none=True, exclude={"vehicle_id"})}
    result = predict_failure(sensor)

    if data.vehicle_id and user:
        vehicle = db.query(Vehicle).filter(
            Vehicle.id == data.vehicle_id,
            Vehicle.user_id == user.id,
        ).first()
        if vehicle:
            vehicle.ai_risk_level = result["riskLevel"]
            vehicle.ai_failure_probability = result["failureProbability"]
            vehicle.ai_component = result.get("component")
            vehicle.ai_last_analyzed = datetime.utcnow()
            db.commit()

    return result
