from typing import Dict, Any, List
from backend.app.agents.base import BaseAgent
from backend.app.core.config import settings

class DecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("DecisionAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Executing Decision Agent guardrails and policy triage rules...")
        claim_data = state.get("claim_data", {})
        intake = state.get("intake_output", {})
        vision = state.get("vision_output", {})
        policy = state.get("policy_output", {})
        fraud = state.get("fraud_output", {})
        severity = state.get("severity_output", {})

        claimed = claim_data.get("claimed_amount", 0.0)
        missing_info = intake.get("missing_information", [])
        coverage_applicable = policy.get("coverage_applicable", True)
        fraud_score = fraud.get("fraud_score", 0.0)
        overall_confidence = (vision.get("confidence", 0.8) + policy.get("confidence", 0.8)) / 2.0

        evidence_points: List[str] = []
        component_confidences = {
            "vision": vision.get("confidence", 0.85),
            "policy": policy.get("confidence", 0.94),
            "document": state.get("document_output", {}).get("overall_extraction_confidence", 0.90),
            "overall": round(overall_confidence, 2)
        }

        # 1. Check Missing Information
        if len(missing_info) >= 2 or "Photographic Evidence of Damage" in missing_info:
            recommendation = "REQUEST_INFORMATION"
            summary = f"Claim lacks essential verification evidence: {', '.join(missing_info)}."
            action = "Prompt claimant via portal to submit clear damage photos and incident documentation."
            evidence_points.append(f"Missing required items: {', '.join(missing_info)}")

        # 2. Check Fraud / Anomaly Guardrail
        elif fraud_score >= settings.FRAUD_FLAG_THRESHOLD or any(s.get("severity") == "CRITICAL" for s in fraud.get("signals", [])):
            recommendation = "FRAUD_INVESTIGATION"
            summary = f"High fraud risk indicators detected (Score: {fraud_score}/100). Suspicious anomalies require SIU examination."
            action = "Route dossier immediately to Special Investigation Unit (SIU) for physical audit and fraud ring inspection."
            for s in fraud.get("signals", []):
                evidence_points.append(f"Fraud Signal: {s.get('signal')}")

        # 3. Check Policy Exclusions
        elif not coverage_applicable:
            recommendation = "MANUAL_REVIEW"  # Route to human rather than blind auto-reject
            summary = "Policy analysis indicates potential exclusion or non-covered event. Human adjuster confirmation mandatory."
            action = "Review specific policy exclusion clauses with claimant before issuing adverse decision."
            evidence_points.append("Policy clause conflict identified during RAG analysis.")

        # 4. Check High Value / Low Confidence threshold
        elif claimed >= settings.HIGH_VALUE_THRESHOLD_INR:
            recommendation = "MANUAL_REVIEW"
            summary = f"Claim amount (₹{claimed:,.0f}) exceeds automatic adjudication ceiling (₹{settings.HIGH_VALUE_THRESHOLD_INR:,.0f})."
            action = "Senior adjuster review required for high-value financial authorization."
            evidence_points.append(f"High claimed amount: ₹{claimed:,.0f}")

        elif overall_confidence < settings.MIN_CONFIDENCE_AUTO_APPROVE:
            recommendation = "MANUAL_REVIEW"
            summary = f"AI aggregate confidence ({int(overall_confidence*100)}%) is below auto-approval threshold ({int(settings.MIN_CONFIDENCE_AUTO_APPROVE*100)}%)."
            action = "Secondary adjuster review recommended to verify ambiguous visual or documentary evidence."
            evidence_points.append(f"Confidence score {overall_confidence:.2f} requires human validation.")

        # 5. Low-risk, high-confidence, standard claim within policy bounds
        else:
            recommendation = "AUTO_APPROVE"
            summary = "Low-risk claim with confirmed policy coverage, consistent visual damage evidence, and absence of fraud signals."
            action = "Proceed with automated payout schedule and issue customer approval dispatch."
            evidence_points.append("All primary document and photographic checks passed with high confidence.")

        return {
            "recommendation": recommendation,
            "confidence": round(overall_confidence, 2),
            "reasoning_summary": summary,
            "evidence_points": evidence_points,
            "component_confidences": component_confidences,
            "recommended_action": action
        }
