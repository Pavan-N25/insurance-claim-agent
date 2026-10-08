import pytest
from backend.app.agents.intake_agent import IntakeAgent
from backend.app.agents.vision_agent import VisionDamageAgent
from backend.app.agents.fraud_agent import FraudDetectionAgent
from backend.app.agents.severity_agent import ClaimSeverityAgent
from backend.app.agents.estimation_agent import ClaimEstimationAgent
from backend.app.agents.decision_agent import DecisionAgent
from backend.app.agents.explainability_agent import ExplainabilityAgent
from backend.app.services.image_hash_service import ImageHashService

@pytest.mark.asyncio
async def test_intake_agent():
    agent = IntakeAgent()
    state = {
        "claim_id": "CLM-TEST-001",
        "claim_data": {
            "policy_number": "POL-AUTO-8821",
            "claimant_name": "Test User",
            "incident_date": "2026-10-01",
            "incident_location": "Bangalore",
            "claimed_amount": 35000.0,
            "incident_description": "Hit parked car."
        },
        "documents": [
            {"file_name": "damage.jpg", "file_type": "image/jpeg", "id": "D1"}
        ]
    }
    result = await agent.process(state)
    assert result["claim_id"] == "CLM-TEST-001"
    assert "image" in result["submitted_modalities"]
    assert "text" in result["submitted_modalities"]

@pytest.mark.asyncio
async def test_fraud_agent_duplicate_image():
    agent = FraudDetectionAgent()
    # Test identical hash triggering duplicate image signal
    state = {
        "claim_id": "CLM-CURR-01",
        "claim_data": {"claimed_amount": 50000.0},
        "vision_output": {
            "perceptual_hashes": [{"hash": "a1b2c3d4e5f60011", "document_id": "D1"}]
        },
        "historical_hashes": [
            {"claim_id": "CLM-HIST-99", "hash": "a1b2c3d4e5f60011"}
        ],
        "network_signals": [],
        "timeline_output": {"anomalies": []}
    }
    result = await agent.process(state)
    assert result["fraud_score"] >= 50.0
    assert any(s["category"] == "DUPLICATE_IMAGE" for s in result["signals"])

@pytest.mark.asyncio
async def test_decision_agent_guardrail():
    agent = DecisionAgent()
    # High value claim should require MANUAL_REVIEW
    state = {
        "claim_data": {"claimed_amount": 250000.0},
        "intake_output": {"missing_information": []},
        "vision_output": {"confidence": 0.92, "severity": "high"},
        "policy_output": {"coverage_applicable": True, "confidence": 0.95},
        "fraud_output": {"fraud_score": 15.0, "signals": []},
        "severity_output": {"overall_severity": "HIGH"}
    }
    result = await agent.process(state)
    assert result["recommendation"] == "MANUAL_REVIEW"
    assert "exceeds" in result["reasoning_summary"]

def test_image_hasher_hamming():
    h1 = "ffff0000ffff0000"
    h2 = "ffff0000ffff0000"
    assert ImageHashService.hamming_distance(h1, h2) == 0

    h3 = "0000ffff0000ffff"
    assert ImageHashService.hamming_distance(h1, h3) > 0
