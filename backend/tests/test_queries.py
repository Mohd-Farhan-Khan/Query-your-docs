import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_query_documents():
    """Test querying documents"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        query_data = {
            "query": "What is the main topic of the documents?",
            "top_k": 5
        }
        
        response = await client.post("/api/queries", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "answer" in data
        assert "sources" in data

@pytest.mark.asyncio
async def test_health_check():
    """Test health endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"