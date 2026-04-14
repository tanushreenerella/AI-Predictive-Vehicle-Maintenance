from datetime import datetime
from orchestrators.run_orchestrator import run_orchestrator
def run_vehicle_ai(vehicle, sensor_data, db):
    result = run_orchestrator(
        vehicle_id=vehicle.id,
        sensor_data=sensor_data
    )

    vehicle.ai_risk_level = result["health_update"]["risk_level"]
    vehicle.ai_failure_probability = result["health_update"]["failure_probability"]
    #vehicle.ai_component = result["health_update"]["critical_component"]
    vehicle.ai_last_analyzed = datetime.utcnow()

    db.commit()

    return result
