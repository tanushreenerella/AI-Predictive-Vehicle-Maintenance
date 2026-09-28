from __future__ import annotations
from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class MLResult(TypedDict, total=False):
    """The complete, structured output of the Random Forest + SHAP prediction
    pipeline (agents/failure_prediction/predict.py), normalized for
    LangGraph state. See build_ml_result() below — that function is the
    ONLY place a predict_failure() response gets translated into this
    shape, so every caller (sensor_node, the /predict route) produces an
    identical structure.
    """
    failure_probability: Optional[float]
    risk_level: str
    top_features: List[Dict[str, Any]]
    sensor_values: Dict[str, float]
    component: Optional[str]
    model_status: Optional[str]
    error: bool
    message: Optional[str]


class VehicleAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    phase: str
    symptom: Optional[str]
    sensor_data: Optional[Dict[str, Any]]
    diagnostic_answers: List[Dict[str, str]]
    diagnostic_question_index: int
    issue_context: Optional[Dict[str, Any]]
    recommendation: Optional[Dict[str, Any]]
    scheduling: Optional[Dict[str, Any]]
    vehicle_label: str
    failure_probability: Optional[float]
    risk_level: Optional[str]
    ml_result: Optional[MLResult]
    next_agent: str


def build_ml_result(raw: Dict[str, Any]) -> MLResult:
    """Normalize predict_failure()'s raw (camelCase) output into the
    snake_case MLResult shape LangGraph state stores. This is the single
    source of truth for that translation — sensor_node and the /predict
    route both call this, so they can never report ml_result differently.

    Nothing here invents a value: every field is read straight from the
    real model/SHAP output, or from predict_failure()'s own honest error
    contract (error=True, riskLevel="ERROR", failureProbability=None).
    """
    return {
        "failure_probability": raw.get("failureProbability"),
        "risk_level": raw.get("riskLevel") or "ERROR",
        "top_features": raw.get("top_features", []),
        "sensor_values": raw.get("input_features", {}),
        "component": raw.get("component"),
        "model_status": raw.get("model_status"),
        "error": bool(raw.get("error", False)),
        "message": raw.get("message"),
    }
