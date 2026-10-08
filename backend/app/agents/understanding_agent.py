from typing import Dict, Any
from backend.app.agents.base import BaseAgent

class ClaimUnderstandingAgent(BaseAgent):
    def __init__(self):
        super().__init__("ClaimUnderstandingAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Synthesizing normalized claim representation...")
        claim_data = state.get("claim_data", {})
        intake = state.get("intake_output", {})
        docs = state.get("document_output", {})
        vision = state.get("vision_output", {})

        normalized_claim = {
            "claim_id": state.get("claim_id"),
            "claim_type": claim_data.get("claim_type", "Auto Collision"),
            "policy_number": claim_data.get("policy_number"),
            "claimant": {
                "name": claim_data.get("claimant_name"),
                "email": claim_data.get("claimant_email"),
                "phone": claim_data.get("claimant_phone")
            },
            "asset_details": {
                "identifier": claim_data.get("asset_identifier", "KA-01-MJ-9921"),
                "repair_facility": claim_data.get("repair_shop_name")
            },
            "incident": {
                "date": claim_data.get("incident_date"),
                "location": claim_data.get("incident_location"),
                "description": claim_data.get("incident_description")
            },
            "financials": {
                "claimed_amount": claim_data.get("claimed_amount", 0.0),
                "currency": claim_data.get("currency", "INR")
            },
            "evidence_summary": {
                "documents_count": len(state.get("documents", [])),
                "damage_detected": vision.get("damage_detected", False),
                "damage_severity": vision.get("severity", "low"),
                "affected_components": vision.get("affected_components", [])
            }
        }

        return {"normalized_claim": normalized_claim}
