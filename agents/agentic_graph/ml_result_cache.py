"""
Process-local, in-memory cache of the most recent full ML prediction result
per vehicle.

Bridges the /predict HTTP route's output (Random Forest + SHAP — see
agents/failure_prediction/predict.py) into LangGraph's initial conversation
state for /chat, so a chat session for a vehicle that already has a real
prediction doesn't start with sensor_data/risk_level as None. This avoids
requiring a database migration or a frontend change, both out of scope for
this step.

Not persisted: a process restart clears it — the same tradeoff already made
by the existing _CONVERSATIONS cache in backend/routes/agent_chat.py.
"""

import threading
from typing import Any, Dict, Optional

_lock = threading.Lock()
_STORE: Dict[str, Dict[str, Any]] = {}


def set_cached_ml_result(vehicle_id: str, sensor_data: Dict[str, Any], ml_result: Dict[str, Any]) -> None:
    if not vehicle_id:
        return
    with _lock:
        _STORE[str(vehicle_id)] = {"sensor_data": dict(sensor_data), "ml_result": dict(ml_result)}


def get_cached_ml_result(vehicle_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not vehicle_id:
        return None
    with _lock:
        entry = _STORE.get(str(vehicle_id))
        return {"sensor_data": dict(entry["sensor_data"]), "ml_result": dict(entry["ml_result"])} if entry else None
