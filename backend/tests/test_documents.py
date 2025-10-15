import pytest
from httpx import AsyncClient
from app.main import app
import os

@pytest.mark.asyncio
async def test_upload_document():
    """Test document upload endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a test file
        test_content = b"This is a test document content."
        files = {"file": ("test.txt", test_content, "text/plain")}
        
        response = await client.post("/api/documents/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["status"] == "completed"

@pytest.mark.asyncio
async def test_list_documents():
    """Test listing documents"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/documents")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_upload_invalid_file():
    """Test uploading invalid file type"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        files = {"file": ("test.exe", b"content", "application/x-msdownload")}
        
        response = await client.post("/api/documents/upload", files=files)
        
        assert response.status_code == 400