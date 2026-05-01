import numpy as np
import pickle
import os
from typing import Dict, Any

def _base_dir():
    return os.path.dirname(os.path.abspath(__file__))

def load_model():
    base = _base_dir()

    # Try joblib first (committed to git), then pkl
    for ext in [".joblib", ".pkl"]:
        model_path = os.path.join(base, f"model{ext}")
        scaler_path = os.path.join(base, f"scaler{ext}")

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                if ext == ".joblib":
                    import joblib
                    model = joblib.load(model_path)
                    scaler = joblib.load(scaler_path)
                else:
                    with open(model_path, "rb") as f:
                        model = pickle.load(f)
                    with open(scaler_path, "rb") as f:
                        scaler = pickle.load(f)
                print(f"✅ Model loaded from {model_path}")
                return model, scaler
            except Exception as e:
                print(f"❌ Failed to load {model_path}: {e}")

    print("⚠️ Model file not found, using fallback")
    return create_fallback_model()

def create_fallback_model():
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

try:
    model, scaler = load_model()
    MODEL_LOADED = True
except Exception:
    model, scaler = create_fallback_model()
    MODEL_LOADED = False

def predict_failure(sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        feature_order = [
            "engine_rpm",
            "lub_oil_pressure",
            "fuel_pressure",
            "coolant_pressure",
            "lub_oil_temp",
            "coolant_temp",
        ]

        defaults = {
            "engine_rpm": 3000.0,
            "lub_oil_pressure": 2.0,
            "fuel_pressure": 2.5,
            "coolant_pressure": 1.2,
            "lub_oil_temp": 90.0,
            "coolant_temp": 85.0,
        }

        features = []
        for feat in feature_order:
            val = sensor_data.get(feat, defaults[feat])
            try:
                features.append(float(val))
            except (ValueError, TypeError):
                features.append(defaults[feat])

        features_array = np.array([features])
        features_scaled = scaler.transform(features_array)
        prob = float(model.predict_proba(features_scaled)[0][1])

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
            "failureProbability": round(prob, 3),
            "riskLevel": risk,
            "estimatedFailureWindow": window,
            "confidence": round(min(0.95, prob + 0.1), 2),
            "message": f"Analysis complete. Risk level: {risk}",
            "model_status": "production" if MODEL_LOADED else "fallback",
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
            "model_status": "error",
        }
