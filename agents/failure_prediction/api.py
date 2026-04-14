from fastapi import FastAPI
from pydantic import BaseModel
from agents.failure_prediction.predict import predict_failure

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
    prediction = predict_failure(data.dict())
    return prediction
