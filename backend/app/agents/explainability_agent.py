from typing import Dict, Any, List
from backend.app.agents.base import BaseAgent

class ExplainabilityAgent(BaseAgent):
    def __init__(self):
        super().__init__("ExplainabilityAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Generating transparent plain-English decision explanation...")
        decision = state.get("decision_output", {})
        fraud = state.get("fraud_output", {})
        vision = state.get("vision_output", {})
        policy = state.get("policy_output", {})

        recommendation = decision.get("recommendation", "MANUAL_REVIEW")
        why_list: List[str] = []

        if recommendation == "AUTO_APPROVE":
            why_list.append("Claimed amount is within the automatic approval threshold.")
            why_list.append("Computer vision verified physical damage consistent with incident narrative.")
            why_list.append("Policy RAG check confirmed active coverage with zero exclusion conflicts.")
            why_list.append(f"Fraud risk score is low ({fraud.get('fraud_score', 0):.0f}/100) with zero duplicate signals.")
        elif recommendation == "FRAUD_INVESTIGATION":
            why_list.append(f"Elevated fraud anomaly score ({fraud.get('fraud_score', 0):.0f}/100) detected.")
            for sig in fraud.get("signals", []):
                why_list.append(f"Flagged signal: {sig.get('signal')}")
        elif recommendation == "REQUEST_INFORMATION":
            why_list.append("Essential evidence items or documentation are missing from the claim file.")
            why_list.append("Clear damage photography or incident documentation required to conclude triage.")
        else:  # MANUAL_REVIEW
            if state.get("claim_data", {}).get("claimed_amount", 0) >= 100000:
                why_list.append("High financial valuation requires human authorization.")
            if fraud.get("fraud_score", 0) >= 40:
                why_list.append("Moderate fraud signals necessitate adjuster cross-examination.")
            if decision.get("confidence", 0) < 0.85:
                why_list.append("Evidence confidence score requires human verification.")

        evidence_list = decision.get("evidence_points", [])
        if not evidence_list:
            if vision.get("visual_evidence"):
                evidence_list.extend(vision["visual_evidence"])
            if policy.get("citations"):
                evidence_list.append(f"Policy Clause: {policy['citations'][0]['page_or_section']}")

        return {
            "decision": recommendation.replace("_", " "),
            "why": why_list,
            "evidence": evidence_list,
            "confidence_by_component": decision.get("component_confidences", {}),
            "recommended_action": decision.get("recommended_action", "Proceed with standard claim review.")
        }
