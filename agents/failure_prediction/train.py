import json
import logging
import os

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

DATA_PATH = "data/raw/engine_data.csv"
MODEL_DIR = "agents/failure_prediction"

FEATURE_COLUMNS = [
    "engine_rpm",
    "lub_oil_pressure",
    "fuel_pressure",
    "coolant_pressure",
    "lub_oil_temp",
    "coolant_temp",
]
TARGET_COLUMN = "engine_condition"


def load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

    data = pd.read_csv(DATA_PATH)
    data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_")

    missing = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c not in data.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    return data


def remove_outliers(data: pd.DataFrame) -> pd.DataFrame:
    # Coolant temp above 150°C is physically implausible — drop those rows
    before = len(data)
    data = data[data["coolant_temp"] < 150].copy()
    dropped = before - len(data)
    if dropped:
        log.info("Dropped %d outlier rows (coolant_temp >= 150)", dropped)
    return data


def train_model():
    os.makedirs(MODEL_DIR, exist_ok=True)

    log.info("Loading dataset from %s", DATA_PATH)
    data = load_data()
    log.info("Loaded %d rows", len(data))

    data = remove_outliers(data)

    X = data[FEATURE_COLUMNS]
    y = data[TARGET_COLUMN]
    X = X.copy()
    X['rpm_oil_ratio'] = X['engine_rpm'] / (X['lub_oil_pressure'] + 0.001)
    X['temp_diff'] = X['lub_oil_temp'] - X['coolant_temp']
    X['pressure_total'] = X['fuel_pressure'] + X['coolant_pressure'] + X['lub_oil_pressure']

    log.info("Class distribution: %s", y.value_counts().to_dict())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_res)
    y_train = y_train_res
    X_test_scaled = scaler.transform(X_test)

    log.info("Training LightGBM model...")
    model = LGBMClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    class_weight='balanced',
    random_state=42,
    verbose=-1,
    )

    model.fit(X_train_scaled, y_train)

    proba = model.predict_proba(X_test_scaled)[:, 1]
    preds = (proba >= 0.5).astype(int)

    metrics = {
        "accuracy": round(accuracy_score(y_test, preds), 4),
        "precision": round(precision_score(y_test, preds), 4),
        "recall": round(recall_score(y_test, preds), 4),
        "f1": round(f1_score(y_test, preds), 4),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "features": FEATURE_COLUMNS,
    }

    log.info("Accuracy:  %.2f%%", metrics["accuracy"] * 100)
    log.info("Precision: %.2f%%", metrics["precision"] * 100)
    log.info("Recall:    %.2f%%", metrics["recall"] * 100)
    log.info("F1:        %.2f%%", metrics["f1"] * 100)
    log.info("\n%s", classification_report(y_test, preds))

    joblib.dump(model, os.path.join(MODEL_DIR, "model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))

    metrics_path = os.path.join(MODEL_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    log.info("Model saved to %s/model.joblib", MODEL_DIR)
    log.info("Metrics saved to %s", metrics_path)


if __name__ == "__main__":
    train_model()
