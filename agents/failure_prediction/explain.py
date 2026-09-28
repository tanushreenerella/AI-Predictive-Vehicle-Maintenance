"""
SHAP-based explainability for the engine failure-prediction model.

For a given prediction, this computes the actual SHAP (SHapley Additive
exPlanations) contribution of every model feature toward the FAILURE class,
using shap.TreeExplainer against the real trained Random Forest model. Nothing
here is a static/hardcoded feature-importance table — every number is
recomputed per prediction from that prediction's own SHAP values.

Background data: TreeExplainer's interventional mode needs a reference
("background") dataset to measure each feature's marginal contribution
against. train.py saves a sample of real, held-out (non-SMOTE-synthetic)
rows to shap_background.joblib for this purpose.
"""

import os
from typing import Any, Dict, List

import numpy as np

from agents.failure_prediction.features import ALL_FEATURE_COLUMNS, FAILURE_LABEL

BACKGROUND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shap_background.joblib")

# Relative-share thresholds for impact bucketing. "Share" is this feature's
# |SHAP value| as a fraction of the TOTAL |SHAP value| across all features
# for THIS SPECIFIC prediction. The bucket is therefore derived fresh from
# the real SHAP output on every call — never a fixed per-feature ranking.
HIGH_SHARE = 0.35
MEDIUM_SHARE = 0.15


def impact_for_share(share: float) -> str:
    if share >= HIGH_SHARE:
        return "high"
    if share >= MEDIUM_SHARE:
        return "medium"
    return "low"


class FailureExplainer:
    """A shap.TreeExplainer normalized so its output always means
    "contribution toward the FAILURE class", regardless of which class
    shap's underlying API happens to orient itself to.
    """

    def __init__(self, model, background: np.ndarray, failure_col: int):
        import shap  # local import: predict.py must keep working even if shap isn't installed

        self._failure_col = failure_col
        self._explainer = shap.TreeExplainer(
            model,
            data=background,
            model_output="probability",
            feature_perturbation="interventional",
        )

        # shap's TreeExplainer, for a binary classifier, returns a single
        # array of SHAP values oriented to whichever class it treats as
        # "positive" — this is not guaranteed to be FAILURE_LABEL. Detect
        # the orientation empirically (once, here) by comparing the
        # explainer's own base value to the background's actual mean
        # predicted probability for each class, and flip the sign if needed.
        mean_proba = model.predict_proba(background).mean(axis=0)
        base = self._explainer.expected_value
        base = base[0] if isinstance(base, (list, np.ndarray)) else float(base)

        dist_to_failure = abs(base - mean_proba[failure_col])
        dist_to_other = abs(base - mean_proba[1 - failure_col])
        self._sign = 1.0 if dist_to_failure <= dist_to_other else -1.0

    def shap_values_for(self, x_scaled: np.ndarray) -> np.ndarray:
        """Return a 1D array of FAILURE-oriented SHAP values for one row of
        already-scaled, already-feature-engineered input.
        """
        raw = self._explainer.shap_values(x_scaled)
        if isinstance(raw, list):
            # Older SHAP versions return one (n_samples, n_features) array
            # per class. Pick the actual failure-class output.
            raw = raw[self._failure_col]
        raw = np.asarray(raw)
        if raw.ndim == 3:
            # Newer SHAP versions return (samples, features, classes).
            raw = raw[0, :, self._failure_col]
        elif raw.ndim == 2:
            raw = raw[0]
        if raw.ndim != 1 or raw.shape[0] != len(ALL_FEATURE_COLUMNS):
            raise ValueError(
                "Unexpected SHAP output shape "
                f"{raw.shape}; expected {len(ALL_FEATURE_COLUMNS)} feature values"
            )
        return raw * self._sign


def top_features(
    shap_values: np.ndarray,
    raw_row: Dict[str, float],
    top_n: int = 3,
) -> List[Dict[str, Any]]:
    """Rank features by |SHAP value| for one prediction and return the top N,
    each with its real input value, its real SHAP value, and an impact
    bucket derived from that value's share of this prediction's total
    SHAP magnitude.
    """
    total_abs = float(np.sum(np.abs(shap_values)))
    order = np.argsort(-np.abs(shap_values))[:top_n]

    results = []
    for idx in order:
        name = ALL_FEATURE_COLUMNS[idx]
        shap_val = float(shap_values[idx])
        share = (abs(shap_val) / total_abs) if total_abs > 0 else 0.0
        results.append(
            {
                "feature": name,
                "value": round(float(raw_row[name]), 3),
                "shap_value": round(shap_val, 4),
                "impact": impact_for_share(share),
            }
        )
    return results
