from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import documents, queries
from app.database import connect_to_mongo, close_mongo_connection
from app.models import HealthResponse
from app.config import get_settings
import os

settings = get_settings()

app = FastAPI(
    title="RAG Document Q&A API",
    description="Retrieval-Augmented Generation pipeline for document question answering",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Include routers
app.include_router(documents.router)
app.include_router(queries.router)

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "RAG Document Q&A API",
        "docs": "/docs",
        "health": "/api/health"
    }