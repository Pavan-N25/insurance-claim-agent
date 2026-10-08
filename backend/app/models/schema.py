import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="reviewer")  # admin, reviewer, customer
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship("HumanReview", back_populates="reviewer")
    notifications = relationship("Notification", back_populates="user")


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    policy_number = Column(String(100), unique=True, nullable=False, index=True)
    holder_name = Column(String(255), nullable=False)
    holder_email = Column(String(255), nullable=True)
    policy_type = Column(String(50), nullable=False)  # auto, property, commercial, health
    coverage_limit = Column(Float, nullable=False)
    deductible = Column(Float, nullable=False, default=5000.0)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="ACTIVE")
    clauses = Column(JSON, nullable=True)  # List of clause descriptions/rules
    terms_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    claims = relationship("Claim", back_populates="policy")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(50), primary_key=True, index=True)  # e.g., CLM-2026-1001
    policy_number = Column(String(100), ForeignKey("policies.policy_number"), nullable=True)
    claimant_name = Column(String(255), nullable=False)
    claimant_email = Column(String(255), nullable=True)
    claimant_phone = Column(String(50), nullable=True)
    claim_type = Column(String(50), nullable=False)  # Auto Collision, Property Water Damage, etc.
    incident_date = Column(String(50), nullable=False)
    incident_location = Column(String(255), nullable=False)
    incident_description = Column(Text, nullable=False)
    claimed_amount = Column(Float, nullable=False, default=0.0)
    currency = Column(String(10), default="INR")

    # Workflow & Triage State
    status = Column(String(50), default="SUBMITTED", index=True)
    # SUBMITTED, PROCESSING, AUTO_APPROVED, MANUAL_REVIEW, FLAGGED_INVESTIGATION, REQUEST_INFO, REJECTED, APPROVED
    priority = Column(String(20), default="NORMAL")  # LOW, NORMAL, HIGH, CRITICAL
    priority_score = Column(Float, default=50.0)
    fraud_score = Column(Float, default=0.0)
    fraud_risk_level = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    ai_confidence = Column(Float, default=0.0)

    # Financial Estimates
    estimated_min = Column(Float, nullable=True)
    estimated_max = Column(Float, nullable=True)

    # Modalities & Normalized Data
    submitted_modalities = Column(JSON, default=list)  # ["text", "image", "document", "audio"]
    missing_information = Column(JSON, default=list)
    extracted_data = Column(JSON, default=dict)

    # Associated Entity Metadata for Fraud Graph
    asset_identifier = Column(String(100), nullable=True)  # VIN / Plate / Property Reg
    repair_shop_name = Column(String(255), nullable=True)
    bank_account_hash = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    policy = relationship("Policy", back_populates="claims")
    documents = relationship("Document", back_populates="claim", cascade="all, delete-orphan")
    damage_assessments = relationship("DamageAssessment", back_populates="claim", cascade="all, delete-orphan")
    fraud_signals = relationship("FraudSignal", back_populates="claim", cascade="all, delete-orphan")
    ai_decisions = relationship("AIDecision", back_populates="claim", cascade="all, delete-orphan")
    human_reviews = relationship("HumanReview", back_populates="claim", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="claim", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(50), ForeignKey("claims.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)
    doc_category = Column(String(50), default="other")  # damage_photo, police_report, invoice, audio_statement
    file_size = Column(Integer, default=0)
    perceptual_hash = Column(String(100), nullable=True, index=True)  # For duplicate image detection
    ocr_text = Column(Text, nullable=True)
    extracted_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="documents")
    damage_assessment = relationship("DamageAssessment", back_populates="document", uselist=False)


class DamageAssessment(Base):
    __tablename__ = "damage_assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(50), ForeignKey("claims.id"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)
    damage_detected = Column(Boolean, default=False)
    damage_types = Column(JSON, default=list)  # ["dent", "scratch", "broken_bumper"]
    severity = Column(String(20), default="low")  # low, medium, high, critical
    affected_components = Column(JSON, default=list)
    confidence = Column(Float, default=0.0)
    annotated_image_path = Column(String(500), nullable=True)
    bounding_boxes = Column(JSON, default=list)  # [{box_2d: [ymin, xmin, ymax, xmax], label: "dent", score: 0.92}]
    manipulation_indicators = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="damage_assessments")
    document = relationship("Document", back_populates="damage_assessment")


class FraudSignal(Base):
    __tablename__ = "fraud_signals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(50), ForeignKey("claims.id"), nullable=False, index=True)
    signal = Column(String(255), nullable=False)
    severity = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    confidence = Column(Float, default=0.8)
    category = Column(String(50), default="ANOMALY")  # DUPLICATE_IMAGE, NETWORK_CLUSTER, TIMELINE_CONFLICT, INVOICE_INFLATION
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="fraud_signals")


class AIDecision(Base):
    __tablename__ = "ai_decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(50), ForeignKey("claims.id"), nullable=False, index=True)
    recommendation = Column(String(50), nullable=False)  # AUTO_APPROVE, MANUAL_REVIEW, REQUEST_INFORMATION, FRAUD_INVESTIGATION, AUTO_REJECT
    confidence = Column(Float, default=0.0)
    reasoning_summary = Column(Text, nullable=False)
    evidence_points = Column(JSON, default=list)
    component_confidences = Column(JSON, default=dict)
    recommended_action = Column(Text, nullable=False)
    model_used = Column(String(100), default="Multi-Agent Pipeline v1.0")
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="ai_decisions")


class HumanReview(Base):
    __tablename__ = "human_reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(50), ForeignKey("claims.id"), nullable=False, index=True)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    reviewer_name = Column(String(255), nullable=False)
    human_decision = Column(String(50), nullable=False)  # APPROVED, REJECTED, REQUEST_INFO, ESCALATED_INVESTIGATION
    ai_decision_at_time = Column(String(50), nullable=True)
    override_ai = Column(Boolean, default=False)
    override_reason = Column(Text, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="human_reviews")
    reviewer = relationship("User", back_populates="reviews")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(50), ForeignKey("claims.id"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False)  # CLAIM_CREATED, OCR_COMPLETED, VISION_ANALYSIS, FRAUD_FLAGGED, AI_DECISION, HUMAN_OVERRIDE
    actor = Column(String(100), nullable=False)  # AI_AGENT, USER, SYSTEM
    actor_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="audit_logs")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    claim_id = Column(String(50), nullable=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    channel = Column(String(50), default="in_app")  # in_app, email, sms
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class AdminConfig(Base):
    __tablename__ = "admin_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(500), nullable=False)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
