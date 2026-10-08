export interface Claim {
  id: string;
  policy_number: string;
  claimant_name: string;
  claimant_email?: string;
  claimant_phone?: string;
  claim_type: string;
  incident_date: string;
  incident_location: string;
  incident_description: string;
  claimed_amount: number;
  currency: string;
  status: 'SUBMITTED' | 'PROCESSING' | 'AUTO_APPROVED' | 'MANUAL_REVIEW' | 'FLAGGED_INVESTIGATION' | 'REQUEST_INFO' | 'REJECTED' | 'APPROVED';
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'CRITICAL';
  priority_score: number;
  fraud_score: number;
  fraud_risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  ai_confidence: number;
  estimated_min?: number;
  estimated_max?: number;
  submitted_modalities: string[];
  missing_information?: string[];
  asset_identifier?: string;
  repair_shop_name?: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentItem {
  id: string;
  claim_id: string;
  file_name: string;
  file_path: string;
  file_type: string;
  doc_category: string;
  file_size: number;
  perceptual_hash?: string;
  ocr_text?: string;
}

export interface DamageAssessment {
  id: string;
  claim_id: string;
  damage_detected: boolean;
  damage_types: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
  affected_components: string[];
  confidence: number;
  annotated_image_path?: string;
  bounding_boxes: Array<{
    box_2d: [number, number, number, number];
    label: string;
    score: number;
  }>;
}

export interface FraudSignal {
  id: string;
  claim_id: string;
  signal: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  category: string;
  details?: any;
}

export interface AIDecision {
  id: string;
  claim_id: string;
  recommendation: string;
  confidence: number;
  reasoning_summary: string;
  evidence_points: string[];
  component_confidences: Record<string, number>;
  recommended_action: string;
}

export interface HumanReview {
  id: string;
  claim_id: string;
  reviewer_name: string;
  human_decision: string;
  override_ai: boolean;
  override_reason?: string;
  reviewer_notes?: string;
  created_at: string;
}

export interface AuditLog {
  id: string;
  claim_id: string;
  event_type: string;
  actor: string;
  actor_id?: string;
  details: any;
  timestamp: string;
}

export interface ClaimDetailResponse {
  claim: Claim;
  documents: DocumentItem[];
  damage_assessments: DamageAssessment[];
  fraud_signals: FraudSignal[];
  ai_decisions: AIDecision[];
  human_reviews: HumanReview[];
  audit_logs: AuditLog[];
}
