from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.services.rag_service import rag_service

router = APIRouter(prefix="/knowledge", tags=["Policy Knowledge Base (RAG)"])

class QueryKnowledgeRequest(BaseModel):
    query: str
    top_k: int = 3

@router.get("")
def list_knowledge_documents():
    return [
        {
            "id": doc["id"],
            "title": doc["title"],
            "section": doc["section"],
            "source_document": doc["source_document"],
            "coverage_applicable": doc["coverage_applicable"],
            "deductible": doc["deductible"],
            "content_preview": doc["content"][:160] + "..."
        }
        for doc in rag_service.knowledge_base
    ]

@router.post("/query")
async def query_knowledge_base(req: QueryKnowledgeRequest):
    results = await rag_service.retrieve_relevant_clauses(req.query, top_k=req.top_k)
    return {"query": req.query, "results": results}
