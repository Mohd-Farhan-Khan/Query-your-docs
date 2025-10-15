from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # MongoDB
    mongodb_uri: str = "mongodb://mongodb:27017/"
    mongodb_db_name: str = "rag_documents"
    
    # Gemini
    gemini_api_key: str
    
    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"
    
    # App Settings
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # Upload Settings
    max_file_size_mb: int = 50
    max_pages_per_doc: int = 1000
    max_documents: int = 20
    
    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()