from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# User & Auth
class UserRegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "customer"  # "admin", "reviewer", "customer"
    phone: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    role: str

# Claim Submission
class ClaimCreateRequest(BaseModel):
    policy_number: str
    claimant_name: str
    claimant_email: Optional[str] = None
    claimant_phone: Optional[str] = None
    claim_type: str = "Auto Collision"
    incident_date: str
    incident_location: str
    incident_description: str
    claimed_amount: float
    currency: str = "INR"
    asset_identifier: Optional[str] = None
    repair_shop_name: Optional[str] = None
    bank_account_hash: Optional[str] = None

# Agents Output Schemas
class IntakeAgentOutput(BaseModel):
    claim_id: str
    claim_type: str
    customer_information: Dict[str, Any]
    incident_information: Dict[str, Any]
    submitted_modalities: List[str]
    missing_information: List[str]
    initial_summary: str

class DocumentIntelligenceOutput(BaseModel):
    document_id: str
    file_name: str
    doc_category: str
    extracted_fields: Dict[str, Any]
    confidence_scores: Dict[str, float]
    raw_text_preview: str

class DamageBox(BaseModel):
    box_2d: List[float] = Field(description="[ymin, xmin, ymax, xmax] normalized 0-1000 or 0-1")
    label: str
    score: float

class VisionDamageOutput(BaseModel):
    damage_detected: bool
    damage_type: List[str]
    severity: str  # low | medium | high | critical
    affected_components: List[str]
    confidence: float
    visual_evidence: List[str]
    annotated_image_url: Optional[str] = None
    bounding_boxes: List[Dict[str, Any]] = []

class PolicyCitation(BaseModel):
    source_document: str
    page_or_section: str
    clause_text: str
    coverage_applicable: bool
    deductible: float
    confidence: float

class PolicyCoverageOutput(BaseModel):
    coverage_applicable: bool
    coverage_limit: float
    deductible: float
    confidence: float
    citations: List[PolicyCitation]
    coverage_notes: str

class FraudSignalItem(BaseModel):
    signal: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float
    category: str
    details: Dict[str, Any] = {}

class FraudDetectionOutput(BaseModel):
    fraud_score: float  # 0 to 100
    risk_level: str     # LOW, MEDIUM, HIGH, CRITICAL
    signals: List[FraudSignalItem]
    recommendation: str

class SeverityOutput(BaseModel):
    damage_severity: str
    financial_severity: str
    urgency: str
    overall_severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    priority_score: float

class EstimationOutput(BaseModel):
    estimated_min: float
    estimated_max: float
    currency: str = "INR"
    confidence: float
    factors: List[str]
    breakdown: Dict[str, float]

class DecisionOutput(BaseModel):
    recommendation: str  # AUTO_APPROVE, AUTO_REJECT, REQUEST_INFORMATION, MANUAL_REVIEW, FRAUD_INVESTIGATION
    confidence: float
    reasoning_summary: str
    evidence_points: List[str]
    component_confidences: Dict[str, float]
    recommended_action: str

class ExplainabilityOutput(BaseModel):
    decision: str
    why: List[str]
    evidence: List[str]
    confidence_by_component: Dict[str, float]
    recommended_action: str

class CustomerMessageOutput(BaseModel):
    language: str
    subject: str
    message: str

# Human Review & Overrides
class HumanReviewRequest(BaseModel):
    human_decision: str  # APPROVED, REJECTED, REQUEST_INFO, ESCALATED_INVESTIGATION
    override_reason: Optional[str] = None
    reviewer_notes: Optional[str] = None

# Copilot Chat
class CopilotChatRequest(BaseModel):
    claim_id: Optional[str] = None
    query: str
    history: Optional[List[Dict[str, str]]] = []

class CopilotChatResponse(BaseModel):
    response: str
    grounded_citations: List[str] = []
    suggested_followups: List[str] = []

# What-if Decision Simulator
class SimulatorRequest(BaseModel):
    claimed_amount: float
    damage_severity: str
    fraud_score: float
    policy_limit: float
    deductible: float
    confidence: float

class SimulatorResponse(BaseModel):
    simulated_recommendation: str
    simulated_priority_score: float
    factors: List[str]
