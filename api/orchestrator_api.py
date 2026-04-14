from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from orchestrators.master_orchestrator import MasterOrchestrator

app = FastAPI(title="ProactiveAI Orchestrator API")

# Enable CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = MasterOrchestrator()
# -----------------------------
# Request & Response Schemas
# -----------------------------

class AnalyzeRequest(BaseModel):
    sensor_data: Dict[str, Any]
    user_context: Optional[str] = ""

class AnalyzeResponse(BaseModel):
    timestamp: str
    analysis: str
    status: str
    component: str
    failureProbability: float
    riskLevel: str
    confidence: float
    estimatedFailureWindow: Optional[str] = ""

# -----------------------------
# Routes
# -----------------------------

@app.get("/")
def root():
    return {
        "status": "Orchestrator API running",
        "endpoints": {
            "POST /analyze": "Run full agentic analysis"
        }
    }

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_vehicle(data: AnalyzeRequest):
    try:
        result = orchestrator.analyze(
            sensor_data=data.sensor_data,
            user_context=data.user_context
        )

        return {
            "timestamp": result.get("timestamp"),
            "analysis": result.get("analysis"),
            "status": result.get("status"),
            "component": result.get("component"),
            "failureProbability": result.get("failureProbability", 0),
            "riskLevel": result.get("riskLevel", "LOW"),
            "confidence": result.get("confidence", 0),
            "estimatedFailureWindow": result.get("estimatedFailureWindow", ""),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestrator failed: {str(e)}"
        )

# -----------------------------
# Run locally
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
