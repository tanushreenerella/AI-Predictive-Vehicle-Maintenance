# orchestrators/run_orchestrator.py

from orchestrators.master_orchestrator import MasterOrchestrator

def run_orchestrator(vehicle_id: int, sensor_data: dict) -> dict:
    """
    Entry point used by backend services.
    """

    orchestrator = MasterOrchestrator()

    analysis_result = orchestrator.analyze(
        sensor_data=sensor_data,
        user_context=f"Vehicle ID: {vehicle_id}"
    )

    # 🔁 Normalize output for DB + frontend
    return {
        "health_update": {
            "vehicle_id": vehicle_id,
            "risk_level": analysis_result["riskLevel"],
            "failure_probability": analysis_result["failureProbability"],
            "critical_component": analysis_result["component"],
            "confidence": analysis_result["confidence"],
            "estimated_failure_window": analysis_result["estimatedFailureWindow"],
        },
        "ai_report": analysis_result["analysis"],
        "raw": analysis_result
    }
