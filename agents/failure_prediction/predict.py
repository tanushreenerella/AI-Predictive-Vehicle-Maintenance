import os
import pickle
from typing import Any, Dict

import pandas as pd

from agents.failure_prediction.explain import BACKGROUND_PATH, FailureExplainer, top_features
from agents.failure_prediction.features import (
    BASE_FEATURE_COLUMNS,
    FAILURE_LABEL,
    engineer_features,
    risk_level_for,
)


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

    print("Model file not found")
    return None, None, "unavailable"


try:
    model, scaler, MODEL_STATUS = load_model()
except Exception as exc:
    print(f"Prediction model initialization failed: {exc}")
    model, scaler = None, None
    MODEL_STATUS = "unavailable"

# Column index of FAILURE_LABEL within model.predict_proba(...)'s output.
# Resolved once at import time (rather than assumed) so training and
# inference can never silently disagree on which column is "failure".
_FAILURE_COL = None
if model is not None:
    try:
        _FAILURE_COL = list(model.classes_).index(FAILURE_LABEL)
    except (AttributeError, ValueError) as exc:
        print(f"Model does not expose classes_ compatible with FAILURE_LABEL: {exc}")
        model, scaler = None, None
        MODEL_STATUS = "unavailable"

# SHAP explainer — optional. Explainability is an add-on: if shap isn't
# installed or the background artifact is missing, predictions still work,
# they just won't include "top_features".
_explainer = None
if model is not None and _FAILURE_COL is not None:
    if not os.path.exists(BACKGROUND_PATH):
        print(
            "SHAP background artifact is missing at "
            f"{BACKGROUND_PATH}; predictions will omit top_features. "
            "Deploy agents/failure_prediction/shap_background.joblib with the model."
        )
    else:
        try:
            import joblib as _joblib

            _background = _joblib.load(BACKGROUND_PATH)
            _explainer = FailureExplainer(model, _background, _FAILURE_COL)
            print(f"SHAP explainer ready (background: {BACKGROUND_PATH})")
        except Exception as exc:
            print(f"SHAP explainer unavailable, predictions will omit top_features: {exc}")
            _explainer = None


def predict_failure(sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    if model is None or scaler is None or _FAILURE_COL is None:
        return {
            "component": "Engine",
            "error": True,
            # Not a real prediction — callers must check "error" before using
            # these, but the keys are present so code expecting them doesn't crash.
            "failureProbability": None,
            "riskLevel": "ERROR",
            "message": "Prediction model is not available on this server.",
            "model_status": MODEL_STATUS,
            "input_features": sensor_data,
        }

    defaults = {
        "engine_rpm": 3000.0,
        "lub_oil_pressure": 2.0,
        "fuel_pressure": 2.5,
        "coolant_pressure": 1.2,
        "lub_oil_temp": 90.0,
        "coolant_temp": 85.0,
    }

    try:
        row = {}
        for feature in BASE_FEATURE_COLUMNS:
            value = sensor_data.get(feature, defaults[feature])
            try:
                row[feature] = float(value)
            except (ValueError, TypeError):
                row[feature] = defaults[feature]

        features_df = engineer_features(pd.DataFrame([row]))
        features_scaled = scaler.transform(features_df)

        probability = float(model.predict_proba(features_scaled)[0][_FAILURE_COL])
        risk = risk_level_for(probability)

        result = {
            "component": "Engine",
            "failureProbability": round(probability, 3),
            "riskLevel": risk,
            "message": f"Analysis complete. Risk level: {risk}",
            "model_status": MODEL_STATUS,
            "input_features": row,
        }

        if _explainer is not None:
            try:
                engineered_row = features_df.iloc[0].to_dict()
                shap_values = _explainer.shap_values_for(features_scaled)
                result["top_features"] = top_features(shap_values, engineered_row, top_n=3)
            except Exception as exc:
                # Explainability failing must never take down the prediction itself.
                print(f"SHAP explanation failed: {exc}")

        return result

    except Exception as exc:
        print(f"Prediction error: {exc}")
        return {
            "component": "Engine",
            "error": True,
            "failureProbability": None,
            "riskLevel": "ERROR",
            "message": f"Prediction failed: {exc}",
            "model_status": "error",
            "input_features": sensor_data,
        }
