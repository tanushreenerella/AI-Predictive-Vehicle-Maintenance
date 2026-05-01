from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.session import get_db
from backend.models.vehicle import Vehicle
from backend.models.user import User
from backend.auth.dependencies import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def _build_alerts(vehicles):
    alerts = []
    alert_id = 1

    for v in vehicles:
        # AI prediction-based alerts
        if v.ai_risk_level == "HIGH" and v.ai_failure_probability is not None:
            alerts.append({
                "id": alert_id,
                "type": "critical",
                "title": "High Failure Risk Detected",
                "message": f"{v.name}: {int(v.ai_failure_probability * 100)}% engine failure probability",
                "time": "From last ML analysis",
                "vehicle": v.name,
            })
            alert_id += 1
        elif v.ai_risk_level == "MEDIUM" and v.ai_failure_probability is not None:
            alerts.append({
                "id": alert_id,
                "type": "warning",
                "title": "Medium Failure Risk",
                "message": f"{v.name}: {int(v.ai_failure_probability * 100)}% engine failure probability",
                "time": "From last ML analysis",
                "vehicle": v.name,
            })
            alert_id += 1

        # Fuel alerts
        if v.fuel_level is not None and v.fuel_level < 15:
            alerts.append({
                "id": alert_id,
                "type": "critical",
                "title": "Critical Fuel Level",
                "message": f"{v.name} fuel critically low ({v.fuel_level}%)",
                "time": "Just now",
                "vehicle": v.name,
            })
            alert_id += 1
        elif v.fuel_level is not None and v.fuel_level < 25:
            alerts.append({
                "id": alert_id,
                "type": "warning",
                "title": "Low Fuel Level",
                "message": f"{v.name} fuel below 25% ({v.fuel_level}%)",
                "time": "Just now",
                "vehicle": v.name,
            })
            alert_id += 1

        # High mileage
        if v.mileage and v.mileage > 60000:
            alerts.append({
                "id": alert_id,
                "type": "info",
                "title": "High Mileage",
                "message": f"{v.name} exceeded 60,000 km",
                "time": "Recently",
                "vehicle": v.name,
            })
            alert_id += 1

    return alerts


@router.get("/me")
def get_alerts_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == user.id).all()
    return _build_alerts(vehicles)


@router.get("/{user_id}")
def get_alerts(user_id: str, db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == user_id).all()
    return _build_alerts(vehicles)
