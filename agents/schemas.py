from typing import TypedDict, Literal

class SchedulingDecision(TypedDict):
    recommended_urgency: Literal["LOW", "MEDIUM", "HIGH"]
    suggested_window_days: int
    confidence: float
    reasoning: str
