from datetime import date, time, timedelta

import pytest

from agents.chat_agent import make_tools
from backend.models.appointment import Appointment
from backend.models.user import User
from backend.models.vehicle import Vehicle
from backend.routes import agent_chat
from backend.services import availability
from backend.services.availability import BAYS, book_slot, free_slots_for_urgency, start_times
from backend.session import SessionLocal

from conftest import add_vehicle, signup, user_id


def open_day(min_offset: int = 3) -> date:
    day = date.today() + timedelta(days=min_offset)
    while day.weekday() == 6:
        day += timedelta(days=1)
    return day


def next_sunday() -> date:
    day = date.today() + timedelta(days=1)
    while day.weekday() != 6:
        day += timedelta(days=1)
    return day


@pytest.fixture
def owner(client):
    headers = signup(client, "owner@example.com")
    return {"headers": headers, "user_id": user_id(client, headers), "vehicle_id": add_vehicle(client, headers)}


def book(client, owner, day, at="10:00"):
    return client.post(
        "/schedule",
        json={"vehicle_id": owner["vehicle_id"], "service_type": "Inspection",
              "appointment_date": day.isoformat(), "appointment_time": at, "urgency": "LOW"},
        headers=owner["headers"],
    )


def active_count(day, at):
    with SessionLocal() as db:
        return db.query(Appointment).filter(
            Appointment.appointment_date == day,
            Appointment.appointment_time == time.fromisoformat(at),
            Appointment.status != "CANCELLED",
        ).count()


# ── validation → 422 ─────────────────────────────────────────────────────────

def test_past_date_returns_422(client, owner):
    res = book(client, owner, date.today() - timedelta(days=1))

    assert res.status_code == 422
    assert "already passed" in res.json()["detail"]


def test_sunday_returns_422(client, owner):
    res = book(client, owner, next_sunday())

    assert res.status_code == 422
    assert "closed on Sundays" in res.json()["detail"]


@pytest.mark.parametrize("at, reason", [
    ("10:30", "on the hour"),
    ("08:00", "between 09:00 and 17:00"),
    ("18:00", "between 09:00 and 17:00"),
])
def test_off_grid_time_returns_422(client, owner, at, reason):
    res = book(client, owner, open_day(), at)

    assert res.status_code == 422
    assert reason in res.json()["detail"]
    assert active_count(open_day(), at) == 0


@pytest.mark.parametrize("field, value", [
    ("appointment_date", "not-a-date"),
    ("appointment_time", "25:00"),
    ("urgency", "SOON"),
])
def test_malformed_booking_body_returns_422(client, owner, field, value):
    body = {"vehicle_id": owner["vehicle_id"], "service_type": "Inspection",
            "appointment_date": open_day().isoformat(), "appointment_time": "10:00", "urgency": "LOW", field: value}

    assert client.post("/schedule", json=body, headers=owner["headers"]).status_code == 422


# ── capacity → 409 ───────────────────────────────────────────────────────────

def test_double_booking_fills_three_bays_then_409(client, owner):
    day = open_day()
    bays = []
    for _ in range(BAYS):
        res = book(client, owner, day)
        assert res.status_code == 200, res.text
        bays.append(res.json()["bay"])

    assert bays == [1, 2, 3]
    full = book(client, owner, day)
    assert full.status_code == 409
    assert "fully booked" in full.json()["detail"]
    assert active_count(day, "10:00") == BAYS


def test_cancelled_slot_can_be_booked_again(client, owner):
    day = open_day()
    ids = [book(client, owner, day).json()["appointment_id"] for _ in range(BAYS)]
    assert book(client, owner, day).status_code == 409

    assert client.delete(f"/schedule/{ids[1]}", headers=owner["headers"]).status_code == 200

    res = book(client, owner, day)
    assert res.status_code == 200
    assert res.json()["bay"] == 2


def test_status_cancelled_row_does_not_hold_its_bay(client, owner):
    # The partial unique index must allow a new booking in a bay whose
    # previous booking is marked CANCELLED (not deleted).
    day = open_day()
    first = book(client, owner, day).json()
    with SessionLocal() as db:
        db.query(Appointment).filter(Appointment.id == first["appointment_id"]).update({"status": "CANCELLED"})
        db.commit()

    res = book(client, owner, day)
    assert res.status_code == 200
    assert res.json()["bay"] == first["bay"]


def test_concurrent_booking_race_returns_409(client, owner, monkeypatch):
    # Simulate two requests that both saw bay 1 free: the second insert hits
    # the unique index, which must surface as 409, not 500.
    day = open_day()
    monkeypatch.setattr(availability, "_free_bays", lambda taken: [1])
    assert book(client, owner, day).status_code == 200

    res = book(client, owner, day)

    assert res.status_code == 409
    assert "just booked" in res.json()["detail"]
    assert active_count(day, "10:00") == 1


def test_reschedule_is_validated_and_capacity_checked(client, owner):
    day = open_day()
    for _ in range(BAYS):
        assert book(client, owner, day, "11:00").status_code == 200
    mine = book(client, owner, day, "12:00").json()["appointment_id"]
    url = f"/schedule/{mine}"

    full = client.patch(url, json={"appointment_date": day.isoformat(), "appointment_time": "11:00"}, headers=owner["headers"])
    sunday = client.patch(url, json={"appointment_date": next_sunday().isoformat(), "appointment_time": "11:00"}, headers=owner["headers"])
    ok = client.patch(url, json={"appointment_date": day.isoformat(), "appointment_time": "13:00"}, headers=owner["headers"])

    assert full.status_code == 409
    assert sunday.status_code == 422
    assert ok.status_code == 200
    assert ok.json()["bay"] == 1


# ── GET /slots ───────────────────────────────────────────────────────────────

def test_slots_requires_auth(client):
    assert client.get("/slots", params={"date": open_day().isoformat()}).status_code == 401


def test_slots_lists_free_capacity(client, owner):
    day = open_day()
    for _ in range(BAYS):
        book(client, owner, day, "09:00")
    book(client, owner, day, "10:00")

    res = client.get("/slots", params={"date": day.isoformat()}, headers=owner["headers"])

    assert res.status_code == 200
    slots = {s["time"]: s["free_bays"] for s in res.json()["slots"]}
    assert "09:00" not in slots
    assert slots["10:00"] == 2
    assert slots["17:00"] == 3
    assert len(slots) == len(start_times()) - 1


@pytest.mark.parametrize("day", [next_sunday(), date.today() - timedelta(days=1)])
def test_slots_empty_for_sunday_and_past(client, owner, day):
    res = client.get("/slots", params={"date": day.isoformat()}, headers=owner["headers"])

    assert res.status_code == 200
    assert res.json()["slots"] == []


def test_slots_bad_date_returns_422(client, owner):
    assert client.get("/slots", params={"date": "tomorrow"}, headers=owner["headers"]).status_code == 422


# ── agent ────────────────────────────────────────────────────────────────────

def _fill(owner, day, at):
    with SessionLocal() as db:
        for _ in range(BAYS):
            book_slot(db, user_id=owner["user_id"], vehicle_id=owner["vehicle_id"], service_type="Fill",
                      urgency="HIGH", day=day, start=time.fromisoformat(at))


def _agent_tools(rec, slot_prior=None, book_fn=None, confirm_booking=False):
    ctx = {"recommendation": rec, "rec_prior": rec, "slot_prior": slot_prior, "scheduling": slot_prior,
           "appointment": None, "executed": None, "called": [], "dq": 0, "show_rec": False, "show_slot": False,
           "confirm_booking": confirm_booking, "needs_confirm": False}
    tools = {t.name: t for t in make_tools(ctx, {}, book_fn or (lambda rec, sched: {}))}
    return ctx, tools


def test_agent_proposes_first_free_slot_in_urgency_window(owner):
    with SessionLocal() as db:
        earliest = free_slots_for_urgency(db, "HIGH")[0]
    _fill(owner, date.fromisoformat(earliest["date"]), earliest["time"])  # take it away

    ctx, tools = _agent_tools({"urgency": "HIGH", "recommended_service": "Brake check"})
    proposal = tools["propose_appointment_slot"].invoke({"time_preference": ""})

    with SessionLocal() as db:
        free_now = free_slots_for_urgency(db, "HIGH")
    selected = proposal["selected_slot"]
    assert selected == {"date": free_now[0]["date"], "time": free_now[0]["time"]}
    assert selected != {"date": earliest["date"], "time": earliest["time"]}
    assert 1 <= (date.fromisoformat(selected["date"]) - date.today()).days <= 2
    assert all({"date": s["date"], "time": s["time"]} in [{"date": f["date"], "time": f["time"]} for f in free_now]
               for s in proposal["suggested_slots"])
    assert ctx["scheduling"] is proposal


@pytest.mark.parametrize("urgency, window", [("MEDIUM", (3, 7)), ("LOW", (8, 14))])
def test_agent_slot_respects_window(owner, urgency, window):
    _, tools = _agent_tools({"urgency": urgency})
    selected = tools["propose_appointment_slot"].invoke({"time_preference": "afternoon"})["selected_slot"]

    assert window[0] <= (date.fromisoformat(selected["date"]) - date.today()).days <= window[1]
    assert 12 <= int(selected["time"][:2]) < 16


def test_agent_reports_error_when_window_is_full(owner):
    first, last = availability.URGENCY_WINDOWS["HIGH"]
    for offset in range(first, last + 1):
        day = date.today() + timedelta(days=offset)
        if day.weekday() != 6:
            for start in start_times():
                _fill(owner, day, start.strftime("%H:%M"))

    ctx, tools = _agent_tools({"urgency": "HIGH"})
    result = tools["propose_appointment_slot"].invoke({"time_preference": ""})

    assert "No free slots" in result["error"]
    assert ctx["scheduling"] is None


def test_agent_booking_of_a_slot_that_filled_up_returns_error(owner):
    with SessionLocal() as db:
        slot = free_slots_for_urgency(db, "HIGH")[0]
    proposed = {"selected_slot": {"date": slot["date"], "time": slot["time"]}, "service_type": "Brake check"}
    _fill(owner, date.fromisoformat(slot["date"]), slot["time"])

    def book_fn(rec, sched):
        with SessionLocal() as db:
            user = db.get(User, owner["user_id"])
            vehicle = db.get(Vehicle, owner["vehicle_id"])
            return agent_chat._book_from_agent_state(db, user, vehicle, {"recommendation": rec, "scheduling": sched})

    # The user pressed Confirm booking; the booking still fails because the slot is full.
    ctx, tools = _agent_tools({"urgency": "HIGH"}, slot_prior=proposed, book_fn=book_fn, confirm_booking=True)
    result = tools["book_appointment"].invoke({"user_confirmed": True})

    assert "fully booked" in result["error"]
    assert ctx["appointment"] is None
    assert ctx["scheduling"] is None  # so the next turn proposes a fresh slot


# ── /schedule-agentic never trusts LLM or client slots ───────────────────────

@pytest.fixture
def lying_scheduler(monkeypatch):
    def fake(**kwargs):
        # An LLM that invents a Sunday 03:00 slot.
        bogus = {"date": next_sunday().isoformat(), "time": "03:00", "label": "made up"}
        return {"recommended_urgency": "MEDIUM", "service_type": "Oil Change", "reason": "test",
                "suggested_slots": [bogus], "selected_slot": bogus, "reply": "Booked Sunday 3am!"}

    monkeypatch.setattr(agent_chat, "agentic_scheduling_agent", fake)


def test_schedule_agentic_offers_only_real_free_slots(client, owner, lying_scheduler):
    res = client.post("/schedule-agentic", json={"vehicle_id": owner["vehicle_id"], "message": ""}, headers=owner["headers"])

    assert res.status_code == 200
    scheduling = res.json()["scheduling"]
    with SessionLocal() as db:
        expected = free_slots_for_urgency(db, "MEDIUM")[0]
    assert scheduling["selected_slot"] == expected
    assert all(s["time"] != "03:00" for s in scheduling["suggested_slots"])


def _confirm(client, owner, day, at):
    state = {"scheduling": {"selected_slot": {"date": day.isoformat(), "time": at}}}
    return client.post("/schedule-agentic", json={"vehicle_id": owner["vehicle_id"], "confirm": True, "state": state},
                       headers=owner["headers"])


def test_schedule_agentic_rechecks_client_slot(client, owner, lying_scheduler):
    assert _confirm(client, owner, next_sunday(), "10:00").status_code == 422
    assert _confirm(client, owner, date.today() - timedelta(days=1), "10:00").status_code == 422
    assert _confirm(client, owner, open_day(), "10:45").status_code == 422

    day = open_day()
    for _ in range(BAYS):
        assert _confirm(client, owner, day, "15:00").status_code == 200
    full = _confirm(client, owner, day, "15:00")
    assert full.status_code == 409
    assert active_count(day, "15:00") == BAYS
