import streamlit as st
import requests
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="RAG Document Q&A",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Title and description
st.title("📚 RAG Document Q&A System")
st.markdown("Upload documents and ask questions based on their content")

# Sidebar for document management
with st.sidebar:
    st.header("📁 Document Management")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=['pdf', 'docx', 'txt'],
        help="Max 50MB, up to 1000 pages"
    )
    
    if uploaded_file and st.button("Upload"):
        with st.spinner("Uploading and processing..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(f"{BACKEND_URL}/api/documents/upload", files=files)
                
                if response.status_code == 200:
                    st.success("✅ Document uploaded successfully!")
                else:
                    st.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    # List documents
    st.subheader("📄 Uploaded Documents")
    try:
        response = requests.get(f"{BACKEND_URL}/api/documents")
        if response.status_code == 200:
            documents = response.json()
            
            if documents:
                for doc in documents:
                    with st.expander(f"📄 {doc['filename'][:30]}..."):
                        st.write(f"**Status:** {doc['status']}")
                        st.write(f"**Pages:** {doc['page_count']}")
                        st.write(f"**Chunks:** {doc['chunk_count']}")
                        st.write(f"**Size:** {doc['file_size'] / 1024:.2f} KB")
                        st.write(f"**Uploaded:** {doc['upload_date'][:19]}")
                        
                        if st.button(f"🗑️ Delete", key=doc['id']):
                            del_response = requests.delete(f"{BACKEND_URL}/api/documents/{doc['id']}")
                            if del_response.status_code == 200:
                                st.success("Deleted!")
                                st.rerun()
            else:
                st.info("No documents uploaded yet")
    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")

# Main chat interface
st.header("💬 Ask Questions")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 Sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"**Source {i}:** {source['filename']}")
                    st.text(source['content'])
                    st.divider()

# Chat input
if query := st.chat_input("Ask a question about your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/queries",
                    json={"query": query, "top_k": 5}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.markdown(result['answer'])
                    
                    # Add assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result['answer'],
                        "sources": result['sources']
                    })
                    
                    # Show sources
                    if result['sources']:
                        with st.expander("📚 Sources"):
                            for i, source in enumerate(result['sources'], 1):
                                st.markdown(f"**Source {i}:** {source['filename']}")
                                st.text(source['content'])
                                st.divider()
                else:
                    st.error("Failed to get response")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Clear chat button
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Footer
st.sidebar.divider()
st.sidebar.caption("RAG Document Q&A v1.0.0")