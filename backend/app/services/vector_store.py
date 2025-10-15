import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Optional
from app.config import get_settings
import uuid

# Use sentence_transformers directly
from sentence_transformers import SentenceTransformer

settings = get_settings()

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Load sentence transformer model directly
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def _embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def _embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query text"""
        embedding = self.embedding_model.encode([text], convert_to_numpy=True)
        return embedding[0].tolist()
    
    async def add_document(self, document_id: str, chunks: List[str], metadata: dict):
        """Add document chunks to vector store"""
        embeddings = self._embed_documents(chunks)
        
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        metadatas = [{**metadata, "chunk_index": i} for i in range(len(chunks))]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
    
    async def search(self, query: str, document_ids: Optional[List[str]] = None, top_k: int = 5):
        """Search for relevant chunks"""
        query_embedding = self._embed_query(query)
        
        where_filter = None
        if document_ids:
            where_filter = {"document_id": {"$in": document_ids}}
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
        
        return results
    
    async def delete_document(self, document_id: str):
        """Delete all chunks of a document"""
        self.collection.delete(where={"document_id": document_id})