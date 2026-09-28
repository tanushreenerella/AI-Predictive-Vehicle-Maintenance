"""
Shared feature definitions for the engine failure-prediction pipeline.

train.py and predict.py both import from here so that training and inference
can never drift apart on which engineered features exist or what order they
are fed to the scaler/model in.

Label semantics (from data/raw/engine_data.csv / "Engine Condition"):
    0 = Unhealthy / FAILURE
    1 = Healthy / NO FAILURE
This was verified against the dataset's own documentation
(engine-health-prediction-69-failure-detection.ipynb), not assumed.
"""

import pandas as pd

FAILURE_LABEL = 0
HEALTHY_LABEL = 1

BASE_FEATURE_COLUMNS = [
    "engine_rpm",
    "lub_oil_pressure",
    "fuel_pressure",
    "coolant_pressure",
    "lub_oil_temp",
    "coolant_temp",
]

ENGINEERED_FEATURE_COLUMNS = [
    "rpm_oil_ratio",
    "temp_diff",
    "pressure_total",
]

# Exact column order the scaler/model were fit on. Do not reorder without retraining.
ALL_FEATURE_COLUMNS = BASE_FEATURE_COLUMNS + ENGINEERED_FEATURE_COLUMNS


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add the engineered features to a DataFrame that already has BASE_FEATURE_COLUMNS,
    and return only ALL_FEATURE_COLUMNS in the fixed order the model expects.
    """
    df = df.copy()
    df["rpm_oil_ratio"] = df["engine_rpm"] / (df["lub_oil_pressure"] + 0.001)
    df["temp_diff"] = df["lub_oil_temp"] - df["coolant_temp"]
    df["pressure_total"] = df["fuel_pressure"] + df["coolant_pressure"] + df["lub_oil_pressure"]
    return df[ALL_FEATURE_COLUMNS]


def risk_level_for(probability: float) -> str:
    """Policy: <0.40 = LOW, <0.70 = MEDIUM, >=0.70 = HIGH."""
    if probability >= 0.70:
        return "HIGH"
    if probability >= 0.40:
        return "MEDIUM"
    return "LOW"
