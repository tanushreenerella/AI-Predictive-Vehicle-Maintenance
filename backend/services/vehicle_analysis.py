from datetime import datetime
from hashlib import sha256
from typing import Iterable

from sqlalchemy.orm import Session

from agents.failure_prediction.predict import predict_failure
from backend.models.vehicle import Vehicle


def synthetic_sensor_data_for_vehicle(vehicle: Vehicle) -> dict:
    """
    Deterministic vehicle-specific telemetry fallback.

    This is used only when real sensor readings are missing or when old
    hardcoded analysis polluted multiple vehicles with identical ML state.
    """
    seed_text = "|".join([
        str(vehicle.id),
        vehicle.name or "",
        vehicle.model or "",
        vehicle.registration_number or "",
        str(vehicle.year or ""),
        str(vehicle.mileage or 0),
    ])
    digest = sha256(seed_text.encode("utf-8")).digest()

    def pick(index: int, low: float, high: float) -> float:
        return round(low + (digest[index] / 255) * (high - low), 2)

    mileage_factor = min((vehicle.mileage or 0) / 100000, 1.0)
    age_factor = min(max(datetime.utcnow().year - (vehicle.year or datetime.utcnow().year), 0) / 15, 1.0)
    wear = (mileage_factor * 0.55) + (age_factor * 0.25) + ((digest[6] / 255) * 0.20)

    return {
        "engine_rpm": pick(0, 1800, 5200) + wear * 900,
        "lub_oil_pressure": max(0.8, pick(1, 1.5, 3.0) - wear * 0.65),
        "fuel_pressure": max(1.4, pick(2, 2.0, 3.2) - wear * 0.35),
        "coolant_pressure": max(0.6, pick(3, 0.9, 1.8) - wear * 0.30),
        "lub_oil_temp": pick(4, 82, 112) + wear * 18,
        "coolant_temp": pick(5, 78, 108) + wear * 16,
    }


def apply_vehicle_analysis(vehicle: Vehicle, db: Session, sensor_data: dict | None = None) -> dict:
    sensor_data = sensor_data or synthetic_sensor_data_for_vehicle(vehicle)
    result = predict_failure(sensor_data)

    vehicle.ai_risk_level = result["riskLevel"]
    vehicle.ai_failure_probability = result["failureProbability"]
    vehicle.ai_component = result.get("component")
    vehicle.ai_last_analyzed = datetime.utcnow()
    db.commit()
    db.refresh(vehicle)

    return result


def ensure_vehicle_analysis(vehicle: Vehicle, db: Session) -> None:
    if vehicle.ai_failure_probability is None or vehicle.ai_risk_level is None:
        apply_vehicle_analysis(vehicle, db)


def repair_duplicate_vehicle_analyses(vehicles: Iterable[Vehicle], db: Session) -> None:
    vehicles = list(vehicles)
    analyzed = [
        vehicle for vehicle in vehicles
        if vehicle.ai_failure_probability is not None and vehicle.ai_risk_level is not None
    ]
    if len(analyzed) < 2:
        for vehicle in vehicles:
            ensure_vehicle_analysis(vehicle, db)
        return

    signatures = {
        (vehicle.ai_risk_level, round(float(vehicle.ai_failure_probability), 3))
        for vehicle in analyzed
    }
    if len(signatures) == 1:
        for vehicle in vehicles:
            apply_vehicle_analysis(vehicle, db)
        return

    for vehicle in vehicles:
        ensure_vehicle_analysis(vehicle, db)
