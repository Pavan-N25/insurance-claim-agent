from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.llm_provider import get_llm_provider
from backend.app.models.schema import Claim, Document, FraudSignal, DamageAssessment, AIDecision
from backend.app.schemas.pydantic_models import CopilotChatRequest, CopilotChatResponse
from backend.app.services.rag_service import rag_service

router = APIRouter(prefix="/copilot", tags=["AI Claim Copilot"])

@router.post("/chat", response_model=CopilotChatResponse)
async def chat_copilot(req: CopilotChatRequest, db: Session = Depends(get_db)):
    llm = get_llm_provider()
    query_lower = req.query.lower()
    citations = []
    followups = [
        "What policy clause is relevant?",
        "Show me the fraud indicators",
        "Generate a customer response"
    ]

    claim = None
    if req.claim_id:
        claim = db.query(Claim).filter(Claim.id == req.claim_id).first()

    if not claim:
        # General insurance knowledge query
        citations_data = await rag_service.retrieve_relevant_clauses(req.query)
        citation_texts = [f"{c['source_document']} ({c['page_or_section']})" for c in citations_data]
        prompt = f"Question: {req.query}\nPolicy Context: {citations_data[0]['clause_text'] if citations_data else ''}"
        reply = await llm.generate_text(prompt, system_prompt="You are an enterprise AI Insurance Copilot assistant.")
        return CopilotChatResponse(
            response=reply,
            grounded_citations=citation_texts,
            suggested_followups=["How does deductible apply?", "What are the exclusions?"]
        )

    # Claim-grounded responses
    signals = db.query(FraudSignal).filter(FraudSignal.claim_id == claim.id).all()
    damage = db.query(DamageAssessment).filter(DamageAssessment.claim_id == claim.id).first()
    ai_dec = db.query(AIDecision).filter(AIDecision.claim_id == claim.id).first()

    if "why was this claim flagged" in query_lower or "flagged" in query_lower:
        if signals:
            sig_list = "\n".join([f"• [{s.severity}] {s.signal}" for s in signals])
            response_text = (
                f"Claim {claim.id} was flagged with a Fraud Risk Score of {claim.fraud_score}/100 based on the following anomalies:\n\n"
                f"{sig_list}\n\n"
                f"Additionally, the priority is ranked as {claim.priority} with claimed amount of ₹{claim.claimed_amount:,.0f}."
            )
            citations.append("Fraud Engine Telemetry")
        else:
            response_text = f"Claim {claim.id} has not been flagged for fraud (Risk Score: {claim.fraud_score}/100, Level: {claim.fraud_risk_level})."

    elif "summarize" in query_lower:
        response_text = (
            f"**Claim Summary for {claim.id}**:\n"
            f"• Claimant: {claim.claimant_name} ({claim.claim_type})\n"
            f"• Incident: {claim.incident_date} at {claim.incident_location}\n"
            f"• Claimed Amount: ₹{claim.claimed_amount:,.0f} (Estimated range: ₹{claim.estimated_min or 0:,.0f} - ₹{claim.estimated_max or 0:,.0f})\n"
            f"• Status: {claim.status} (AI Confidence: {int(claim.ai_confidence * 100)}%)\n"
            f"• Key Narrative: {claim.incident_description}"
        )
        citations.append(f"Claim Record #{claim.id}")

    elif "missing" in query_lower or "documents" in query_lower:
        missing = claim.missing_information or []
        if missing:
            response_text = (
                f"The following required documentation items are currently missing for claim {claim.id}:\n"
                + "\n".join([f"• {m}" for m in missing]) +
                "\n\nYou can use the Customer Portal messaging agent to request these from the claimant."
            )
        else:
            response_text = f"All required document and evidence modalities have been satisfied for claim {claim.id}."

    elif "clause" in query_lower or "policy" in query_lower:
        rag_hits = await rag_service.retrieve_relevant_clauses(f"{claim.claim_type} {claim.incident_description}")
        if rag_hits:
            hit = rag_hits[0]
            response_text = (
                f"Relevant Policy Clause for this claim:\n"
                f"**{hit['page_or_section']}** from *{hit['source_document']}* (Confidence: {int(hit['confidence']*100)}%)\n\n"
                f"> \"{hit['clause_text']}\"\n\n"
                f"Applicable Deductible: ₹{hit['deductible']:,.0f}. Coverage Applicable: {'Yes' if hit['coverage_applicable'] else 'No'}."
            )
            citations.append(f"{hit['source_document']} - {hit['page_or_section']}")
        else:
            response_text = "No conflicting policy exclusion clauses identified."

    elif "investigate" in query_lower or "next" in query_lower:
        response_text = (
            f"Recommended Next Actions for Adjuster:\n"
            f"1. Conduct cross-check of repair facility '{claim.repair_shop_name or 'designated shop'}' against historical invoice clusters.\n"
            f"2. Validate damage photos with perceptual hash duplicates.\n"
            f"3. Verify incident time with police station report if applicable."
        )

    else:
        # Contextual LLM completion
        context = f"Claim ID: {claim.id}, Claimant: {claim.claimant_name}, Status: {claim.status}, Fraud Score: {claim.fraud_score}, Description: {claim.incident_description}"
        response_text = await llm.generate_text(
            f"Claim Context:\n{context}\n\nAdjuster Question: {req.query}",
            system_prompt="You are an enterprise AI Insurance Copilot assistant providing exact, factual adjuster assistance."
        )

    return CopilotChatResponse(
        response=response_text,
        grounded_citations=citations,
        suggested_followups=followups
    )
