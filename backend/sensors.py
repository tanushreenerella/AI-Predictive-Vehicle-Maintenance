from typing import Annotated, Optional

from pydantic import BaseModel, Field

from agents.failure_prediction.features import SENSOR_RANGES


def _reading(name: str):
    low, high = SENSOR_RANGES[name]
    # strict: numbers only (no "12" strings, no booleans); finite only.
    return Annotated[float, Field(strict=True, ge=low, le=high, allow_inf_nan=False)]


class SensorReadings(BaseModel):
    """All six sensors, required, within the range the model was trained on."""
    engine_rpm: _reading("engine_rpm")
    lub_oil_pressure: _reading("lub_oil_pressure")
    fuel_pressure: _reading("fuel_pressure")
    coolant_pressure: _reading("coolant_pressure")
    lub_oil_temp: _reading("lub_oil_temp")
    coolant_temp: _reading("coolant_temp")


class PredictRequest(SensorReadings):
    vehicle_id: Optional[str] = None
