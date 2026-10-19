from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.core.security import get_current_user_payload, require_role

router = APIRouter(prefix="/admin", tags=["Admin Configuration"])

class ConfigUpdateRequest(BaseModel):
    fraud_flag_threshold: int = 65
    high_value_threshold_inr: float = 100000.0
    min_confidence_auto_approve: float = 0.85
    sla_critical_hours: int = 2
    sla_high_hours: int = 6
    sla_normal_hours: int = 24
    llm_provider: str = "local"

@router.get("/configs")
def get_configs(_: dict = Depends(get_current_user_payload)):
    return {
        "fraud_flag_threshold": settings.FRAUD_FLAG_THRESHOLD,
        "high_value_threshold_inr": settings.HIGH_VALUE_THRESHOLD_INR,
        "min_confidence_auto_approve": settings.MIN_CONFIDENCE_AUTO_APPROVE,
        "sla_critical_hours": settings.MAX_SLA_HOURS_CRITICAL,
        "sla_high_hours": settings.MAX_SLA_HOURS_HIGH,
        "sla_normal_hours": settings.MAX_SLA_HOURS_NORMAL,
        "llm_provider": settings.LLM_PROVIDER,
        "supported_claim_types": [
            "Auto Collision",
            "Property Water Damage",
            "Commercial Fire",
            "Theft & Burglary",
            "Third-Party Liability"
        ],
        "supported_languages": ["en", "hi", "kn"]
    }

@router.put("/configs")
def update_configs(
    req: ConfigUpdateRequest,
    _: dict = Depends(require_role(["admin"])),
):
    settings.FRAUD_FLAG_THRESHOLD = req.fraud_flag_threshold
    settings.HIGH_VALUE_THRESHOLD_INR = req.high_value_threshold_inr
    settings.MIN_CONFIDENCE_AUTO_APPROVE = req.min_confidence_auto_approve
    settings.MAX_SLA_HOURS_CRITICAL = req.sla_critical_hours
    settings.MAX_SLA_HOURS_HIGH = req.sla_high_hours
    settings.MAX_SLA_HOURS_NORMAL = req.sla_normal_hours
    settings.LLM_PROVIDER = req.llm_provider

    return {"status": "SUCCESS", "message": "Admin business configurations updated."}
