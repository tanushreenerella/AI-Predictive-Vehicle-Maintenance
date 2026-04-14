"""
agents/failure_prediction/predict.py - UPDATED
"""
import numpy as np
import pickle
import os
from typing import Dict, Any

def load_model():
    """Load model with error handling"""
    try:
        model_path = "agents/failure_prediction/model.pkl"
        scaler_path = "agents/failure_prediction/scaler.pkl"
        
        if not os.path.exists(model_path):
            print("⚠️ Model file not found, using fallback")
            return create_fallback_model()
        
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)
            
        return model, scaler
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return create_fallback_model()

def create_fallback_model():
    """Create simple fallback model"""
    from sklearn.preprocessing import StandardScaler
    from xgboost import XGBClassifier
    
    np.random.seed(42)
    X_dummy = np.random.randn(100, 6)
    y_dummy = np.random.choice([0, 1], 100, p=[0.8, 0.2])
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_dummy)
    
    model = XGBClassifier(n_estimators=10, random_state=42)
    model.fit(X_scaled, y_dummy)
    
    print("⚠️ Using fallback model")
    return model, scaler

# Load model at startup
try:
    model, scaler = load_model()
    MODEL_LOADED = True
except:
    model, scaler = create_fallback_model()
    MODEL_LOADED = False

def predict_failure(sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict failure from sensor data
    """
    try:
        # Extract features in correct order
        feature_order = [
            "engine_rpm",
            "lub_oil_pressure", 
            "fuel_pressure",
            "coolant_pressure",
            "lub_oil_temp",
            "coolant_temp"
        ]
        
        # Validate we have all required features
        missing = [f for f in feature_order if f not in sensor_data]
        if missing:
            print(f"⚠️ Missing features, using defaults: {missing}")
            # Provide defaults
            defaults = {
                "engine_rpm": 3000.0,
                "lub_oil_pressure": 2.0,
                "fuel_pressure": 2.5,
                "coolant_pressure": 1.2,
                "lub_oil_temp": 90.0,
                "coolant_temp": 85.0
            }
            for m in missing:
                sensor_data[m] = defaults.get(m, 0.0)
        
        # Create feature array
        features = []
        for feature in feature_order:
            value = sensor_data.get(feature)
            # Convert to float
            try:
                features.append(float(value))
            except (ValueError, TypeError):
                print(f"⚠️ Invalid value for {feature}: {value}, using default")
                features.append(0.0)
        
        features_array = np.array([features])
        
        # Scale features
        features_scaled = scaler.transform(features_array)
        
        # Get prediction
        prob = model.predict_proba(features_scaled)[0][1]
        
        # Determine risk level
        if prob > 0.7:
            risk = "HIGH"
            window = "1-3 days"
        elif prob > 0.4:
            risk = "MEDIUM"
            window = "4-7 days"
        else:
            risk = "LOW"
            window = "8+ days"
        
        return {
            "component": "Engine",
            "failureProbability": round(float(prob), 3),
            "riskLevel": risk,
            "estimatedFailureWindow": window,
            "confidence": round(min(0.95, prob + 0.1), 2),
            "message": f"Analysis complete. Risk level: {risk}",
            "model_status": "production" if MODEL_LOADED else "fallback"
        }
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return {
            "component": "Engine",
            "failureProbability": 0.5,
            "riskLevel": "UNKNOWN",
            "estimatedFailureWindow": "Unknown",
            "confidence": 0.5,
            "message": f"Error in prediction: {str(e)}",
            "model_status": "error"
        }