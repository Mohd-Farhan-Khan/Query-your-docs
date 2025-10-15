from fastapi import APIRouter, HTTPException
from app.models import QueryRequest, QueryResponse
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api/queries", tags=["queries"])

@router.post("", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents using RAG"""
    try:
        rag_service = RAGService()
        result = await rag_service.query(
            query=request.query,
            document_ids=request.document_ids,
            top_k=request.top_k
        )
        
        return QueryResponse(
            query=request.query,
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(500, f"Query failed: {str(e)}")