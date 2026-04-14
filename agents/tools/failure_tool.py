import requests
from langchain.tools import tool
from typing import Dict, Any

@tool
def analyze_vehicle_data(sensor_data: Dict[str, Any]) -> str:
    """
    Predicts vehicle component failures from sensor data.
    
    Args:
        sensor_data: Dictionary containing sensor readings
            - engine_rpm: float
            - lub_oil_pressure: float  
            - fuel_pressure: float
            - coolant_pressure: float
            - lub_oil_temp: float
            - coolant_temp: float
    
    Returns:
        JSON string with prediction results
    """
    try:
        # Call your FastAPI endpoint
        url = "http://localhost:8000/predict"
        response = requests.post(url, json=sensor_data, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        return f"Prediction Results: {result}"
    except Exception as e:
        return f"Error calling prediction API: {str(e)}"