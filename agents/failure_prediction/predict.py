import os
import pickle
from typing import Any, Dict

import numpy as np


def _base_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def load_model():
    base = _base_dir()

    for ext in [".joblib", ".pkl"]:
        model_path = os.path.join(base, f"model{ext}")
        scaler_path = os.path.join(base, f"scaler{ext}")

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                if ext == ".joblib":
                    import joblib

                    loaded_model = joblib.load(model_path)
                    loaded_scaler = joblib.load(scaler_path)
                else:
                    with open(model_path, "rb") as model_file:
                        loaded_model = pickle.load(model_file)
                    with open(scaler_path, "rb") as scaler_file:
                        loaded_scaler = pickle.load(scaler_file)

                print(f"Model loaded from {model_path}")
                return loaded_model, loaded_scaler, "production"
            except Exception as exc:
                print(f"Failed to load {model_path}: {exc}")

    print("Model file not found, using fallback")
    fallback_model, fallback_scaler = create_fallback_model()
    return fallback_model, fallback_scaler, "fallback"


def create_fallback_model():
    from sklearn.preprocessing import StandardScaler
    from xgboost import XGBClassifier

    np.random.seed(42)
    x_dummy = np.random.randn(100, 6)
    y_dummy = np.random.choice([0, 1], 100, p=[0.8, 0.2])

    fallback_scaler = StandardScaler()
    x_scaled = fallback_scaler.fit_transform(x_dummy)

    fallback_model = XGBClassifier(n_estimators=10, random_state=42)
    fallback_model.fit(x_scaled, y_dummy)

    print("Using fallback model")
    return fallback_model, fallback_scaler


try:
    model, scaler, MODEL_STATUS = load_model()
except Exception as exc:
    print(f"Prediction model initialization failed, using fallback: {exc}")
    model, scaler = create_fallback_model()
    MODEL_STATUS = "fallback"


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
        for feature in feature_order:
            value = sensor_data.get(feature, defaults[feature])
            try:
                features.append(float(value))
            except (ValueError, TypeError):
                features.append(defaults[feature])

        features_array = np.array([features])
        features_scaled = scaler.transform(features_array)
        probability = float(model.predict_proba(features_scaled)[0][1])

        if probability > 0.7:
            risk = "HIGH"
            window = "1-3 days"
        elif probability > 0.4:
            risk = "MEDIUM"
            window = "4-7 days"
        else:
            risk = "LOW"
            window = "8+ days"

        return {
            "component": "Engine",
            "failureProbability": round(probability, 3),
            "riskLevel": risk,
            "estimatedFailureWindow": window,
            "confidence": round(min(0.95, probability + 0.1), 2),
            "message": f"Analysis complete. Risk level: {risk}",
            "model_status": MODEL_STATUS,
            "input_features": dict(zip(feature_order, features)),
        }

    except Exception as exc:
        print(f"Prediction error: {exc}")
        return {
            "component": "Engine",
            "failureProbability": 0.5,
            "riskLevel": "UNKNOWN",
            "estimatedFailureWindow": "Unknown",
            "confidence": 0.5,
            "message": f"Error in prediction: {str(exc)}",
            "model_status": "error",
            "input_features": sensor_data,
        }
