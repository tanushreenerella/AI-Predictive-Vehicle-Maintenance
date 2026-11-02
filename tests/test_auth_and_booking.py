from backend.models.appointment import Appointment
from backend.session import SessionLocal

from conftest import ORIGIN, signup


def test_missing_token_returns_401_with_cors_headers(client):
    res = client.get("/auth/me", headers={"Origin": ORIGIN})

    assert res.status_code == 401
    assert res.json() == {"detail": "Not authenticated"}
    assert res.headers["access-control-allow-origin"] == ORIGIN
    assert res.headers["access-control-allow-credentials"] == "true"


def test_invalid_token_returns_401_with_cors_headers(client):
    res = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-real-token", "Origin": ORIGIN},
    )

    assert res.status_code == 401
    assert res.json() == {"detail": "Invalid token"}
    assert res.headers["access-control-allow-origin"] == ORIGIN


def test_error_response_omits_cors_headers_for_unknown_origin(client):
    res = client.get("/auth/me", headers={"Origin": "https://evil.example.com"})

    assert res.status_code == 401
    assert "access-control-allow-origin" not in res.headers


def test_cross_user_booking_returns_404_and_writes_nothing(client):
    owner = signup(client, "owner@example.com")
    other = signup(client, "other@example.com")

    vehicle = client.post(
        "/vehicles",
        json={"name": "Owner Car", "model": "M", "year": 2020, "registration_number": "OWN-1"},
        headers=owner,
    )
    assert vehicle.status_code == 200, vehicle.text

    res = client.post(
        "/schedule",
        json={
            "vehicle_id": vehicle.json()["id"],
            "service_type": "Inspection",
            "appointment_date": "2030-01-01",
            "appointment_time": "10:00",
            "urgency": "LOW",
        },
        headers={**other, "Origin": ORIGIN},
    )

    assert res.status_code == 404
    assert res.json() == {"detail": "Vehicle not found"}
    assert res.headers["access-control-allow-origin"] == ORIGIN
    with SessionLocal() as db:
        assert db.query(Appointment).count() == 0
