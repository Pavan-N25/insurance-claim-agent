from fastapi import APIRouter
from backend.app.schemas.pydantic_models import SimulatorRequest, SimulatorResponse
from backend.app.core.config import settings

router = APIRouter(prefix="/simulator", tags=["Decision Simulator & What-If Analysis"])

@router.post("/evaluate", response_model=SimulatorResponse)
def evaluate_what_if(req: SimulatorRequest):
    factors = []
    
    # Priority score simulation
    dmg_map = {"CRITICAL": 40.0, "HIGH": 30.0, "MEDIUM": 20.0, "LOW": 10.0}
    dmg_points = dmg_map.get(req.damage_severity.upper(), 20.0)
    fin_points = 35.0 if req.claimed_amount >= settings.HIGH_VALUE_THRESHOLD_INR else (20.0 if req.claimed_amount >= 40000 else 10.0)
    fraud_points = (req.fraud_score / 100.0) * 30.0
    sim_priority = min(100.0, dmg_points + fin_points + fraud_points + 10.0)

    # Decision rule simulation
    if req.fraud_score >= settings.FRAUD_FLAG_THRESHOLD:
        rec = "FRAUD_INVESTIGATION"
        factors.append(f"Simulated fraud score ({req.fraud_score:.0f}) exceeds threshold ({settings.FRAUD_FLAG_THRESHOLD}).")
    elif req.claimed_amount >= settings.HIGH_VALUE_THRESHOLD_INR:
        rec = "MANUAL_REVIEW"
        factors.append(f"Simulated claim amount (₹{req.claimed_amount:,.0f}) breaches high-value limit (₹{settings.HIGH_VALUE_THRESHOLD_INR:,.0f}).")
    elif req.confidence < settings.MIN_CONFIDENCE_AUTO_APPROVE:
        rec = "MANUAL_REVIEW"
        factors.append(f"Simulated confidence ({int(req.confidence*100)}%) is below auto-approval threshold ({int(settings.MIN_CONFIDENCE_AUTO_APPROVE*100)}%).")
    else:
        rec = "AUTO_APPROVE"
        factors.append("All simulated factors qualify for automated straight-through processing.")

    return SimulatorResponse(
        simulated_recommendation=rec,
        simulated_priority_score=round(sim_priority, 1),
        factors=factors
    )
