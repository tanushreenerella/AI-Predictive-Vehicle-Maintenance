from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from backend.session import get_db
from backend.models.vehicle import Vehicle

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/{user_id}")
def get_alerts(user_id: str, db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == user_id).all()

    alerts = []
    alert_id = 1

    for v in vehicles:
        # 🔴 Low fuel
        if v.fuel_level < 25:
            alerts.append({
                "id": alert_id,
                "type": "warning",
                "title": "Low Fuel Level",
                "message": f"{v.name} fuel below 25%",
                "time": "Just now",
                "vehicle": v.name
            })
            alert_id += 1

        # 🟡 High mileage
        if v.mileage > 60000:
            alerts.append({
                "id": alert_id,
                "type": "info",
                "title": "High Mileage",
                "message": f"{v.name} crossed 60,000 km",
                "time": "Recently",
                "vehicle": v.name
            })
            alert_id += 1

        # 🔴 Critical condition
        if v.fuel_level < 15:
            alerts.append({
                "id": alert_id,
                "type": "critical",
                "title": "Critical Vehicle Condition",
                "message": f"{v.name} requires immediate attention",
                "time": "Just now",
                "vehicle": v.name
            })
            alert_id += 1

    return alerts
