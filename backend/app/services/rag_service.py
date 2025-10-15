from langchain_google_genai import ChatGoogleGenerativeAI
from app.services.vector_store import VectorStore
from app.config import get_settings
from typing import Optional, List
import re

settings = get_settings()

class RAGService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",  # Updated to Gemini 2.5 Flash
            google_api_key=settings.gemini_api_key,
            temperature=0.4
        )
    
    def _handle_small_talk(self, query: str) -> Optional[str]:
        """Return a friendly, human response for small‑talk style queries.

        This avoids forcing the LLM to answer strictly from document context
        when the user is just greeting or asking about capabilities.
        """
        q = query.strip().lower()
        # Greetings
        if re.fullmatch(r"(hi|hello|hey|yo|hiya|good\s*(morning|afternoon|evening))\b[!. ]*", q):
            return (
                "Hi there! I can answer questions about the documents you upload. "
                "Use the panel on the left to upload PDFs, DOCX, or TXT files, then ask me things like "
                "'Summarize section 3', 'What are the prerequisites?', or 'List the key topics about X'."
            )
        
        # Help / capabilities
        if any(kw in q for kw in ["help", "what can you do", "how to use", "how do i use", "guide", "instructions"]):
            return (
                "Here's how I can help: upload one or more documents and ask questions. "
                "I’ll retrieve the most relevant snippets and draft a clear answer with sources. "
                "Try: 'Give me a high‑level summary', 'Compare A vs B', or 'Extract deadlines from the syllabus'."
            )
        
        # Thanks / closing
        if any(kw in q for kw in ["thanks", "thank you", "ty", "thx"]):
            return "You're welcome! If you have more questions about your documents, just ask."
        if any(kw in q for kw in ["bye", "goodbye", "see you", "cya"]):
            return "Goodbye! Feel free to come back anytime with more documents or questions."
        
        # About the assistant
        if any(kw in q for kw in ["who are you", "what are you", "about you"]):
            return (
                "I'm a document Q&A assistant powered by retrieval‑augmented generation (RAG). "
                "I search your uploaded files for relevant passages and use an LLM to compose answers, "
                "including short source snippets so you can verify them."
            )
        
        return None
    
    async def query(self, query: str, document_ids: Optional[List[str]] = None, top_k: int = 5):
        """Execute RAG pipeline with a conversational fallback."""
        # 0. Friendly small‑talk handling
        small_talk = self._handle_small_talk(query)
        if small_talk is not None:
            return {"answer": small_talk, "sources": []}
        
        # 1. Retrieve relevant chunks
        search_results = await self.vector_store.search(query, document_ids, top_k)
        
        if not search_results['documents'][0]:
            return {
                "answer": (
                    "I couldn't find anything in your documents that answers that directly. "
                    "You can try asking about a specific topic or phrase, upload another file, "
                    "or increase the 'Top k' setting to search more snippets."
                ),
                "sources": []
            }
        
        # 2. Prepare context from retrieved chunks
        contexts = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        
        context_text = "\n\n".join([f"[{i+1}] {ctx}" for i, ctx in enumerate(contexts)])
        
        # 3. Create prompt
        prompt = f"""You are a friendly, helpful assistant answering questions about the user's uploaded documents. 
Write naturally and clearly in a conversational tone, but stay faithful to the provided context.

Context (snippets from the user's documents):
{context_text}

User question: {query}

Instructions:
- Answer directly and concisely, using bullet points or short paragraphs when helpful.
- Cite facts only if they appear in the context. Do not invent details.
- If the context is insufficient, say politely that the documents don't contain enough information and suggest what to ask next.
"""
        
        # 4. Generate response
        response = self.llm.invoke(prompt)
        
        # 5. Format sources
        sources = [
            {
                "content": contexts[i][:200] + "..." if len(contexts[i]) > 200 else contexts[i],
                "document_id": metadatas[i].get("document_id"),
                "filename": metadatas[i].get("filename"),
                "chunk_index": metadatas[i].get("chunk_index")
            }
            for i in range(len(contexts))
        ]
        
        return {
            "answer": response.content,
            "sources": sources
        }