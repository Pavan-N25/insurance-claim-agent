from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_auth_login_admin():
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@insurance.ai",
        "password": "Admin@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"

def test_list_claims():
    response = client.get("/api/v1/claims")
    assert response.status_code == 200
    claims = response.json()
    assert isinstance(claims, list)
    assert len(claims) >= 3

def test_get_claim_detail():
    response = client.get("/api/v1/claims/CLM-2026-1001")
    assert response.status_code == 200
    data = response.json()
    assert data["claim"]["id"] == "CLM-2026-1001"
    assert "documents" in data
    assert "ai_decisions" in data

def test_simulator():
    response = client.post("/api/v1/simulator/evaluate", json={
        "claimed_amount": 45000.0,
        "damage_severity": "MEDIUM",
        "fraud_score": 15.0,
        "policy_limit": 500000.0,
        "deductible": 5000.0,
        "confidence": 0.90
    })
    assert response.status_code == 200
    data = response.json()
    assert data["simulated_recommendation"] == "AUTO_APPROVE"
