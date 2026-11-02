from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.models.vehicle import Vehicle
from backend.rate_limit import EXPENSIVE_LIMIT, limiter
from backend.session import get_db

router = APIRouter(tags=["Analysis"])
_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        from orchestrators.master_orchestrator import MasterOrchestrator
        _orchestrator = MasterOrchestrator()
    return _orchestrator

class AnalyzeRequest(BaseModel):
    vehicle_id: str
    sensor_data: Dict[str, Any]
    user_context: Optional[str] = ""

@router.post("/analyze")
@limiter.limit(EXPENSIVE_LIMIT)
def analyze_vehicle(
    request: Request,
    data: AnalyzeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == data.vehicle_id,
        Vehicle.user_id == user.id,
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    try:
        result = get_orchestrator().analyze(
            sensor_data=data.sensor_data,
            user_context=data.user_context,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
