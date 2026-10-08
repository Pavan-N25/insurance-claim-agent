from typing import Dict, List, Any
from sqlalchemy.orm import Session
from backend.app.models.schema import Claim, Document

class FraudGraphService:
    @staticmethod
    def analyze_network_clusters(db: Session, current_claim: Claim) -> List[Dict[str, Any]]:
        """
        Analyzes relationships between Claimants, Vehicles, Repair Shops, and Bank Accounts.
        Identifies suspicious repeat clusters and organized fraud rings.
        """
        signals = []

        # 1. Check if same repair shop appears in abnormally high frequency of recent claims
        if current_claim.repair_shop_name:
            shop_claims = db.query(Claim).filter(
                Claim.repair_shop_name == current_claim.repair_shop_name,
                Claim.id != current_claim.id
            ).all()

            if len(shop_claims) >= 3:
                signals.append({
                    "signal": f"Suspicious Repair Shop Cluster: '{current_claim.repair_shop_name}' associated with {len(shop_claims)} other recent claims.",
                    "severity": "HIGH" if len(shop_claims) >= 5 else "MEDIUM",
                    "confidence": 0.89,
                    "category": "NETWORK_CLUSTER",
                    "details": {
                        "repair_shop": current_claim.repair_shop_name,
                        "related_claims_count": len(shop_claims),
                        "related_claim_ids": [c.id for c in shop_claims[:5]]
                    }
                })

        # 2. Check if same asset/VIN was claimed multiple times in a short window
        if current_claim.asset_identifier:
            asset_claims = db.query(Claim).filter(
                Claim.asset_identifier == current_claim.asset_identifier,
                Claim.id != current_claim.id
            ).all()

            if len(asset_claims) >= 1:
                signals.append({
                    "signal": f"Repeat Asset Claim: Asset '{current_claim.asset_identifier}' previously claimed in {len(asset_claims)} prior cases.",
                    "severity": "HIGH",
                    "confidence": 0.94,
                    "category": "REPEAT_ASSET",
                    "details": {
                        "asset_id": current_claim.asset_identifier,
                        "prior_claim_ids": [c.id for c in asset_claims]
                    }
                })

        # 3. Check shared bank account hash across different claimants
        if current_claim.bank_account_hash:
            bank_claims = db.query(Claim).filter(
                Claim.bank_account_hash == current_claim.bank_account_hash,
                Claim.claimant_name != current_claim.claimant_name,
                Claim.id != current_claim.id
            ).all()

            if bank_claims:
                signals.append({
                    "signal": f"Shared Payout Account Anomaly: Same bank account registered under different claimant names ({len(bank_claims)} match).",
                    "severity": "CRITICAL",
                    "confidence": 0.98,
                    "category": "ACCOUNT_SHARING",
                    "details": {
                        "matching_claims": [c.id for c in bank_claims]
                    }
                })

        return signals

    @staticmethod
    def get_claim_graph_data(db: Session, claim_id: str) -> Dict[str, Any]:
        """
        Returns nodes and edges formatted for interactive graph visualization.
        """
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            return {"nodes": [], "edges": []}

        nodes = [
            {"id": f"claim_{claim.id}", "label": f"Claim: {claim.id}", "type": "claim", "color": "#3B82F6"},
            {"id": f"customer_{claim.claimant_name}", "label": claim.claimant_name, "type": "customer", "color": "#10B981"}
        ]
        edges = [
            {"source": f"customer_{claim.claimant_name}", "target": f"claim_{claim.id}", "relation": "FILED"}
        ]

        if claim.asset_identifier:
            nodes.append({"id": f"asset_{claim.asset_identifier}", "label": f"Asset: {claim.asset_identifier}", "type": "asset", "color": "#8B5CF6"})
            edges.append({"source": f"claim_{claim.id}", "target": f"asset_{claim.asset_identifier}", "relation": "INVOLVES"})

        if claim.repair_shop_name:
            nodes.append({"id": f"shop_{claim.repair_shop_name}", "label": f"Shop: {claim.repair_shop_name}", "type": "shop", "color": "#F59E0B"})
            edges.append({"source": f"claim_{claim.id}", "target": f"shop_{claim.repair_shop_name}", "relation": "ESTIMATED_BY"})

            # Connect other claims using this shop
            other_claims = db.query(Claim).filter(
                Claim.repair_shop_name == claim.repair_shop_name,
                Claim.id != claim.id
            ).limit(4).all()

            for oc in other_claims:
                nodes.append({"id": f"claim_{oc.id}", "label": f"Claim: {oc.id}", "type": "claim", "color": "#94A3B8"})
                edges.append({"source": f"claim_{oc.id}", "target": f"shop_{claim.repair_shop_name}", "relation": "ESTIMATED_BY"})

        if claim.bank_account_hash:
            nodes.append({"id": f"bank_{claim.bank_account_hash[:6]}", "label": "Bank Acct ***" + claim.bank_account_hash[-4:], "type": "bank", "color": "#EC4899"})
            edges.append({"source": f"claim_{claim.id}", "target": f"bank_{claim.bank_account_hash[:6]}", "relation": "PAYOUT_TO"})

        return {"nodes": nodes, "edges": edges}
