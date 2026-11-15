from fastapi import APIRouter, Depends, Request
from backend.sensors import PredictRequest
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from agents.agentic_graph.ml_result_cache import set_cached_ml_result
from agents.agentic_graph.state import build_ml_result
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



def _predict_and_save(data: PredictRequest, db: Session, user: Optional[User]) -> dict:
    sensor = data.model_dump(exclude={"vehicle_id"})
    result = predict_failure(sensor)

    # Save result to vehicle if vehicle_id provided and user authenticated
    if data.vehicle_id and user and not result.get("error"):
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

            # Make the complete result (incl. SHAP top_features) available to
            # a later /chat turn for this vehicle, via LangGraph state.
            set_cached_ml_result(vehicle.id, sensor, build_ml_result(result))

    return result


@router.post("/predict")
def predict(
    data: PredictRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(_optional_user),
):
    return _predict_and_save(data, db, user)


@router.post("/predict_flex")
def predict_flex(
    data: PredictRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(_optional_user),
):
    # Kept for existing callers. It used to fill missing sensors with
    # defaults; it now requires all six, exactly like /predict.
    return _predict_and_save(data, db, user)
