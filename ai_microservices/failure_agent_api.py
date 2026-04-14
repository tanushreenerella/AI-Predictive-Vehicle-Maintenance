"""
ai_microservices/failure_agent_api.py - FIXED VERSION
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import traceback

# Import your prediction function
try:
    from agents.failure_prediction.predict import predict_failure
except ImportError:
    # Fallback if module not found
    def predict_failure(sensor_data: dict):
        return {
            "component": "Engine",
            "failureProbability": 0.5,
            "riskLevel": "MEDIUM",
            "estimatedFailureWindow": "7-10 days",
            "confidence": 0.7,
            "message": "Fallback mode - prediction module not loaded"
        }

app = FastAPI(
    title="Failure Prediction Agent",
    description="Predicts vehicle component failures from sensor data",
    version="1.0.0"
)

# ✅ FIXED: Define EXACT schema with proper validation
class SensorData(BaseModel):
    engine_rpm: float = Field(..., ge=0, le=10000, description="Engine RPM (0-10000)")
    lub_oil_pressure: float = Field(..., ge=0, le=5.0, description="Lubrication oil pressure in bar")
    fuel_pressure: float = Field(..., ge=0, le=5.0, description="Fuel pressure in bar")
    coolant_pressure: float = Field(..., ge=0, le=3.0, description="Coolant pressure in bar")
    lub_oil_temp: float = Field(..., ge=-20, le=150, description="Lubrication oil temperature in °C")
    coolant_temp: float = Field(..., ge=-20, le=150, description="Coolant temperature in °C")
    
    class Config:
        schema_extra = {
            "example": {
                "engine_rpm": 3200.0,
                "lub_oil_pressure": 1.9,
                "fuel_pressure": 2.3,
                "coolant_pressure": 1.4,
                "lub_oil_temp": 95.0,
                "coolant_temp": 88.0
            }
        }

# Alternative: Flexible schema (if you want to accept partial data)
class FlexibleSensorData(BaseModel):
    engine_rpm: Optional[float] = Field(None, ge=0, le=10000)
    lub_oil_pressure: Optional[float] = Field(None, ge=0, le=5.0)
    fuel_pressure: Optional[float] = Field(None, ge=0, le=5.0)
    coolant_pressure: Optional[float] = Field(None, ge=0, le=3.0)
    lub_oil_temp: Optional[float] = Field(None, ge=-20, le=150)
    coolant_temp: Optional[float] = Field(None, ge=-20, le=150)

@app.get("/")
def root():
    return {
        "status": "Failure Prediction Agent Online",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "This info",
            "GET /health": "Health check",
            "POST /predict": "Predict failure with full schema",
            "POST /predict_flex": "Predict with flexible schema"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "failure_agent",
        "timestamp": "2024-01-01T00:00:00Z"  # You can use datetime.now().isoformat()
    }

@app.post("/predict")
def predict(data: SensorData):
    """Main prediction endpoint with strict validation"""
    try:
        # Convert Pydantic model to dict
        sensor_dict = data.dict()
        
        # Call prediction function
        prediction = predict_failure(sensor_dict)
        
        return {
            **prediction,
            "api_version": "1.0",
            "validation": "strict"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

@app.post("/predict_flex")
def predict_flexible(data: FlexibleSensorData):
    """Flexible endpoint that handles missing fields"""
    try:
        # Get only the fields that were provided
        sensor_dict = data.dict(exclude_none=True)
        
        # Provide defaults for missing fields
        defaults = {
            "engine_rpm": 3000.0,
            "lub_oil_pressure": 2.0,
            "fuel_pressure": 2.5,
            "coolant_pressure": 1.2,
            "lub_oil_temp": 90.0,
            "coolant_temp": 85.0
        }
        
        # Merge provided data with defaults
        full_data = {**defaults, **sensor_dict}
        
        # Call prediction function
        prediction = predict_failure(full_data)
        
        return {
            **prediction,
            "api_version": "1.0",
            "validation": "flexible",
            "provided_fields": list(sensor_dict.keys()),
            "defaulted_fields": [k for k in defaults if k not in sensor_dict]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Flexible prediction failed: {str(e)}\n{traceback.format_exc()}"
        )

@app.post("/predict_raw")
async def predict_raw(payload: Dict[str, Any]):
    """Raw endpoint that accepts any JSON - for debugging"""
    try:
        print(f"📥 Received raw payload: {payload}")
        
        # Validate manually
        required_fields = [
            "engine_rpm", "lub_oil_pressure", "fuel_pressure",
            "coolant_pressure", "lub_oil_temp", "coolant_temp"
        ]
        
        missing = [field for field in required_fields if field not in payload]
        
        if missing:
            return {
                "error": "Missing fields",
                "missing_fields": missing,
                "received_fields": list(payload.keys()),
                "advice": f"Please provide all fields: {required_fields}"
            }
        
        # Ensure all values are numbers
        for field in required_fields:
            if not isinstance(payload[field], (int, float)):
                try:
                    payload[field] = float(payload[field])
                except:
                    return {
                        "error": f"Invalid type for {field}",
                        "value": payload[field],
                        "type": type(payload[field]).__name__
                    }
        
        # Call prediction
        prediction = predict_failure(payload)
        
        return {
            **prediction,
            "api_version": "1.0",
            "validation": "raw",
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "status": "error"
        }

# Error handlers
@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body,
            "advice": "Check that all fields are present and have correct types"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)