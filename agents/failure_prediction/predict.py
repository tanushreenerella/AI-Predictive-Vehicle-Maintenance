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

    print("Model file not found, using heuristic fallback")
    return None, None, "heuristic"


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
    print(f"Prediction model initialization failed, using heuristic fallback: {exc}")
    model, scaler = None, None
    MODEL_STATUS = "heuristic"


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
        rpm_oil_ratio = features[0] / (features[1] + 0.001)
        temp_diff = features[4] - features[5]
        pressure_total = features[2] + features[3] + features[1]
        features = features + [rpm_oil_ratio, temp_diff, pressure_total]

        if model is not None and scaler is not None:
            features_array = np.array([features])
            features_scaled = scaler.transform(features_array)
            probability = float(model.predict_proba(features_scaled)[0][0])
        else:
            probability = _heuristic_probability(dict(zip(feature_order, features)))

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


def _heuristic_probability(features: Dict[str, float]) -> float:
    rpm = features["engine_rpm"]
    oil_pressure = features["lub_oil_pressure"]
    fuel_pressure = features["fuel_pressure"]
    coolant_pressure = features["coolant_pressure"]
    oil_temp = features["lub_oil_temp"]
    coolant_temp = features["coolant_temp"]

    score = 0.08
    score += max(0, rpm - 2500) / 7000 * 0.18
    score += max(0, 2.2 - oil_pressure) / 2.2 * 0.24
    score += max(0, 2.4 - fuel_pressure) / 2.4 * 0.10
    score += max(0, 1.3 - coolant_pressure) / 1.3 * 0.12
    score += max(0, oil_temp - 90) / 70 * 0.16
    score += max(0, coolant_temp - 85) / 65 * 0.18
    score += ((rpm % 97) / 97) * 0.04
    return round(max(0.03, min(0.92, score)), 3)
