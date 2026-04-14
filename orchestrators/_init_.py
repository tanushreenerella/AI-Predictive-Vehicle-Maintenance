"""
orchestrators/__init__.py
Orchestrators package
"""
from .master_orchestrator import (
    MasterOrchestrator,
    analyze_vehicle_data,  # ✅ Export the tool
    diagnostic_questions_tool,
    service_recommendation_tool,
    rca_analysis_tool
)

__version__ = "1.0.0"
__all__ = [
    "MasterOrchestrator",
    "analyze_vehicle_data", 
    "diagnostic_questions_tool",
    "service_recommendation_tool",
    "rca_analysis_tool"
]