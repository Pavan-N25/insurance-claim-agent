from typing import Dict, Any
from backend.app.agents.base import BaseAgent
from backend.app.core.config import settings

class ClaimSeverityAgent(BaseAgent):
    def __init__(self):
        super().__init__("ClaimSeverityAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Computing claim severity and priority metrics...")
        claim_data = state.get("claim_data", {})
        vision = state.get("vision_output", {})
        fraud = state.get("fraud_output", {})

        claimed = claim_data.get("claimed_amount", 0.0)
        damage_sev = vision.get("severity", "low").upper()
        fraud_score = fraud.get("fraud_score", 0.0)

        # 1. Financial Severity
        if claimed >= settings.HIGH_VALUE_THRESHOLD_INR:
            financial_sev = "HIGH"
            fin_points = 35.0
        elif claimed >= 40000:
            financial_sev = "MEDIUM"
            fin_points = 20.0
        else:
            financial_sev = "LOW"
            fin_points = 10.0

        # 2. Damage Severity points
        damage_points_map = {"CRITICAL": 40.0, "HIGH": 30.0, "MEDIUM": 20.0, "LOW": 10.0}
        dmg_points = damage_points_map.get(damage_sev, 15.0)

        # 3. Urgency points
        urgency = "HIGH" if "emergency" in claim_data.get("incident_description", "").lower() or damage_sev == "CRITICAL" else "NORMAL"
        urgency_points = 20.0 if urgency == "HIGH" else 10.0

        # 4. Configurable Priority Score formula
        fraud_points = (fraud_score / 100.0) * 30.0
        priority_score = min(100.0, dmg_points + fin_points + fraud_points + urgency_points)

        # 5. Overall Severity
        if priority_score >= 80 or damage_sev == "CRITICAL" or financial_sev == "HIGH":
            overall_severity = "CRITICAL" if priority_score >= 85 else "HIGH"
        elif priority_score >= 50 or damage_sev == "MEDIUM":
            overall_severity = "MEDIUM"
        else:
            overall_severity = "LOW"

        return {
            "damage_severity": damage_sev,
            "financial_severity": financial_sev,
            "urgency": urgency,
            "overall_severity": overall_severity,
            "priority_score": round(priority_score, 1)
        }
