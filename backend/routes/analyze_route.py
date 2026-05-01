from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter(tags=["Analysis"])
_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        from orchestrators.master_orchestrator import MasterOrchestrator
        _orchestrator = MasterOrchestrator()
    return _orchestrator

class AnalyzeRequest(BaseModel):
    sensor_data: Dict[str, Any]
    user_context: Optional[str] = ""

@router.post("/analyze")
def analyze_vehicle(data: AnalyzeRequest):
    try:
        result = get_orchestrator().analyze(
            sensor_data=data.sensor_data,
            user_context=data.user_context,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")