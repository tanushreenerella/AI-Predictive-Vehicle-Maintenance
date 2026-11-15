from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.services.availability import BAYS, get_free_slots
from backend.session import get_db

router = APIRouter(tags=["Scheduling"])


@router.get("/slots")
def list_free_slots(
    day: date = Query(alias="date"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Past days and Sundays simply have no free slots.
    return {"date": day.isoformat(), "bays": BAYS, "slots": get_free_slots(db, day)}
