from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from agents.failure_prediction.predict import predict_failure

router = APIRouter(tags=["Predictions"])

class SensorData(BaseModel):
    engine_rpm: float
    lub_oil_pressure: float
    fuel_pressure: float
    coolant_pressure: float
    lub_oil_temp: float
    coolant_temp: float

class FlexibleSensorData(BaseModel):
    engine_rpm: Optional[float] = None
    lub_oil_pressure: Optional[float] = None
    fuel_pressure: Optional[float] = None
    coolant_pressure: Optional[float] = None
    lub_oil_temp: Optional[float] = None
    coolant_temp: Optional[float] = None

@router.post("/predict")
def predict(data: SensorData):
    return predict_failure(data.dict())

@router.post("/predict_flex")
def predict_flex(data: FlexibleSensorData):
    defaults = {
        "engine_rpm": 3000.0, "lub_oil_pressure": 2.0,
        "fuel_pressure": 2.5, "coolant_pressure": 1.2,
        "lub_oil_temp": 90.0, "coolant_temp": 85.0,
    }
    provided = data.dict(exclude_none=True)
    return predict_failure({**defaults, **provided})