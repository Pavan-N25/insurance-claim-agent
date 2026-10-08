from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class WorkflowState(BaseModel):
    claim_id: str
    claim_data: Dict[str, Any]
    documents: List[Dict[str, Any]] = []
    historical_hashes: List[Dict[str, Any]] = []
    network_signals: List[Dict[str, Any]] = []
    timeline_output: Dict[str, Any] = {}

    # Stage outputs
    intake_output: Optional[Dict[str, Any]] = None
    document_output: Optional[Dict[str, Any]] = None
    understanding_output: Optional[Dict[str, Any]] = None
    vision_output: Optional[Dict[str, Any]] = None
    policy_output: Optional[Dict[str, Any]] = None
    fraud_output: Optional[Dict[str, Any]] = None
    severity_output: Optional[Dict[str, Any]] = None
    estimation_output: Optional[Dict[str, Any]] = None
    decision_output: Optional[Dict[str, Any]] = None
    explainability_output: Optional[Dict[str, Any]] = None
    customer_comm_output: Optional[Dict[str, Any]] = None

    # Pipeline tracking
    current_step: str = "INITIALIZED"
    completed_steps: List[str] = []
    errors: List[str] = []
