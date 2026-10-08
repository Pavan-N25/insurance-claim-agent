from typing import Dict, Any, List
from backend.app.agents.base import BaseAgent
from backend.app.services.image_hash_service import ImageHashService

class FraudDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__("FraudDetectionAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Executing Fraud & Anomaly detection...")
        claim_data = state.get("claim_data", {})
        vision = state.get("vision_output", {})
        timeline_info = state.get("timeline_output", {})
        network_signals = state.get("network_signals", [])

        signals: List[Dict[str, Any]] = []
        fraud_score = 15.0  # Base natural risk baseline

        # 1. Check duplicate image hashes from prior claims
        current_hashes = vision.get("perceptual_hashes", [])
        historical_hashes = state.get("historical_hashes", [])

        for curr in current_hashes:
            curr_h = curr.get("hash", "")
            for hist in historical_hashes:
                hist_h = hist.get("hash", "")
                dist = ImageHashService.hamming_distance(curr_h, hist_h)
                # Hamming distance <= 5 implies identical or slightly resized duplicate photo!
                if dist <= 5 and hist.get("claim_id") != state.get("claim_id"):
                    signals.append({
                        "signal": f"Duplicate Image Detected: Image visually matches prior claim {hist.get('claim_id')} (Hamming distance {dist}).",
                        "severity": "CRITICAL",
                        "confidence": 0.96,
                        "category": "DUPLICATE_IMAGE",
                        "details": {"matched_claim_id": hist.get("claim_id"), "hamming_distance": dist}
                    })
                    fraud_score += 45.0

        # 2. Add Network Cluster signals
        for net_sig in network_signals:
            signals.append(net_sig)
            if net_sig.get("severity") == "CRITICAL":
                fraud_score += 40.0
            elif net_sig.get("severity") == "HIGH":
                fraud_score += 25.0
            else:
                fraud_score += 15.0

        # 3. Check Timeline Anomalies
        anomalies = timeline_info.get("anomalies", [])
        for anom in anomalies:
            signals.append({
                "signal": anom.get("issue", "Timeline conflict"),
                "severity": anom.get("severity", "HIGH"),
                "confidence": 0.90,
                "category": "TIMELINE_CONFLICT",
                "details": anom
            })
            if anom.get("severity") == "CRITICAL":
                fraud_score += 35.0
            else:
                fraud_score += 20.0

        # 4. Check Claim Amount Inflation
        claimed = claim_data.get("claimed_amount", 0.0)
        desc = claim_data.get("incident_description", "").lower()
        if "minor scratch" in desc and claimed > 40000:
            signals.append({
                "signal": f"Potential Invoice Inflation: Claimed ₹{claimed:,.0f} for minor cosmetic scratch.",
                "severity": "HIGH",
                "confidence": 0.88,
                "category": "INVOICE_INFLATION",
                "details": {"claimed_amount": claimed}
            })
            fraud_score += 25.0

        # Cap score between 0 and 100
        fraud_score = min(100.0, max(0.0, fraud_score))

        # Risk level classification
        if fraud_score >= 65:
            risk_level = "HIGH"
            recommendation = "MANUAL_INVESTIGATION"
        elif fraud_score >= 40:
            risk_level = "MEDIUM"
            recommendation = "SECONDARY_VERIFICATION"
        else:
            risk_level = "LOW"
            recommendation = "STANDARD_TRIAGE"

        return {
            "fraud_score": round(fraud_score, 1),
            "risk_level": risk_level,
            "signals": signals,
            "recommendation": recommendation
        }
