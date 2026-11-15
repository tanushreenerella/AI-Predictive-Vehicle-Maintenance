"""Availability for the simulated service center.

3 bays, open Monday-Saturday, 1-hour appointments starting on the hour
from 09:00 to 17:00. A bay is taken by any appointment that is not
CANCELLED; the partial unique index on appointments enforces the same rule
in the database, so two concurrent bookings cannot share a bay.

Times are the server's local time.
"""
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models.appointment import Appointment

BAYS = 3
OPEN_WEEKDAYS = range(0, 6)  # Monday (0) .. Saturday (5)
FIRST_START_HOUR = 9
LAST_START_HOUR = 17
CANCELLED = "CANCELLED"

# Days from today in which a slot is offered, inclusive.
URGENCY_WINDOWS = {"HIGH": (1, 2), "MEDIUM": (3, 7), "LOW": (8, 14)}


class InvalidSlot(ValueError):
    """The requested time can never be booked (past, closed, off-grid). HTTP 422."""


class SlotUnavailable(Exception):
    """The time is valid but every bay is taken. HTTP 409."""


def to_http(exc: Exception) -> HTTPException:
    if isinstance(exc, InvalidSlot):
        return HTTPException(status_code=422, detail=str(exc))
    if isinstance(exc, SlotUnavailable):
        return HTTPException(status_code=409, detail=str(exc))
    raise exc


def start_times() -> List[time]:
    return [time(hour) for hour in range(FIRST_START_HOUR, LAST_START_HOUR + 1)]


def validate_slot(day: date, start: time, now: Optional[datetime] = None) -> None:
    now = now or datetime.now()
    if datetime.combine(day, start) <= now:
        raise InvalidSlot("That date and time has already passed.")
    if day.weekday() not in OPEN_WEEKDAYS:
        raise InvalidSlot("The service center is closed on Sundays.")
    if (start.minute, start.second, start.microsecond) != (0, 0, 0):
        raise InvalidSlot("Appointments start on the hour, e.g. 10:00.")
    if not FIRST_START_HOUR <= start.hour <= LAST_START_HOUR:
        raise InvalidSlot(f"Appointments start between {FIRST_START_HOUR:02d}:00 and {LAST_START_HOUR:02d}:00.")


def _active(db: Session, day: date, exclude_id: Optional[str] = None):
    query = db.query(Appointment.appointment_time, Appointment.bay).filter(
        Appointment.appointment_date == day,
        Appointment.status != CANCELLED,
    )
    if exclude_id:
        query = query.filter(Appointment.id != exclude_id)
    return query.all()


def _free_bays(taken: List[Optional[int]]) -> List[int]:
    # Rows booked before bays existed may have no bay number; they still
    # occupy capacity, so cap by count as well as by bay number.
    capacity = BAYS - len(taken)
    free = [bay for bay in range(1, BAYS + 1) if bay not in taken]
    return free[:max(capacity, 0)]


def get_free_slots(db: Session, day: date, now: Optional[datetime] = None) -> List[Dict]:
    """Future slots on `day` with at least one free bay."""
    now = now or datetime.now()
    if day.weekday() not in OPEN_WEEKDAYS:
        return []

    taken: Dict[time, List[Optional[int]]] = {}
    for start, bay in _active(db, day):
        taken.setdefault(start, []).append(bay)

    slots = []
    for start in start_times():
        if datetime.combine(day, start) <= now:
            continue
        free = _free_bays(taken.get(start, []))
        if free:
            slots.append({"date": day.isoformat(), "time": start.strftime("%H:%M"), "free_bays": len(free)})
    return slots


def _matches_preference(slot: Dict, preference: str) -> bool:
    hour = int(slot["time"][:2])
    if "morning" in preference:
        return hour < 12
    if "afternoon" in preference:
        return 12 <= hour < 16
    if "evening" in preference:
        return hour >= 16
    return True


def free_slots_for_urgency(
    db: Session, urgency: str, preference: str = "", now: Optional[datetime] = None
) -> List[Dict]:
    """Free slots inside the urgency window, earliest first. A time-of-day
    preference ("morning", "afternoon", "evening") is honoured when it can
    be; otherwise every free slot in the window is returned."""
    now = now or datetime.now()
    first, last = URGENCY_WINDOWS.get((urgency or "").upper(), URGENCY_WINDOWS["MEDIUM"])
    slots: List[Dict] = []
    for offset in range(first, last + 1):
        slots.extend(get_free_slots(db, now.date() + timedelta(days=offset), now))
    preference = (preference or "").lower()
    preferred = [s for s in slots if _matches_preference(s, preference)]
    return preferred or slots


def _assign_bay(db: Session, day: date, start: time, exclude_id: Optional[str] = None) -> int:
    taken = [bay for slot_start, bay in _active(db, day, exclude_id) if slot_start == start]
    free = _free_bays(taken)
    if not free:
        raise SlotUnavailable("That slot is fully booked. Please choose another time.")
    return free[0]


def _commit_or_unavailable(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        # Another request took the same bay between our check and commit.
        db.rollback()
        raise SlotUnavailable("That slot was just booked by someone else. Please choose another time.")


def book_slot(
    db: Session,
    *,
    user_id: str,
    vehicle_id: str,
    service_type: str,
    urgency: str,
    day: date,
    start: time,
    now: Optional[datetime] = None,
) -> Appointment:
    validate_slot(day, start, now)
    appointment = Appointment(
        user_id=user_id,
        vehicle_id=vehicle_id,
        service_type=service_type,
        appointment_date=day,
        appointment_time=start,
        urgency=urgency,
        bay=_assign_bay(db, day, start),
    )
    db.add(appointment)
    _commit_or_unavailable(db)
    db.refresh(appointment)
    return appointment


def move_slot(db: Session, appointment: Appointment, day: date, start: time, now: Optional[datetime] = None) -> Appointment:
    validate_slot(day, start, now)
    appointment.bay = _assign_bay(db, day, start, exclude_id=appointment.id)
    appointment.appointment_date = day
    appointment.appointment_time = start
    _commit_or_unavailable(db)
    db.refresh(appointment)
    return appointment
