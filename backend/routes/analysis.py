from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.session import get_db
from backend.models.vehicle import Vehicle
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.sensors import SensorReadings
from backend.services.vehicle_analysis import apply_vehicle_analysis
router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.post("/run/{vehicle_id}")
def run_analysis(
    vehicle_id: str,
    sensor_data: SensorReadings,
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

    result = apply_vehicle_analysis(vehicle, db, sensor_data.model_dump())

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
