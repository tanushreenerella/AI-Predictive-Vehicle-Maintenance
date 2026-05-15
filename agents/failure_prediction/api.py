from fastapi import FastAPI
from pydantic import BaseModel
from agents.failure_prediction.predict import predict_failure
from langchain_core.messages import HumanMessage
from agents.agentic_graph.graph import vehicle_graph
from agents.agentic_graph.state import VehicleAgentState
app = FastAPI(title="Failure Prediction Agent")

# Define input data schema
class SensorData(BaseModel):
    engine_rpm: float
    lub_oil_pressure: float
    fuel_pressure: float
    coolant_pressure: float
    lub_oil_temp: float
    coolant_temp: float

# Health check endpoint
@app.get("/")
def root():
    return {"status": "Failure Prediction Agent Online"}

# Prediction endpoint
@app.post("/predict")
def predict(data: SensorData):
    prediction = predict_failure(data.model_dump())
    return prediction

class ChatRequest(BaseModel):
    message: str
    state: dict = {}
    sensor_data: dict = {}
    vehicle_label: str = "your vehicle"

@app.post("/chat")
def chat(req: ChatRequest):
    init_state: VehicleAgentState = {
        "messages": [HumanMessage(content=req.message)],
        "phase": req.state.get("phase", "general"),
        "symptom": req.state.get("symptom"),
        "sensor_data": req.sensor_data or None,
        "diagnostic_answers": req.state.get("diagnostic_answers", []),
        "issue_context": req.state.get("issue_context"),
        "recommendation": req.state.get("recommendation"),
        "scheduling": req.state.get("scheduling"),
        "vehicle_label": req.vehicle_label,
        "failure_probability": req.state.get("failure_probability"),
        "risk_level": req.state.get("risk_level"),
        "next_agent": "supervisor",
    }
    result = vehicle_graph.invoke(init_state, config={"recursion_limit": 5})
    last_reply = result["messages"][-1].content if result["messages"] else "No response."
    return {
        "reply": last_reply,
        "phase": result.get("phase"),
        "risk_level": result.get("risk_level"),
        "recommendation": result.get("recommendation"),
        "scheduling": result.get("scheduling"),
        "state": {
            "phase": result.get("phase"),
            "symptom": result.get("symptom"),
            "diagnostic_answers": result.get("diagnostic_answers", []),
            "issue_context": result.get("issue_context"),
            "recommendation": result.get("recommendation"),
            "scheduling": result.get("scheduling"),
            "failure_probability": result.get("failure_probability"),
            "risk_level": result.get("risk_level"),
        }
    }
