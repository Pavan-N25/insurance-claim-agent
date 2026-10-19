import os
import uuid
import shutil
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.core.security import get_current_user_payload
from backend.app.models.schema import (
    Claim, Document, DamageAssessment, FraudSignal, AIDecision,
    HumanReview, AuditLog, Policy
)
from backend.app.schemas.pydantic_models import (
    ClaimCreateRequest, HumanReviewRequest
)
from backend.app.workflows.orchestrator import orchestrator
from backend.app.services.timeline_service import TimelineService
from backend.app.services.fraud_graph_service import FraudGraphService
from backend.app.services.image_hash_service import ImageHashService

router = APIRouter(prefix="/claims", tags=["Claims"])

@router.post("")
def create_claim(
    req: ClaimCreateRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user_payload),
):
    # Generate human-friendly ID: CLM-2026-XXXX
    short_id = f"CLM-2026-{uuid.uuid4().hex[:4].upper()}"
    
    new_claim = Claim(
        id=short_id,
        policy_number=req.policy_number,
        claimant_name=req.claimant_name,
        claimant_email=req.claimant_email,
        claimant_phone=req.claimant_phone,
        claim_type=req.claim_type,
        incident_date=req.incident_date,
        incident_location=req.incident_location,
        incident_description=req.incident_description,
        claimed_amount=req.claimed_amount,
        currency=req.currency,
        asset_identifier=req.asset_identifier,
        repair_shop_name=req.repair_shop_name,
        bank_account_hash=req.bank_account_hash,
        status="SUBMITTED",
        priority="NORMAL",
        submitted_modalities=["text"]
    )
    db.add(new_claim)

    # Add audit log
    audit = AuditLog(
        claim_id=short_id,
        event_type="CLAIM_CREATED",
        actor="CLAIMANT",
        actor_id=req.claimant_email or req.claimant_name,
        details={"claimed_amount": req.claimed_amount, "claim_type": req.claim_type}
    )
    db.add(audit)
    db.commit()
    db.refresh(new_claim)
    return new_claim

@router.get("")
def list_claims(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user_payload),
):
    query = db.query(Claim)
    if status and status != "ALL":
        query = query.filter(Claim.status == status)
    if priority and priority != "ALL":
        query = query.filter(Claim.priority == priority)
    if search:
        query = query.filter(
            (Claim.id.ilike(f"%{search}%")) |
            (Claim.claimant_name.ilike(f"%{search}%")) |
            (Claim.policy_number.ilike(f"%{search}%"))
        )
    claims = query.order_by(Claim.created_at.desc()).limit(limit).all()
    return claims

@router.get("/{claim_id}")
def get_claim(
    claim_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user_payload),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    docs = db.query(Document).filter(Document.claim_id == claim_id).all()
    damage = db.query(DamageAssessment).filter(DamageAssessment.claim_id == claim_id).all()
    signals = db.query(FraudSignal).filter(FraudSignal.claim_id == claim_id).all()
    decisions = db.query(AIDecision).filter(AIDecision.claim_id == claim_id).all()
    reviews = db.query(HumanReview).filter(HumanReview.claim_id == claim_id).all()
    audits = db.query(AuditLog).filter(AuditLog.claim_id == claim_id).order_by(AuditLog.timestamp.desc()).all()

    return {
        "claim": claim,
        "documents": docs,
        "damage_assessments": damage,
        "fraud_signals": signals,
        "ai_decisions": decisions,
        "human_reviews": reviews,
        "audit_logs": audits
    }

@router.post("/{claim_id}/documents")
async def upload_document(
    claim_id: str,
    file: UploadFile = File(...),
    doc_category: str = Form("other"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user_payload),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{claim_id}_{uuid.uuid4().hex[:6]}{file_ext}"
    target_path = os.path.join(settings.STORAGE_DIR, unique_filename)

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc_id = str(uuid.uuid4())
    p_hash = None
    if "image" in file.content_type:
        p_hash = ImageHashService.compute_dhash(target_path)

    new_doc = Document(
        id=doc_id,
        claim_id=claim_id,
        file_name=file.filename,
        file_path=target_path,
        file_type=file.content_type,
        doc_category=doc_category,
        file_size=os.path.getsize(target_path),
        perceptual_hash=p_hash
    )
    db.add(new_doc)

    # Update claim modalities
    modalities = list(claim.submitted_modalities or ["text"])
    if "image" in file.content_type and "image" not in modalities:
        modalities.append("image")
    elif "pdf" in file.content_type and "document" not in modalities:
        modalities.append("document")
    elif "audio" in file.content_type and "audio" not in modalities:
        modalities.append("audio")
    claim.submitted_modalities = modalities

    # Audit log
    audit = AuditLog(
        claim_id=claim_id,
        event_type="DOCUMENT_UPLOADED",
        actor="CLAIMANT",
        details={"file_name": file.filename, "category": doc_category}
    )
    db.add(audit)
    db.commit()
    db.refresh(new_doc)

    return new_doc

@router.post("/{claim_id}/analyze")
async def analyze_claim(
    claim_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user_payload),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim.status = "PROCESSING"
    db.commit()

    # Load documents
    docs = db.query(Document).filter(Document.claim_id == claim_id).all()
    docs_data = [
        {
            "id": d.id,
            "file_name": d.file_name,
            "file_path": d.file_path,
            "file_type": d.file_type,
            "doc_category": d.doc_category,
            "ocr_text": d.ocr_text,
            "extracted_metadata": d.extracted_metadata or {}
        }
        for d in docs
    ]

    # Gather historical perceptual hashes from other claims
    historical_docs = db.query(Document).filter(Document.claim_id != claim_id, Document.perceptual_hash.isnot(None)).all()
    hist_hashes = [{"claim_id": h.claim_id, "hash": h.perceptual_hash} for h in historical_docs]

    # Gather entity cluster signals
    net_signals = FraudGraphService.analyze_network_clusters(db, claim)

    # Reconstruct timeline
    pol = db.query(Policy).filter(Policy.policy_number == claim.policy_number).first()
    pol_start = pol.start_date if pol else None
    timeline = TimelineService.reconstruct_timeline(
        policy_start=pol_start,
        incident_date_str=claim.incident_date,
        claim_created=claim.created_at,
        documents_metadata=docs_data
    )

    # Initial state
    workflow_state = {
        "claim_id": claim.id,
        "claim_data": {
            "policy_number": claim.policy_number,
            "claimant_name": claim.claimant_name,
            "claimant_email": claim.claimant_email,
            "claimant_phone": claim.claimant_phone,
            "claim_type": claim.claim_type,
            "incident_date": claim.incident_date,
            "incident_location": claim.incident_location,
            "incident_description": claim.incident_description,
            "claimed_amount": claim.claimed_amount,
            "currency": claim.currency,
            "asset_identifier": claim.asset_identifier,
            "repair_shop_name": claim.repair_shop_name,
            "bank_account_hash": claim.bank_account_hash
        },
        "documents": docs_data,
        "historical_hashes": hist_hashes,
        "network_signals": net_signals,
        "timeline_output": timeline
    }

    # Execute workflow orchestrator with real-time websocket callback
    from backend.app.api.v1.ws import ws_manager
    async def stream_progress(step: str, pct: int, msg: str):
        await ws_manager.broadcast_step(claim.id, step, pct, msg)

    result = await orchestrator.run(workflow_state, progress_callback=stream_progress)

    # Persist Results
    vision = result.get("vision_output", {})
    if vision and vision.get("damage_detected"):
        damage = DamageAssessment(
            claim_id=claim.id,
            damage_detected=vision.get("damage_detected", True),
            damage_types=vision.get("damage_type", []),
            severity=vision.get("severity", "medium"),
            affected_components=vision.get("affected_components", []),
            confidence=vision.get("confidence", 0.9),
            annotated_image_path=vision.get("annotated_image_path"),
            bounding_boxes=vision.get("bounding_boxes", [])
        )
        db.add(damage)

    # Persist Fraud Signals
    fraud = result.get("fraud_output", {})
    claim.fraud_score = fraud.get("fraud_score", 0.0)
    claim.fraud_risk_level = fraud.get("risk_level", "LOW")
    for s in fraud.get("signals", []):
        fs = FraudSignal(
            claim_id=claim.id,
            signal=s.get("signal"),
            severity=s.get("severity", "MEDIUM"),
            confidence=s.get("confidence", 0.85),
            category=s.get("category", "ANOMALY"),
            details=s.get("details", {})
        )
        db.add(fs)

    # Persist Severity & Estimates
    sev = result.get("severity_output", {})
    claim.priority = sev.get("overall_severity", "NORMAL")
    claim.priority_score = sev.get("priority_score", 50.0)

    est = result.get("estimation_output", {})
    claim.estimated_min = est.get("estimated_min")
    claim.estimated_max = est.get("estimated_max")

    # Persist Decision
    dec = result.get("decision_output", {})
    claim.status = dec.get("recommendation", "MANUAL_REVIEW")
    claim.ai_confidence = dec.get("confidence", 0.85)

    exp = result.get("explainability_output", {})
    ai_dec = AIDecision(
        claim_id=claim.id,
        recommendation=dec.get("recommendation", "MANUAL_REVIEW"),
        confidence=dec.get("confidence", 0.85),
        reasoning_summary=dec.get("reasoning_summary", ""),
        evidence_points=exp.get("evidence", []),
        component_confidences=dec.get("component_confidences", {}),
        recommended_action=dec.get("recommended_action", "")
    )
    db.add(ai_dec)

    # Update missing information
    intake = result.get("intake_output", {})
    claim.missing_information = intake.get("missing_information", [])

    # Audit log
    audit = AuditLog(
        claim_id=claim.id,
        event_type="AI_TRIAGE_COMPLETED",
        actor="AI_AGENT",
        actor_id="ClaimWorkflowOrchestrator",
        details={
            "recommendation": claim.status,
            "fraud_score": claim.fraud_score,
            "priority": claim.priority,
            "confidence": claim.ai_confidence
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(claim)

    return {
        "status": "COMPLETED",
        "claim": claim,
        "workflow_results": result
    }

@router.get("/{claim_id}/timeline")
def get_claim_timeline(
    claim_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user_payload),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    docs = db.query(Document).filter(Document.claim_id == claim_id).all()
    docs_data = [{"doc_category": d.doc_category, "file_name": d.file_name, "extracted_metadata": d.extracted_metadata or {}} for d in docs]
    pol = db.query(Policy).filter(Policy.policy_number == claim.policy_number).first()
    pol_start = pol.start_date if pol else None

    return TimelineService.reconstruct_timeline(
        policy_start=pol_start,
        incident_date_str=claim.incident_date,
        claim_created=claim.created_at,
        documents_metadata=docs_data
    )

@router.get("/{claim_id}/similar")
def get_similar_claims(
    claim_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user_payload),
):
    """
    Returns similar historical claims with similarity %, amount, outcome, and resolution duration.
    """
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    similar = db.query(Claim).filter(
        Claim.id != claim_id,
        Claim.claim_type == claim.claim_type
    ).limit(5).all()

    results = []
    for s in similar:
        results.append({
            "claim_id": s.id,
            "claimant": s.claimant_name,
            "claim_type": s.claim_type,
            "similarity": 0.88 if s.claim_type == claim.claim_type else 0.72,
            "claimed_amount": s.claimed_amount,
            "status": s.status,
            "fraud_risk": s.fraud_risk_level,
            "resolution_days": 2 if s.status == "AUTO_APPROVED" else 5
        })

    return results

@router.post("/{claim_id}/review")
def review_claim(
    claim_id: str,
    req: HumanReviewRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_payload),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    old_status = claim.status
    is_override = (old_status != req.human_decision)
    
    if is_override and not req.override_reason:
        raise HTTPException(status_code=400, detail="Reviewer reason is mandatory when overriding AI recommendation.")

    reviewer_id = str(current_user.get("user_id", "unknown"))
    reviewer_name = current_user.get("name", "Unknown Reviewer")

    review = HumanReview(
        claim_id=claim_id,
        reviewer_id=reviewer_id,
        reviewer_name=reviewer_name,
        human_decision=req.human_decision,
        ai_decision_at_time=old_status,
        override_ai=is_override,
        override_reason=req.override_reason,
        reviewer_notes=req.reviewer_notes
    )
    db.add(review)

    claim.status = req.human_decision
    audit = AuditLog(
        claim_id=claim_id,
        event_type="HUMAN_REVIEW_SUBMITTED",
        actor="HUMAN_REVIEWER",
        actor_id=reviewer_id,
        details={
            "human_decision": req.human_decision,
            "override_ai": is_override,
            "override_reason": req.override_reason
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(claim)
    return {"status": "SUCCESS", "claim": claim, "review": review}

@router.get("/{claim_id}/report")
def generate_claim_report(
    claim_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user_payload),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    docs = db.query(Document).filter(Document.claim_id == claim_id).all()
    damage = db.query(DamageAssessment).filter(DamageAssessment.claim_id == claim_id).all()
    signals = db.query(FraudSignal).filter(FraudSignal.claim_id == claim_id).all()
    decisions = db.query(AIDecision).filter(AIDecision.claim_id == claim_id).all()
    reviews = db.query(HumanReview).filter(HumanReview.claim_id == claim_id).all()
    audits = db.query(AuditLog).filter(AuditLog.claim_id == claim_id).all()

    return {
        "report_id": f"REP-{claim_id}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "claim": {
            "id": claim.id,
            "policy_number": claim.policy_number,
            "claimant_name": claim.claimant_name,
            "claim_type": claim.claim_type,
            "incident_date": claim.incident_date,
            "incident_location": claim.incident_location,
            "incident_description": claim.incident_description,
            "claimed_amount": claim.claimed_amount,
            "status": claim.status,
            "priority": claim.priority,
            "fraud_score": claim.fraud_score,
            "ai_confidence": claim.ai_confidence,
            "estimated_payout": {
                "min": claim.estimated_min,
                "max": claim.estimated_max
            }
        },
        "evidence_summary": [
            {"file_name": d.file_name, "category": d.doc_category, "file_type": d.file_type}
            for d in docs
        ],
        "damage_assessment": [
            {"severity": d.severity, "damage_types": d.damage_types, "affected_components": d.affected_components}
            for d in damage
        ],
        "fraud_signals": [
            {"signal": s.signal, "severity": s.severity, "confidence": s.confidence}
            for s in signals
        ],
        "ai_decision": decisions[0].reasoning_summary if decisions else "Pending AI Evaluation",
        "human_reviews": [
            {"reviewer": r.reviewer_name, "decision": r.human_decision, "notes": r.reviewer_notes}
            for r in reviews
        ],
        "audit_trail_count": len(audits)
    }

@router.post("/synthetic")
def create_synthetic_claim(
    scenario: str = Query("normal", description="normal | duplicate_fraud | fire_high_value | minor_scratch_auto"),
    db: Session = Depends(get_db)
):
    from backend.app.services.synthetic_generator import SyntheticClaimGenerator
    claim = SyntheticClaimGenerator.generate_synthetic_claim(db, scenario=scenario)
    return {
        "status": "SUCCESS",
        "scenario": scenario,
        "claim": claim
    }
