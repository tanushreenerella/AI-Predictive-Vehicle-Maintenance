from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from backend.session import get_db
from backend.models.vehicle import Vehicle
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from agents.llm import call_llm
from backend.services.vehicle_analysis import ensure_vehicle_analysis, repair_duplicate_vehicle_analyses

router = APIRouter(prefix="/reports", tags=["Reports"])


def _rca_fallback(vehicle: Vehicle) -> dict:
    if vehicle.ai_failure_probability is None or vehicle.ai_risk_level is None:
        return {
            "root_cause": "Analysis required",
            "contributing_factors": [
                "No ML sensor analysis has been saved for this vehicle yet",
                "RCA needs vehicle-specific sensor readings before it can identify causes",
            ],
            "recommendations": [
                "Run AI Analysis for this specific vehicle using its current sensor readings",
                "Return to this RCA report after analysis completes",
            ],
            "severity": "Unknown",
            "action_timeline": "Run analysis first",
            "summary": (
                f"No vehicle-specific ML analysis exists yet for {vehicle.name}. "
                "The system will not reuse another vehicle's RCA or generate a misleading report."
            ),
            "generated_by": "rule-based",
        }

    risk = vehicle.ai_risk_level or "LOW"
    prob = vehicle.ai_failure_probability or 0
    component = vehicle.ai_component or "Engine"
    prob_pct = int(prob * 100)

    if risk == "HIGH":
        root_cause = f"Critical degradation detected in the {component} system"
        contributing = [
            "Abnormal engine RPM patterns exceeding safe thresholds",
            "Lubricant oil pressure below recommended operating range",
            "Elevated coolant temperature indicating thermal stress",
            "Fuel pressure irregularities affecting combustion efficiency",
        ]
        recommendations = [
            "Schedule immediate inspection within 1–2 days",
            f"Prioritise {component} system diagnostic and repair",
            "Avoid highway or long-distance driving until serviced",
            "Monitor engine temperature gauge closely",
            "Check oil and coolant levels before each drive",
        ]
        severity = "Critical"
        timeline = "Within 48 hours"
        summary = (
            f"The ML model detected a {prob_pct}% engine failure probability for your {vehicle.name}. "
            f"The primary affected system is {component}. Immediate professional inspection is required."
        )
    elif risk == "MEDIUM":
        root_cause = f"Progressive wear detected in the {component} system"
        contributing = [
            "Gradual deviation in sensor readings from baseline",
            "Moderate stress on mechanical components",
            "Possible delayed maintenance leading to accelerated wear",
            "Environmental factors affecting system performance",
        ]
        recommendations = [
            "Schedule a service within 5–7 days",
            f"Have the {component} system inspected and serviced",
            "Perform an oil and filter change if overdue",
            "Check tyre pressure and wheel alignment",
            "Monitor for any new symptoms (noise, vibration, heating)",
        ]
        severity = "Moderate"
        timeline = "Within 1 week"
        summary = (
            f"The ML model detected a {prob_pct}% engine failure probability for your {vehicle.name}. "
            f"The {component} system shows moderate wear. Scheduling service this week is advised."
        )
    else:
        root_cause = "No significant failure indicators detected"
        contributing = [
            "Sensor readings within normal operating parameters",
            "No abnormal wear patterns identified",
            "System health consistent with regular usage",
        ]
        recommendations = [
            "Continue with scheduled maintenance intervals",
            "Next full service as per manufacturer schedule",
            "Monitor tyre wear and tread depth",
            "Check fluid levels monthly",
        ]
        severity = "Low"
        timeline = "Routine maintenance schedule"
        summary = (
            f"Your {vehicle.name} is in good health with only {prob_pct}% engine failure probability. "
            "No immediate action required. Keep up with regular maintenance."
        )

    return {
        "root_cause": root_cause,
        "contributing_factors": contributing,
        "recommendations": recommendations,
        "severity": severity,
        "action_timeline": timeline,
        "summary": summary,
        "generated_by": "rule-based",
    }


def _rca_with_llm(vehicle: Vehicle) -> dict | None:
    if vehicle.ai_failure_probability is None or vehicle.ai_risk_level is None:
        return None

    try:
        prob_pct = int((vehicle.ai_failure_probability or 0) * 100)
        prompt = f"""You are an expert vehicle diagnostics engineer performing a Root Cause Analysis (RCA).

Vehicle: {vehicle.name} ({vehicle.model}, {vehicle.year})
Registration: {vehicle.registration_number}
Mileage: {vehicle.mileage} km
AI Risk Level: {vehicle.ai_risk_level or 'LOW'}
Engine Failure Probability: {prob_pct}%
Affected Component: {vehicle.ai_component or 'General Engine Systems'}
Last Analysed: {vehicle.ai_last_analyzed}

Produce a structured RCA report as JSON only (no markdown, no extra text):
{{
  "root_cause": "one sentence root cause",
  "contributing_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendations": ["action 1", "action 2", "action 3"],
  "severity": "Critical|Moderate|Low",
  "action_timeline": "e.g. Within 48 hours",
  "summary": "2-3 sentence plain-language summary for the vehicle owner",
  "generated_by": "llm"
}}"""

        import json, re
        raw = call_llm(prompt)
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"RCA LLM failed: {e}")
    return None


@router.get("/rca/{vehicle_id}")
def get_rca(
    vehicle_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.user_id == user.id,
    ).first()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    ensure_vehicle_analysis(vehicle, db)
    rca = _rca_with_llm(vehicle) or _rca_fallback(vehicle)

    return {
        "vehicle": {
            "id": vehicle.id,
            "name": vehicle.name,
            "model": vehicle.model,
            "year": vehicle.year,
            "registration": vehicle.registration_number,
            "mileage": vehicle.mileage,
        },
        "risk_level": vehicle.ai_risk_level or "LOW",
        "failure_probability": vehicle.ai_failure_probability or 0,
        "component": vehicle.ai_component or "Engine",
        "health": (
            max(0, min(100, round(100 - vehicle.ai_failure_probability * 100)))
            if vehicle.ai_failure_probability is not None
            else None
        ),
        "last_analyzed": vehicle.ai_last_analyzed.isoformat() if vehicle.ai_last_analyzed else None,
        "generated_at": datetime.utcnow().isoformat(),
        **rca,
    }


@router.get("/vehicles")
def get_my_vehicles_for_reports(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == user.id).all()
    repair_duplicate_vehicle_analyses(vehicles, db)
    return [
        {
            "id": v.id,
            "name": v.name,
            "model": v.model,
            "ai_risk_level": v.ai_risk_level,
            "ai_failure_probability": v.ai_failure_probability,
            "health": (
                max(0, min(100, round(100 - v.ai_failure_probability * 100)))
                if v.ai_failure_probability is not None
                else None
            ),
            "ai_last_analyzed": v.ai_last_analyzed.isoformat() if v.ai_last_analyzed else None,
        }
        for v in vehicles
    ]
