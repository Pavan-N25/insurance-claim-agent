import os
import math
from typing import List, Dict, Any, Optional
from backend.app.core.llm_provider import get_llm_provider

class PolicyRAGService:
    def __init__(self):
        self.llm = get_llm_provider()
        self.knowledge_base: List[Dict[str, Any]] = [
            {
                "id": "KB-AUTO-01",
                "title": "Comprehensive Motor Vehicle Policy Terms",
                "section": "Section 4.1 - Collision & Impact Damage",
                "source_document": "Motor_Comprehensive_Policy_v4.pdf",
                "content": (
                    "Covers accidental external physical damage to the insured vehicle arising from collision, "
                    "impact, overturn, or collision with stationary objects. Standard compulsory deductible is ₹5,000 "
                    "for private cars up to 1500cc, and ₹10,000 for vehicles exceeding 1500cc. Depreciation applied on "
                    "rubber and nylon parts is 50%, glass parts 0%, metal parts 10% for vehicles aged 1-2 years."
                ),
                "coverage_applicable": True,
                "deductible": 5000.0,
                "embedding": None
            },
            {
                "id": "KB-AUTO-02",
                "title": "Exclusions: Mechanical Breakdown & Intoxication",
                "section": "Section 8.2 - General Exclusions",
                "source_document": "Motor_Comprehensive_Policy_v4.pdf",
                "content": (
                    "The company shall not be liable to make any payment in respect of: consequential loss, "
                    "depreciation, wear and tear, mechanical or electrical breakdown, failures or breakages; "
                    "damage caused whilst the person driving is under the influence of intoxicating liquor or drugs; "
                    "or damage sustained when vehicle was operated outside territorial limits."
                ),
                "coverage_applicable": False,
                "deductible": 0.0,
                "embedding": None
            },
            {
                "id": "KB-PROP-01",
                "title": "Standard Property Damage & Water Ingress",
                "section": "Clause 12.3 - Pipe Burst & Accidental Water Discharge",
                "source_document": "Property_Standard_Protection_Policy.pdf",
                "content": (
                    "Protects against sudden and accidental discharge or overflow of water or steam from within a "
                    "plumbing, heating, air conditioning or automatic fire protective sprinkler system. Deductible is "
                    "₹15,000. Gradual seepage or continuous leaks occurring over a period exceeding 14 days are excluded."
                ),
                "coverage_applicable": True,
                "deductible": 15000.0,
                "embedding": None
            },
            {
                "id": "KB-COMM-01",
                "title": "Commercial Fire & Special Perils",
                "section": "Section 3 - Fire & Lightning Perils",
                "source_document": "Commercial_Fire_Special_Perils_2025.pdf",
                "content": (
                    "Covers loss or damage to building and contents caused by fire, lightning, explosion/implosion, "
                    "aircraft damage, riot, strike, and malicious damage. Fire incident must be supported by an official "
                    "Fire Brigade Incident Report and Forensic Safety Inspection."
                ),
                "coverage_applicable": True,
                "deductible": 25000.0,
                "embedding": None
            }
        ]

    async def _ensure_embeddings(self):
        for item in self.knowledge_base:
            if item["embedding"] is None:
                item["embedding"] = await self.llm.generate_embedding(item["content"])

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.5
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.5
        return (dot / (norm1 * norm2) + 1.0) / 2.0  # Normalized to [0, 1]

    async def retrieve_relevant_clauses(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Retrieves top relevant policy clauses for a given incident query with citations and confidence.
        """
        await self._ensure_embeddings()
        query_emb = await self.llm.generate_embedding(query)

        scored = []
        for item in self.knowledge_base:
            sim = self._cosine_similarity(query_emb, item["embedding"])
            # Boost score if keywords match
            query_lower = query.lower()
            if ("collision" in query_lower or "car" in query_lower or "accident" in query_lower) and "motor" in item["source_document"].lower():
                sim = min(0.98, sim + 0.3)
            elif ("water" in query_lower or "leak" in query_lower or "pipe" in query_lower) and "property" in item["source_document"].lower():
                sim = min(0.97, sim + 0.35)
            elif ("fire" in query_lower or "smoke" in query_lower) and "fire" in item["source_document"].lower():
                sim = min(0.99, sim + 0.4)

            scored.append({
                "source_document": item["source_document"],
                "page_or_section": item["section"],
                "clause_text": item["content"],
                "coverage_applicable": item["coverage_applicable"],
                "deductible": item["deductible"],
                "confidence": round(sim, 2)
            })

        scored.sort(key=lambda x: x["confidence"], reverse=True)
        return scored[:top_k]

rag_service = PolicyRAGService()
