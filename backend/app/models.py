from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentMetadata(BaseModel):
    id: str
    filename: str
    file_size: int
    page_count: int
    status: DocumentStatus
    upload_date: datetime
    chunk_count: Optional[int] = 0

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str

class QueryRequest(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None
    top_k: int = Field(default=5, ge=1, le=10)

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[dict]
    
class HealthResponse(BaseModel):
    status: str
    version: str