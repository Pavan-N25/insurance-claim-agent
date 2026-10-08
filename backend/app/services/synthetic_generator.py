import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.models.schema import Claim, Document, DamageAssessment, FraudSignal, AIDecision
from backend.app.services.image_hash_service import ImageHashService

class SyntheticClaimGenerator:
    """
    Developer & Demo utility to generate realistic synthetic multimodal claims
    covering normal, suspicious, duplicate, high-value, and fraud-ring scenarios.
    """
    @staticmethod
    def generate_synthetic_claim(
        db: Session,
        scenario: str = "normal"
    ) -> Claim:
        short_id = f"CLM-SYN-{uuid.uuid4().hex[:4].upper()}"

        if scenario == "duplicate_fraud":
            claim = Claim(
                id=short_id,
                policy_number="POL-AUTO-9932",
                claimant_name="Karan Malhotra",
                claimant_email="karan.m@demo.com",
                claimant_phone="+91 99112 23344",
                claim_type="Auto Collision",
                incident_date=(datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d 21:00"),
                incident_location="Outer Ring Road, Bengaluru",
                incident_description="Struck concrete median divider during evening commute. Severe front structural damage.",
                claimed_amount=175000.0,
                currency="INR",
                status="FLAGGED_INVESTIGATION",
                priority="CRITICAL",
                priority_score=85.0,
                fraud_score=82.0,
                fraud_risk_level="HIGH",
                ai_confidence=0.89,
                estimated_min=48000.0,
                estimated_max=64000.0,
                submitted_modalities=["text", "image"],
                asset_identifier="KA-04-NB-4411",
                repair_shop_name="Apex Collision Centre",
                bank_account_hash="BANK-HASH-7788"
            )
            db.add(claim)
            db.commit()

            # Add fraud signals
            db.add(FraudSignal(
                claim_id=claim.id,
                signal="Duplicate Damage Photo Detected: Perceptual dHash matches prior claim CLM-2026-1001.",
                severity="CRITICAL",
                confidence=0.96,
                category="DUPLICATE_IMAGE"
            ))
            db.add(FraudSignal(
                claim_id=claim.id,
                signal="Syndicate Payout Risk: Shared bank account hash registered across unrelated claimants.",
                severity="CRITICAL",
                confidence=0.98,
                category="ACCOUNT_SHARING"
            ))

        elif scenario == "fire_high_value":
            claim = Claim(
                id=short_id,
                policy_number="POL-FIRE-1022",
                claimant_name="Vikram Apex Logistics",
                claimant_email="claims@apexlogistics.com",
                claim_type="Commercial Fire",
                incident_date=(datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d 03:30"),
                incident_location="Peenya Industrial Area, Phase II, Bengaluru",
                incident_description="Electrical short circuit in logistics warehouse causing extensive thermal charring and structural roof collapse.",
                claimed_amount=2450000.0,
                currency="INR",
                status="MANUAL_REVIEW",
                priority="CRITICAL",
                priority_score=92.0,
                fraud_score=20.0,
                fraud_risk_level="LOW",
                ai_confidence=0.94,
                estimated_min=2100000.0,
                estimated_max=2600000.0,
                submitted_modalities=["text", "image", "document"],
                asset_identifier="FAC-PNY-BLR-09"
            )
            db.add(claim)
            db.commit()

        elif scenario == "minor_scratch_auto":
            claim = Claim(
                id=short_id,
                policy_number="POL-AUTO-8821",
                claimant_name="Sneha Rao",
                claimant_email="sneha.rao@demo.com",
                claim_type="Auto Collision",
                incident_date=(datetime.utcnow() - timedelta(hours=12)).strftime("%Y-%m-%d 09:15"),
                incident_location="HSR Layout Sector 2, Bengaluru",
                incident_description="Minor superficial paint scratch on rear bumper while reversing out of parking slot.",
                claimed_amount=12000.0,
                currency="INR",
                status="AUTO_APPROVED",
                priority="LOW",
                priority_score=25.0,
                fraud_score=8.0,
                fraud_risk_level="LOW",
                ai_confidence=0.95,
                estimated_min=10000.0,
                estimated_max=13500.0,
                submitted_modalities=["text", "image"],
                asset_identifier="KA-05-AA-1029"
            )
            db.add(claim)
            db.commit()

        else: # Standard normal collision
            claim = Claim(
                id=short_id,
                policy_number="POL-AUTO-8821",
                claimant_name="Rohan Gupta",
                claimant_email="rohan.gupta@demo.com",
                claim_type="Auto Collision",
                incident_date=(datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d 11:30"),
                incident_location="Koramangala 80ft Road, Bengaluru",
                incident_description="Low-speed rear fender impact with another vehicle during stop-and-go morning traffic.",
                claimed_amount=38000.0,
                currency="INR",
                status="AUTO_APPROVED",
                priority="NORMAL",
                priority_score=38.0,
                fraud_score=12.0,
                fraud_risk_level="LOW",
                ai_confidence=0.93,
                estimated_min=34000.0,
                estimated_max=42000.0,
                submitted_modalities=["text", "image", "document"],
                asset_identifier="KA-03-MG-7821"
            )
            db.add(claim)
            db.commit()

        db.commit()
        db.refresh(claim)
        return claim
