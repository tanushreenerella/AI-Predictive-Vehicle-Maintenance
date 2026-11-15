import pytest

from agents.failure_prediction.features import SENSOR_RANGES
from backend.models.vehicle import Vehicle
from backend.session import SessionLocal

from conftest import add_vehicle, signup

VALID = {
    "engine_rpm": 746, "lub_oil_pressure": 3.16, "fuel_pressure": 6.2,
    "coolant_pressure": 2.17, "lub_oil_temp": 76.8, "coolant_temp": 78.4,
}
ENDPOINTS = ["/predict", "/predict_flex"]


def with_(**overrides):
    return {**VALID, **overrides}


def without(field):
    return {k: v for k, v in VALID.items() if k != field}


BAD_BODIES = [
    pytest.param(with_(engine_rpm="abc"), "engine_rpm", id="non-numeric string"),
    pytest.param(with_(engine_rpm="746"), "engine_rpm", id="numeric string"),
    pytest.param(with_(coolant_temp=True), "coolant_temp", id="boolean"),
    pytest.param(with_(fuel_pressure=None), "fuel_pressure", id="null"),
    pytest.param(without("lub_oil_temp"), "lub_oil_temp", id="missing (no default)"),
    pytest.param(with_(engine_rpm=3000), "engine_rpm", id="above training max"),
    pytest.param(with_(lub_oil_temp=90), "lub_oil_temp", id="old default 90C above max"),
    pytest.param(with_(coolant_temp=-9999), "coolant_temp", id="below training min"),
    pytest.param(with_(lub_oil_pressure=0), "lub_oil_pressure", id="zero below min"),
]


@pytest.mark.parametrize("path", ENDPOINTS)
@pytest.mark.parametrize("body, bad_field", BAD_BODIES)
def test_bad_sensor_values_return_422(client, path, body, bad_field):
    res = client.post(path, json=body)

    assert res.status_code == 422
    assert any(err["loc"][-1] == bad_field for err in res.json()["detail"])


@pytest.mark.parametrize("path", ENDPOINTS)
def test_valid_readings_are_predicted(client, path):
    res = client.post(path, json=VALID)

    assert res.status_code == 200, res.text
    body = res.json()
    assert 0 <= body["failureProbability"] <= 1
    assert body["riskLevel"] in {"LOW", "MEDIUM", "HIGH"}
    assert body["input_features"] == {k: float(v) for k, v in VALID.items()}


@pytest.mark.parametrize("path", ENDPOINTS)
def test_range_bounds_are_inclusive(client, path):
    low = {k: lo for k, (lo, hi) in SENSOR_RANGES.items()}
    high = {k: hi for k, (lo, hi) in SENSOR_RANGES.items()}

    assert client.post(path, json=low).status_code == 200
    assert client.post(path, json=high).status_code == 200


def test_rejected_reading_does_not_touch_vehicle(client):
    headers = signup(client, "owner@example.com")
    vid = add_vehicle(client, headers)

    res = client.post("/predict", json={**with_(engine_rpm=5000), "vehicle_id": vid}, headers=headers)

    assert res.status_code == 422
    with SessionLocal() as db:
        assert db.get(Vehicle, vid).ai_last_analyzed is None


def test_vehicle_run_uses_same_validation(client):
    headers = signup(client, "owner@example.com")
    vid = add_vehicle(client, headers)

    assert client.post(f"/vehicles/run/{vid}", json=with_(engine_rpm="abc"), headers=headers).status_code == 422
    assert client.post(f"/vehicles/run/{vid}", json=VALID, headers=headers).status_code == 200
