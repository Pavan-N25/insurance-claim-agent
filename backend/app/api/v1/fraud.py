from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_payload
from backend.app.models.schema import Claim, FraudSignal
from backend.app.services.fraud_graph_service import FraudGraphService

router = APIRouter(prefix="/fraud", tags=["Fraud & Anomaly Intelligence"])

@router.get("/overview")
def get_fraud_overview(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user_payload),
):
    total_claims = db.query(Claim).count()
    flagged_claims = db.query(Claim).filter(Claim.fraud_score >= 60).count()
    critical_signals = db.query(FraudSignal).filter(FraudSignal.severity == "CRITICAL").count()

    # Suspicious repair shops
    shop_stats = (
        db.query(Claim.repair_shop_name, func.count(Claim.id).label("claim_count"), func.avg(Claim.fraud_score).label("avg_fraud"))
        .filter(Claim.repair_shop_name != None)
        .group_by(Claim.repair_shop_name)
        .order_by(func.count(Claim.id).desc())
        .limit(5)
        .all()
    )

    shops = [
        {"shop_name": s[0], "claim_count": s[1], "avg_fraud_score": round(float(s[2] or 0), 1), "flagged": (s[1] >= 3 or (s[2] or 0) >= 60)}
        for s in shop_stats
    ]

    # Signal distribution
    signal_types = (
        db.query(FraudSignal.category, func.count(FraudSignal.id))
        .group_by(FraudSignal.category)
        .all()
    )
    categories = [{"category": st[0], "count": st[1]} for st in signal_types]

    return {
        "total_claims_scanned": total_claims,
        "high_risk_claims": flagged_claims,
        "critical_fraud_signals": critical_signals,
        "fraud_rate_pct": round((flagged_claims / max(1, total_claims)) * 100, 1),
        "suspicious_repair_shops": shops,
        "signal_distribution": categories
    }

@router.get("/network-graph/{claim_id}")
def get_network_graph(
    claim_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user_payload),
):
    return FraudGraphService.get_claim_graph_data(db, claim_id)
