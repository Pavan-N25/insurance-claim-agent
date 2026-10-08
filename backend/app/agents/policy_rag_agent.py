from typing import Dict, Any
from backend.app.agents.base import BaseAgent
from backend.app.services.rag_service import rag_service

class PolicyCoverageAgent(BaseAgent):
    def __init__(self):
        super().__init__("PolicyCoverageAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Evaluating policy coverage via RAG engine...")
        claim_data = state.get("claim_data", {})
        query = f"{claim_data.get('claim_type', '')} {claim_data.get('incident_description', '')}"

        # Retrieve grounded clauses with citations
        citations = await rag_service.retrieve_relevant_clauses(query, top_k=2)

        coverage_applicable = True
        deductible = 5000.0
        coverage_limit = 500000.0
        confidence = 0.94

        if citations:
            best_match = citations[0]
            coverage_applicable = best_match.get("coverage_applicable", True)
            deductible = best_match.get("deductible", 5000.0)
            confidence = best_match.get("confidence", 0.94)

        claimed = claim_data.get("claimed_amount", 0.0)
        coverage_notes = (
            f"Evaluated against {len(citations)} policy clauses. "
            f"Coverage is applicable under {citations[0]['page_or_section'] if citations else 'General Terms'}. "
            f"Applicable compulsory deductible: ₹{deductible:,.0f}."
        )

        return {
            "coverage_applicable": coverage_applicable,
            "coverage_limit": coverage_limit,
            "deductible": deductible,
            "confidence": confidence,
            "citations": citations,
            "coverage_notes": coverage_notes
        }
