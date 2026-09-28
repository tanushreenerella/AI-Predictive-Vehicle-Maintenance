"""Train and compare failure-detection models without touching production inference.

The test split is deliberately created once (seed 42) and is never used for
model selection. All selection, including the resampling decision, happens
inside stratified cross-validation on the training partition.
"""

import json
import logging
import os
from typing import Any, Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, make_scorer, precision_score, recall_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_val_predict, train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from agents.failure_prediction.features import BASE_FEATURE_COLUMNS, FAILURE_LABEL, HEALTHY_LABEL, engineer_features

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

DATA_PATH = "data/raw/engine_data.csv"
MODEL_DIR = "agents/failure_prediction"
FEATURE_COLUMNS = BASE_FEATURE_COLUMNS
TARGET_COLUMN = "engine_condition"
RANDOM_STATE = 42
CV_FOLDS = 3
SEARCH_ITERATIONS = 4


class FailureWeightedXGBClassifier(XGBClassifier):
    """Apply the higher training weight to FAILURE (class 0), not class 1.

    XGBoost's ``scale_pos_weight`` only applies to its numeric positive class
    (1), which is HEALTHY in this dataset. This wrapper keeps the labels and
    production probability-column contract unchanged while weighting failures.
    """

    def __init__(self, failure_weight: float = 1.5, **kwargs):
        self.failure_weight = failure_weight
        super().__init__(**kwargs)

    def fit(self, X, y, sample_weight=None, **kwargs):
        failure_weights = np.where(np.asarray(y) == FAILURE_LABEL, self.failure_weight, 1.0)
        if sample_weight is not None:
            failure_weights = failure_weights * np.asarray(sample_weight)
        return super().fit(X, y, sample_weight=failure_weights, **kwargs)


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
    """Retain the existing physically motivated preprocessing rule."""
    before = len(data)
    data = data[data["coolant_temp"] < 150].copy()
    if before != len(data):
        log.info("Dropped %d outlier rows (coolant_temp >= 150)", before - len(data))
    return data


def failure_metrics(y_true, y_pred) -> Dict[str, float]:
    """Metrics where class 0, not sklearn's default class 1, is positive."""
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "failure_precision": round(precision_score(y_true, y_pred, pos_label=FAILURE_LABEL, zero_division=0), 4),
        "failure_recall": round(recall_score(y_true, y_pred, pos_label=FAILURE_LABEL, zero_division=0), 4),
        "failure_f1": round(f1_score(y_true, y_pred, pos_label=FAILURE_LABEL, zero_division=0), 4),
    }


def pipeline_for(model, balancing: str) -> Pipeline:
    """Build a CV-safe pipeline: SMOTE is fit separately inside each CV fold."""
    steps = [("scaler", StandardScaler())]
    if balancing == "smote":
        steps.append(("sampler", SMOTE(random_state=RANDOM_STATE)))
    steps.append(("model", model))
    return Pipeline(steps)


def model_specs() -> Dict[str, Tuple[Any, Dict[str, list]]]:
    """Conservative search spaces favour shallower, regularized trees."""
    return {
        "random_forest": (
            RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
            {
                "model__n_estimators": [250, 400],
                "model__max_depth": [5, 8, 12],
                "model__min_samples_leaf": [3, 8, 15],
                "model__min_samples_split": [6, 16, 30],
                "model__max_features": ["sqrt", 0.7],
            },
        ),
        "xgboost": (
            XGBClassifier(random_state=RANDOM_STATE, n_jobs=-1, eval_metric="logloss", tree_method="hist"),
            {
                "model__n_estimators": [150, 250, 350], "model__max_depth": [3, 4, 5],
                "model__learning_rate": [0.02, 0.04, 0.06], "model__min_child_weight": [3, 8, 15],
                "model__subsample": [0.7, 0.85], "model__colsample_bytree": [0.7, 0.85],
                "model__reg_alpha": [0.1, 0.5, 1.0], "model__reg_lambda": [3.0, 8.0, 15.0],
            },
        ),
        "lightgbm": (
            LGBMClassifier(random_state=RANDOM_STATE, n_jobs=-1, verbosity=-1),
            {
                "model__n_estimators": [150, 250, 350], "model__learning_rate": [0.02, 0.04, 0.06],
                "model__num_leaves": [7, 15, 31], "model__max_depth": [3, 5, 7],
                "model__min_child_samples": [30, 75, 150], "model__subsample": [0.7, 0.85],
                "model__colsample_bytree": [0.7, 0.85], "model__reg_alpha": [0.1, 0.5, 1.0],
                "model__reg_lambda": [3.0, 8.0, 15.0],
            },
        ),
    }


def weighted_model(name: str):
    """Weights are an alternative to synthetic samples, never combined with SMOTE."""
    if name == "random_forest":
        return RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1, class_weight="balanced")
    if name == "xgboost":
        return FailureWeightedXGBClassifier(
            failure_weight=1.5, random_state=RANDOM_STATE, n_jobs=-1,
            eval_metric="logloss", tree_method="hist",
        )
    return LGBMClassifier(random_state=RANDOM_STATE, n_jobs=-1, verbosity=-1, class_weight={0: 1.5, 1: 1.0})


def legacy_baseline(X_train, y_train, X_test, y_test) -> Dict[str, Any]:
    """Reproduce the former SMOTE + LightGBM baseline for an honest comparison."""
    legacy = pipeline_for(
        LGBMClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.8,
                       colsample_bytree=0.8, class_weight="balanced", random_state=RANDOM_STATE, verbosity=-1),
        "smote",
    )
    legacy.fit(X_train, y_train)
    return {"model": "legacy_lightgbm_smote", "test": failure_metrics(y_test, legacy.predict(X_test)),
            "train": failure_metrics(y_train, legacy.predict(X_train))}


def tune_models(X_train, y_train):
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    scorer = make_scorer(f1_score, pos_label=FAILURE_LABEL, zero_division=0)
    results = []
    best_search = None
    for name, (base_model, params) in model_specs().items():
        for balancing in ("none", "smote", "class_weight"):
            model = weighted_model(name) if balancing == "class_weight" else base_model
            search = RandomizedSearchCV(
                pipeline_for(model, balancing), params, n_iter=SEARCH_ITERATIONS, scoring=scorer,
                cv=cv, refit=True, random_state=RANDOM_STATE, n_jobs=1, return_train_score=True,
            )
            log.info("Tuning %s (%s) with %d-fold stratified CV...", name, balancing, CV_FOLDS)
            search.fit(X_train, y_train)
            results.append({
                "model": name, "balancing": balancing,
                "cv_failure_f1_mean": round(float(search.best_score_), 4),
                "cv_failure_f1_std": round(float(search.cv_results_["std_test_score"][search.best_index_]), 4),
                "cv_train_failure_f1_mean": round(float(search.cv_results_["mean_train_score"][search.best_index_]), 4),
                "best_params": search.best_params_,
            })
            if best_search is None or search.best_score_ > best_search.best_score_:
                best_search = search
    results.sort(key=lambda item: item["cv_failure_f1_mean"], reverse=True)
    return best_search, results


def sweep_threshold(pipeline, X_train, y_train, cv, thresholds=None) -> list:
    """Find the failure-probability cutoff via out-of-fold CV predictions.

    Uses cross_val_predict so every probability was produced by a model that
    never saw that row during fitting -- the threshold is chosen honestly,
    not against training-fold leakage. Does not touch the held-out test set.
    """
    if thresholds is None:
        thresholds = np.arange(0.30, 0.71, 0.02)

    proba = cross_val_predict(pipeline, X_train, y_train, cv=cv, method="predict_proba", n_jobs=1)
    classes_sorted = np.sort(y_train.unique())
    failure_col = int(np.where(classes_sorted == FAILURE_LABEL)[0][0])
    p_failure = proba[:, failure_col]

    rows = []
    for t in thresholds:
        y_pred = np.where(p_failure >= t, FAILURE_LABEL, HEALTHY_LABEL)
        rows.append({"threshold": round(float(t), 2), **failure_metrics(y_train, y_pred)})
    rows.sort(key=lambda r: r["failure_f1"], reverse=True)
    return rows


def train_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    data = remove_outliers(load_data())
    X = engineer_features(data[FEATURE_COLUMNS])
    y = data[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)
    log.info("Class distribution: %s (label %s = FAILURE)", y.value_counts().to_dict(), FAILURE_LABEL)
    log.info("Fixed split: %d training rows / %d test rows", len(X_train), len(X_test))

    old = legacy_baseline(X_train, y_train, X_test, y_test)
    best_search, cv_results = tune_models(X_train, y_train)
    best_pipeline = best_search.best_estimator_
    new_test = failure_metrics(y_test, best_pipeline.predict(X_test))
    new_train = failure_metrics(y_train, best_pipeline.predict(X_train))
    selected = cv_results[0]

    # --- threshold sweep ---
    threshold_cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    threshold_rows = sweep_threshold(best_pipeline, X_train, y_train, threshold_cv)
    best_threshold = threshold_rows[0]["threshold"]

    classes_sorted = np.sort(y_train.unique())
    failure_col = int(np.where(classes_sorted == FAILURE_LABEL)[0][0])
    test_proba = best_pipeline.predict_proba(X_test)[:, failure_col]
    test_at_threshold = np.where(test_proba >= best_threshold, FAILURE_LABEL, HEALTHY_LABEL)
    new_test_at_best_threshold = failure_metrics(y_test, test_at_threshold)
    # --- end threshold sweep ---

    # Preserve the existing inference contract: fitted estimator plus scaler.
    joblib.dump(best_pipeline.named_steps["model"], os.path.join(MODEL_DIR, "model.joblib"))
    joblib.dump(best_pipeline.named_steps["scaler"], os.path.join(MODEL_DIR, "scaler.joblib"))
    bg_size = min(100, len(X_test))
    background = best_pipeline.named_steps["scaler"].transform(X_test.sample(n=bg_size, random_state=RANDOM_STATE))
    joblib.dump(background, os.path.join(MODEL_DIR, "shap_background.joblib"))

    old_gap = round(old["train"]["failure_f1"] - old["test"]["failure_f1"], 4)
    new_gap = round(new_train["failure_f1"] - new_test["failure_f1"], 4)
    metrics = {
        "failure_label": FAILURE_LABEL,
        "split": {"test_size": 0.2, "random_state": RANDOM_STATE, "stratified": True, "train_rows": len(X_train), "test_rows": len(X_test)},
        "selection_metric": "failure_f1 (class 0)", "old_baseline": old,
        "cross_validation": {"folds": CV_FOLDS, "results": cv_results}, "selected_model": selected,
        "new_model": {"train": new_train, "test": new_test},
        "threshold_sweep": {
            "candidates": threshold_rows,
            "recommended_threshold": best_threshold,
            "note": "chosen threshold maximizes FAILURE F1 on out-of-fold CV predictions from training data only",
        },
        "new_model_at_recommended_threshold": {"test": new_test_at_best_threshold},
        "overfitting": {"old_train_minus_test_failure_f1": old_gap, "new_train_minus_test_failure_f1": new_gap, "improved": new_gap < old_gap},
        "features": list(X.columns),
    }

    def _json_default(obj):
        if isinstance(obj, set):
            return sorted(obj)  # convert sets to lists so JSON can store them
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable: {obj!r}")

    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as file:
        json.dump(metrics, file, indent=2, default=_json_default)

    log.info("Old test metrics: %s", old["test"])
    log.info("New test metrics: %s", new_test)
    log.info("Selected %s (%s), CV failure F1 %.4f +/- %.4f", selected["model"], selected["balancing"], selected["cv_failure_f1_mean"], selected["cv_failure_f1_std"])
    log.info("Failure F1 generalization gap: old %.4f -> new %.4f (improved=%s)", old_gap, new_gap, new_gap < old_gap)
    return metrics


if __name__ == "__main__":
    train_model()