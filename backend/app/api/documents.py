from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.models import DocumentUploadResponse, DocumentMetadata, DocumentStatus
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore
from app.utils.file_handler import FileHandler
from app.database import get_database
from app.config import get_settings
from datetime import datetime
import uuid
import os

router = APIRouter(prefix="/api/documents", tags=["documents"])
settings = get_settings()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(400, "Unsupported file format. Use PDF, DOCX, or TXT")
        
        # Check file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        max_size = settings.max_file_size_mb * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(400, f"File size exceeds {settings.max_file_size_mb}MB limit")
        
        # Check document count
        db = get_database()
        doc_count = await db.documents.count_documents({})
        if doc_count >= settings.max_documents:
            raise HTTPException(400, f"Maximum {settings.max_documents} documents allowed")
        
        # Save file (removed await)
        file_path = FileHandler.save_upload_file(file.file, file.filename)
        document_id = str(uuid.uuid4())
        
        # Create document metadata
        doc_metadata = {
            "_id": document_id,
            "filename": file.filename,
            "file_size": file_size,
            "file_path": file_path,
            "status": DocumentStatus.PROCESSING,
            "upload_date": datetime.utcnow(),
            "page_count": 0,
            "chunk_count": 0
        }
        
        await db.documents.insert_one(doc_metadata)
        
        # Process document
        try:
            processor = DocumentProcessor()
            text, page_count, chunks = await processor.process_document(file_path, file.filename)
            
            # Store in vector database
            vector_store = VectorStore()
            await vector_store.add_document(
                document_id=document_id,
                chunks=chunks,
                metadata={
                    "document_id": document_id,
                    "filename": file.filename
                }
            )
            
            # Update metadata
            await db.documents.update_one(
                {"_id": document_id},
                {"$set": {
                    "status": DocumentStatus.COMPLETED,
                    "page_count": page_count,
                    "chunk_count": len(chunks)
                }}
            )
            
            return DocumentUploadResponse(
                document_id=document_id,
                filename=file.filename,
                status="completed",
                message="Document processed successfully"
            )
            
        except Exception as e:
            await db.documents.update_one(
                {"_id": document_id},
                {"$set": {"status": DocumentStatus.FAILED}}
            )
            raise HTTPException(500, f"Error processing document: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

@router.get("", response_model=list[DocumentMetadata])
async def list_documents():
    """Get all documents metadata"""
    db = get_database()
    documents = await db.documents.find().to_list(100)
    
    return [
        DocumentMetadata(
            id=doc["_id"],
            filename=doc["filename"],
            file_size=doc["file_size"],
            page_count=doc.get("page_count", 0),
            status=doc["status"],
            upload_date=doc["upload_date"],
            chunk_count=doc.get("chunk_count", 0)
        )
        for doc in documents
    ]

@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document(document_id: str):
    """Get specific document metadata"""
    db = get_database()
    doc = await db.documents.find_one({"_id": document_id})
    
    if not doc:
        raise HTTPException(404, "Document not found")
    
    return DocumentMetadata(
        id=doc["_id"],
        filename=doc["filename"],
        file_size=doc["file_size"],
        page_count=doc.get("page_count", 0),
        status=doc["status"],
        upload_date=doc["upload_date"],
        chunk_count=doc.get("chunk_count", 0)
    )

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    db = get_database()
    doc = await db.documents.find_one({"_id": document_id})
    
    if not doc:
        raise HTTPException(404, "Document not found")
    
    # Delete from vector store
    vector_store = VectorStore()
    await vector_store.delete_document(document_id)
    
    # Delete file
    if os.path.exists(doc["file_path"]):
        os.remove(doc["file_path"])
    
    # Delete from database
    await db.documents.delete_one({"_id": document_id})
    
    return {"message": "Document deleted successfully"}