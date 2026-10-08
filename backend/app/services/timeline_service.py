from datetime import datetime
from typing import List, Dict, Any, Optional
from dateutil import parser as date_parser

class TimelineService:
    @staticmethod
    def reconstruct_timeline(
        policy_start: Optional[datetime],
        incident_date_str: str,
        claim_created: datetime,
        documents_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Reconstructs the chronological sequence of claim lifecycle events and detects timeline anomalies.
        """
        events = []
        anomalies = []

        # 1. Policy Inception Event
        if policy_start:
            events.append({
                "timestamp": policy_start.isoformat(),
                "title": "Policy Inception",
                "description": "Insurance policy active coverage started.",
                "type": "POLICY"
            })

        # 2. Incident Event
        incident_dt = None
        try:
            incident_dt = date_parser.parse(incident_date_str)
            events.append({
                "timestamp": incident_dt.isoformat(),
                "title": "Reported Incident",
                "description": f"Incident occurred as stated by claimant.",
                "type": "INCIDENT"
            })
        except Exception:
            anomalies.append({
                "issue": "Unparseable incident timestamp format.",
                "severity": "MEDIUM"
            })

        # 3. Document timestamps (Police Report, Repair Estimate, etc.)
        for doc in documents_metadata:
            cat = doc.get("doc_category", "document")
            doc_date_str = doc.get("extracted_metadata", {}).get("document_date")
            doc_dt = None
            if doc_date_str:
                try:
                    doc_dt = date_parser.parse(doc_date_str)
                    events.append({
                        "timestamp": doc_dt.isoformat(),
                        "title": f"Document Issued: {cat.replace('_', ' ').title()}",
                        "description": f"Official record generated ({doc.get('file_name', '')}).",
                        "type": "DOCUMENT"
                    })
                except Exception:
                    pass

            # Check if police report was dated before incident occurred!
            if cat == "police_report" and doc_dt and incident_dt and doc_dt < incident_dt:
                anomalies.append({
                    "issue": "Impossible Timeline: Police report date precedes reported incident timestamp.",
                    "severity": "CRITICAL"
                })

        # 4. Check if incident occurred prior to policy inception
        if policy_start and incident_dt and incident_dt < policy_start:
            anomalies.append({
                "issue": "Coverage Conflict: Incident date is prior to policy commencement date.",
                "severity": "CRITICAL"
            })

        # 5. Claim Submission Event
        events.append({
            "timestamp": claim_created.isoformat(),
            "title": "Claim Submitted",
            "description": "Multimodal dossier submitted into triage pipeline.",
            "type": "SUBMISSION"
        })

        # 6. Sort events chronologically
        events.sort(key=lambda x: x["timestamp"])

        return {
            "events": events,
            "anomalies": anomalies,
            "has_temporal_conflicts": len(anomalies) > 0
        }
