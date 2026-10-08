from typing import Dict, Any, List
from backend.app.agents.base import BaseAgent

class ClaimEstimationAgent(BaseAgent):
    def __init__(self):
        super().__init__("ClaimEstimationAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Estimating claim payout range and repair valuation...")
        claim_data = state.get("claim_data", {})
        vision = state.get("vision_output", {})
        policy = state.get("policy_output", {})

        claimed = claim_data.get("claimed_amount", 50000.0)
        deductible = policy.get("deductible", 5000.0)
        affected_comps = vision.get("affected_components", ["bumper"])
        severity = vision.get("severity", "medium")

        # Baseline part & labor calculations
        base_parts = claimed * 0.60
        base_labor = claimed * 0.35
        # Standard 10% parts depreciation
        depreciated_parts = base_parts * 0.90
        net_reimbursable = max(0.0, (depreciated_parts + base_labor) - deductible)

        variance_factor = 0.15 if severity == "medium" else 0.20
        est_min = round(max(0.0, net_reimbursable * (1.0 - variance_factor)), -2)
        est_max = round(net_reimbursable * (1.0 + variance_factor), -2)

        factors: List[str] = [
            f"Evaluated {len(affected_comps)} damaged component(s): {', '.join(affected_comps)}.",
            f"Compulsory policy deductible of ₹{deductible:,.0f} applied.",
            "10% depreciation rate deducted for metallic/plastic assemblies.",
            "State GST @ 18% included on labor costs."
        ]

        breakdown = {
            "estimated_parts": round(depreciated_parts, 2),
            "estimated_labor": round(base_labor, 2),
            "deductible_applied": deductible,
            "net_payable_midpoint": round((est_min + est_max) / 2.0, 2)
        }

        return {
            "estimated_min": est_min,
            "estimated_max": est_max,
            "currency": claim_data.get("currency", "INR"),
            "confidence": 0.88,
            "factors": factors,
            "breakdown": breakdown
        }
