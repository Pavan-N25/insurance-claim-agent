import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal, engine, Base
from backend.app.core.security import get_password_hash
from backend.app.core.config import settings
from backend.app.models.schema import (
    User, Policy, Claim, Document, DamageAssessment,
    FraudSignal, AIDecision, HumanReview, AuditLog
)
from backend.app.services.image_hash_service import ImageHashService

def create_sample_damage_image(path: str, damage_type: str = "dent", is_duplicate: bool = False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = Image.new("RGB", (640, 480), color=(180, 190, 205) if not is_duplicate else (180, 190, 205))
    draw = ImageDraw.Draw(img)

    # Draw car silhouette / bumper outline
    draw.rectangle([80, 120, 560, 400], fill=(70, 80, 95), outline=(40, 50, 65), width=3)
    draw.ellipse([140, 360, 240, 440], fill=(30, 30, 30))
    draw.ellipse([400, 360, 500, 440], fill=(30, 30, 30))

    if damage_type == "dent":
        # Draw dent deformation in red/dark grey
        draw.polygon([(280, 200), (380, 230), (350, 310), (270, 290)], fill=(45, 45, 55), outline=(220, 50, 50), width=4)
        draw.text((100, 40), "SAMPLE DAMAGE EVIDENCE: Front Bumper Impact Deformation", fill=(20, 20, 20))
    elif damage_type == "water":
        draw.rectangle([80, 120, 560, 400], fill=(210, 215, 225), outline=(100, 110, 130), width=2)
        draw.ellipse([200, 180, 440, 340], fill=(160, 185, 205), outline=(100, 140, 175), width=4)
        draw.text((100, 40), "SAMPLE DAMAGE EVIDENCE: Residential Ceiling Water Ingress", fill=(20, 20, 20))
    else:
        draw.line([(220, 220), (380, 240)], fill=(240, 240, 240), width=3)
        draw.text((100, 40), "SAMPLE DAMAGE EVIDENCE: Minor Surface Scratch", fill=(20, 20, 20))

    img.save(path, "JPEG")
    return path

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Check if already seeded
    if db.query(User).first():
        db.close()
        return

    print("Seeding database with demo users, policies, and multimodal claims...")

    # 1. Users
    admin = User(
        email="admin@insurance.ai",
        full_name="Chief Claims Officer",
        hashed_password=get_password_hash("Admin@123"),
        role="admin",
        phone="+91 98765 43210"
    )
    reviewer = User(
        email="reviewer@insurance.ai",
        full_name="Senior Adjuster V. Menon",
        hashed_password=get_password_hash("Reviewer@123"),
        role="reviewer",
        phone="+91 98765 12345"
    )
    customer = User(
        email="customer@insurance.ai",
        full_name="Priya Sharma",
        hashed_password=get_password_hash("Customer@123"),
        role="customer",
        phone="+91 91234 56789"
    )
    db.add_all([admin, reviewer, customer])
    db.commit()

    # 2. Policies
    pol1 = Policy(
        policy_number="POL-AUTO-8821",
        holder_name="Priya Sharma",
        holder_email="customer@insurance.ai",
        policy_type="auto",
        coverage_limit=500000.0,
        deductible=5000.0,
        start_date=datetime.utcnow() - timedelta(days=120),
        end_date=datetime.utcnow() + timedelta(days=245),
        status="ACTIVE",
        terms_text="Comprehensive Auto Policy with ₹5,000 compulsory deductible."
    )
    pol2 = Policy(
        policy_number="POL-PROP-4419",
        holder_name="Rajesh Nair",
        holder_email="rajesh.nair@email.com",
        policy_type="property",
        coverage_limit=1500000.0,
        deductible=15000.0,
        start_date=datetime.utcnow() - timedelta(days=90),
        end_date=datetime.utcnow() + timedelta(days=275),
        status="ACTIVE",
        terms_text="Standard Residential Protection covering accidental water damage."
    )
    pol3 = Policy(
        policy_number="POL-AUTO-9932",
        holder_name="Amit Verma",
        holder_email="amit.verma@email.com",
        policy_type="auto",
        coverage_limit=400000.0,
        deductible=5000.0,
        start_date=datetime.utcnow() - timedelta(days=40),
        end_date=datetime.utcnow() + timedelta(days=325),
        status="ACTIVE",
        terms_text="Motor Private Comprehensive."
    )
    db.add_all([pol1, pol2, pol3])
    db.commit()

    # 3. Create Sample Claims with Evidence & Multimodal Files
    uploads_dir = os.path.abspath(settings.STORAGE_DIR)

    # Claim 1: Auto Collision (Clean, Auto-approved)
    img1_path = os.path.join(uploads_dir, "CLM-2026-1001_damage.jpg")
    create_sample_damage_image(img1_path, damage_type="dent")
    ann1_path = os.path.join(uploads_dir, "CLM-2026-1001_damage_annotated.jpg")
    boxes1 = [{"box_2d": [0.35, 0.30, 0.65, 0.65], "label": "Impact Dent", "score": 0.94}]
    ImageHashService.annotate_damage_image(img1_path, ann1_path, boxes1)
    hash1 = ImageHashService.compute_dhash(img1_path)

    claim1 = Claim(
        id="CLM-2026-1001",
        policy_number="POL-AUTO-8821",
        claimant_name="Priya Sharma",
        claimant_email="customer@insurance.ai",
        claimant_phone="+91 91234 56789",
        claim_type="Auto Collision",
        incident_date=(datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d 14:30"),
        incident_location="Outer Ring Road, Bellandur, Bengaluru",
        incident_description="Rear-ended by another vehicle at low speed while decelerating at a traffic signal. Impact damaged front bumper and grille.",
        claimed_amount=48000.0,
        currency="INR",
        status="AUTO_APPROVED",
        priority="NORMAL",
        priority_score=42.0,
        fraud_score=14.0,
        fraud_risk_level="LOW",
        ai_confidence=0.92,
        estimated_min=42000.0,
        estimated_max=54000.0,
        submitted_modalities=["text", "image", "document"],
        asset_identifier="KA-01-MJ-9921",
        repair_shop_name="Metro City Honda Care"
    )
    db.add(claim1)
    db.commit()

    doc1 = Document(
        id="DOC-1001-IMG",
        claim_id=claim1.id,
        file_name="front_bumper_damage.jpg",
        file_path=img1_path,
        file_type="image/jpeg",
        doc_category="damage_photo",
        file_size=42100,
        perceptual_hash=hash1
    )
    db.add(doc1)
    db.commit()

    db.add(DamageAssessment(
        claim_id=claim1.id,
        document_id=doc1.id,
        damage_detected=True,
        damage_types=["impact_dent", "bumper_crack"],
        severity="medium",
        affected_components=["front_bumper", "grille_assembly"],
        confidence=0.92,
        annotated_image_path=ann1_path,
        bounding_boxes=boxes1
    ))
    db.add(AIDecision(
        claim_id=claim1.id,
        recommendation="AUTO_APPROVE",
        confidence=0.92,
        reasoning_summary="Straightforward auto collision with verified photo evidence, active policy coverage, and low fraud score (14/100).",
        evidence_points=["Visual impact matches statement", "Policy Section 4.1 coverage confirmed", "No fraud flags"],
        component_confidences={"vision": 0.92, "policy": 0.95, "document": 0.90, "overall": 0.92},
        recommended_action="Execute automated payment transfer."
    ))

    # Claim 2: Suspicious Duplicate Image & Inflated Claim (Fraud Flagged)
    img2_path = os.path.join(uploads_dir, "CLM-2026-1002_damage.jpg")
    create_sample_damage_image(img2_path, damage_type="dent", is_duplicate=True)
    hash2 = ImageHashService.compute_dhash(img2_path) # Intentionally matching or near hash1!

    claim2 = Claim(
        id="CLM-2026-1002",
        policy_number="POL-AUTO-9932",
        claimant_name="Amit Verma",
        claimant_email="amit.verma@email.com",
        claimant_phone="+91 99887 76655",
        claim_type="Auto Collision",
        incident_date=(datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d 19:15"),
        incident_location="MG Road, Bengaluru",
        incident_description="Vehicle struck guardrail causing alleged major front chassis and engine frame collapse.",
        claimed_amount=165000.0,
        currency="INR",
        status="FLAGGED_INVESTIGATION",
        priority="CRITICAL",
        priority_score=88.0,
        fraud_score=78.0,
        fraud_risk_level="HIGH",
        ai_confidence=0.88,
        estimated_min=45000.0,
        estimated_max=62000.0,
        submitted_modalities=["text", "image"],
        asset_identifier="DL-03-CB-1122",
        repair_shop_name="Apex Collision Centre",
        bank_account_hash="BANK-HASH-7788"
    )
    db.add(claim2)
    db.commit()

    doc2 = Document(
        id="DOC-1002-IMG",
        claim_id=claim2.id,
        file_name="chassis_impact.jpg",
        file_path=img2_path,
        file_type="image/jpeg",
        doc_category="damage_photo",
        file_size=42100,
        perceptual_hash=hash2
    )
    db.add(doc2)
    db.commit()

    db.add(FraudSignal(
        claim_id=claim2.id,
        signal="Duplicate Image Detected: Damage photo matches visual hash of prior claim CLM-2026-1001.",
        severity="CRITICAL",
        confidence=0.96,
        category="DUPLICATE_IMAGE",
        details={"matched_claim": "CLM-2026-1001"}
    ))
    db.add(FraudSignal(
        claim_id=claim2.id,
        signal="Suspicious Invoice Inflation: Claimed ₹165,000, AI physical repair benchmark estimates ₹52,000.",
        severity="HIGH",
        confidence=0.91,
        category="INVOICE_INFLATION"
    ))
    db.add(AIDecision(
        claim_id=claim2.id,
        recommendation="FRAUD_INVESTIGATION",
        confidence=0.88,
        reasoning_summary="Critical anomaly detected: Photographic evidence is a duplicate of a previously resolved claim, accompanied by severe cost inflation.",
        evidence_points=["Perceptual dHash match with CLM-2026-1001", "Claimed amount 3.2x AI estimate"],
        component_confidences={"vision": 0.88, "fraud": 0.95, "overall": 0.88},
        recommended_action="Route dossier immediately to Special Investigation Unit (SIU)."
    ))

    # Claim 3: Property Water Damage (Manual Review)
    img3_path = os.path.join(uploads_dir, "CLM-2026-1003_damage.jpg")
    create_sample_damage_image(img3_path, damage_type="water")
    claim3 = Claim(
        id="CLM-2026-1003",
        policy_number="POL-PROP-4419",
        claimant_name="Rajesh Nair",
        claimant_email="rajesh.nair@email.com",
        claimant_phone="+91 97766 55443",
        claim_type="Property Water Damage",
        incident_date=(datetime.utcnow() - timedelta(days=5)).strftime("%Y-%m-%d 08:00"),
        incident_location="Sobha Dream Acres, Wing 4, Bengaluru",
        incident_description="Concealed pipe behind master bathroom burst while family was on weekend vacation, causing saturation to false ceiling and wooden flooring.",
        claimed_amount=85000.0,
        currency="INR",
        status="MANUAL_REVIEW",
        priority="HIGH",
        priority_score=68.0,
        fraud_score=22.0,
        fraud_risk_level="LOW",
        ai_confidence=0.86,
        estimated_min=70000.0,
        estimated_max=92000.0,
        submitted_modalities=["text", "image", "document"],
        asset_identifier="PROP-BLR-SOBHA-402"
    )
    db.add(claim3)
    db.commit()

    db.add(AIDecision(
        claim_id=claim3.id,
        recommendation="MANUAL_REVIEW",
        confidence=0.86,
        reasoning_summary="Property water damage confirmed. Deductible of ₹15,000 applies under Clause 12.3. Adjuster inspection recommended for drywall integrity.",
        evidence_points=["Water saturation verified", "Policy Clause 12.3 applies", "Estimate within 10% tolerance"],
        component_confidences={"vision": 0.85, "policy": 0.92, "overall": 0.86},
        recommended_action="Inspect plumbing contractor invoice and sign off on drywall replacement scope."
    ))

    db.commit()
    db.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
