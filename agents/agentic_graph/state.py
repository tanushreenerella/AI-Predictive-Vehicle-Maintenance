from __future__ import annotations
from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
class VehicleAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    phase: str
    symptom: Optional[str]
    sensor_data: Optional[Dict[str, Any]]
    diagnostic_answers: List[Dict[str, str]]
    issue_context: Optional[Dict[str, Any]]
    recommendation: Optional[Dict[str, Any]]
    scheduling: Optional[Dict[str, Any]]
    vehicle_label: str
    failure_probability: Optional[float]
    risk_level: Optional[str]
    next_agent: str
