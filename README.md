# 📚 RAG Document Q&A System

A production-ready Retrieval-Augmented Generation (RAG) pipeline that allows users to upload documents and ask questions based on their content using LangChain, ChromaDB, and Google Gemini.

## 🌟 Features

- **Document Upload**: Support for PDF, DOCX, and TXT files (up to 1000 pages)
- **Intelligent Chunking**: Efficient text splitting with LangChain
- **Vector Search**: Fast semantic search using ChromaDB with sentence-transformers
- **RAG Pipeline**: Context-aware responses using Google Gemini
- **REST API**: FastAPI backend with comprehensive endpoints
- **Modern UI**: Streamlit-based chat interface
- **Scalable**: Docker containerization for easy deployment
- **Database**: MongoDB Atlas for document metadata

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Streamlit  │ ───► │   FastAPI    │ ───► │   MongoDB   │
│   Frontend  │      │   Backend    │      │   (Metadata)│
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├───► ChromaDB (Vectors)
                            │
                            └───► Google Gemini (LLM)
```

## 📋 Prerequisites

- Docker & Docker Compose
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))
- 4GB RAM minimum
- 10GB free disk space

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd rag-document-qa
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Start the Application

```bash
docker-compose up --build
```

Wait for all services to start (about 2-3 minutes first time).

### 4. Access the Application

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MongoDB**: localhost:27017

## 📖 API Documentation

### Upload Document

```bash
POST /api/documents/upload
Content-Type: multipart/form-data

curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "document_id": "uuid-here",
  "filename": "document.pdf",
  "status": "completed",
  "message": "Document processed successfully"
}
```

### Query Documents

```bash
POST /api/queries
Content-Type: application/json

curl -X POST "http://localhost:8000/api/queries" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "query": "What is the main topic?",
  "answer": "Based on the documents...",
  "sources": [
    {
      "content": "Relevant chunk text...",
      "document_id": "uuid",
      "filename": "document.pdf",
      "chunk_index": 0
    }
  ]
}
```

### List Documents

```bash
GET /api/documents

curl "http://localhost:8000/api/documents"
```

### Get Document Details

```bash
GET /api/documents/{document_id}

curl "http://localhost:8000/api/documents/{document_id}"
```

### Delete Document

```bash
DELETE /api/documents/{document_id}

curl -X DELETE "http://localhost:8000/api/documents/{document_id}"
```

### Health Check

```bash
GET /api/health

curl "http://localhost:8000/api/health"
```

## 🧪 Running Tests

```bash
# Enter backend container
docker-compose exec backend bash

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://mongodb:27017/` |
| `MONGODB_DB_NAME` | Database name | `rag_documents` |
| `GEMINI_API_KEY` | Google Gemini API key | *required* |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | `./chroma_db` |
| `MAX_FILE_SIZE_MB` | Max upload size (MB) | `50` |
| `MAX_PAGES_PER_DOC` | Max pages per document | `1000` |
| `MAX_DOCUMENTS` | Max total documents | `20` |
| `CHUNK_SIZE` | Text chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |

### Customizing LLM Provider

To use a different LLM, modify `backend/app/services/rag_service.py`:

```python
# Example: Using OpenAI instead of Gemini
from langchain_openai import ChatOpenAI

self.llm = ChatOpenAI(
    model="gpt-4",
    openai_api_key=settings.openai_api_key,
    temperature=0.3
)
```

## 📁 Project Structure

```
rag-document-qa/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── utils/            # Utilities
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py         # Configuration
│   │   ├── models.py         # Pydantic models
│   │   └── database.py       # MongoDB connection
│   ├── tests/                # Unit tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app.py                # Streamlit UI
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Development

### Local Development (without Docker)

1. **Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start MongoDB locally or use MongoDB Atlas
export MONGODB_URI="your_mongodb_uri"
export GEMINI_API_KEY="your_api_key"

uvicorn app.main:app --reload --port 8000
```

2. **Frontend:**

```bash
cd frontend
pip install -r requirements.txt
export BACKEND_URL="http://localhost:8000"

streamlit run app.py
```

## 🐛 Troubleshooting

### Issue: MongoDB connection failed
**Solution:** Ensure MongoDB container is running:
```bash
docker-compose ps
docker-compose logs mongodb
```

### Issue: Large file upload fails
**Solution:** Increase `MAX_FILE_SIZE_MB` in `.env` and restart:
```bash
docker-compose restart backend
```

### Issue: Out of memory
**Solution:** Increase Docker memory limit or reduce `MAX_DOCUMENTS`

### Issue: Slow embedding generation
**Solution:** The first time embeddings are generated, the model needs to download. Subsequent runs will be faster.

## 📊 Performance

- **Document Processing**: ~2-5 seconds for 100 pages
- **Query Response**: ~1-3 seconds
- **Concurrent Users**: Supports 10+ simultaneous users
- **Storage**: ~1MB per 100 document pages

## 🔒 Security Notes

- Never commit `.env` file with API keys
- Use environment variables for sensitive data
- Implement authentication for production use
- Validate and sanitize all user inputs
- Set up rate limiting for API endpoints

## 🚀 Deployment

### Cloud Deployment (AWS/GCP/Azure)

1. **Set up MongoDB Atlas** (recommended for production)
2. **Update `.env`** with production values
3. **Deploy using Docker Compose** or Kubernetes
4. **Configure domain and SSL** using reverse proxy (nginx)

### Example: Deploy to AWS EC2

```bash
# SSH into EC2 instance
ssh -i key.pem ubuntu@your-ec2-ip

# Install Docker
sudo apt update
sudo apt install docker.io docker-compose -y

# Clone and configure
git clone 
cd rag-document-qa
nano .env  # Add production values

# Run
sudo docker-compose up -d
```

### Example: Deploy to Google Cloud Platform (GCP)

You can deploy in two common ways on GCP. If you want the simplest path that matches this repo’s docker-compose setup, use Compute Engine (VM). If you prefer serverless, use Cloud Run and deploy the backend and frontend as separate services.

#### Option A: Compute Engine (VM) with Docker Compose

1) Create a VM
- Go to GCP Console → Compute Engine → VM instances → Create instance
- Machine: e2-standard-2 (or similar), Ubuntu 22.04 LTS
- Firewall: Check "Allow HTTP" and "Allow HTTPS". Also open TCP 8000 and 8501 or put a reverse proxy in front (recommended for prod).

2) SSH into the VM and install Docker + Compose

```bash
sudo apt update -y
sudo apt install -y docker.io docker-compose git
sudo usermod -aG docker "$USER"
newgrp docker
```

3) Clone the repo and configure environment

```bash
git clone https://github.com/<your-org-or-user>/<your-repo>.git
cd <your-repo>

# Copy and edit env
cp .env.example .env
nano .env    # set GEMINI_API_KEY and MONGODB_URI (MongoDB Atlas recommended)
```

4) Start the stack

```bash
docker-compose up -d
```

5) Access
- Frontend (Streamlit): http://<vm-external-ip>:8501
- Backend API: http://<vm-external-ip>:8000
- Swagger docs: http://<vm-external-ip>:8000/docs

Notes
- This compose file runs frontend and backend on the same Docker network; the frontend uses `http://backend:8000` internally.
- For production hardening, put Nginx in front (port 80/443) → proxy to 8501 and 8000, add TLS via Let’s Encrypt.
- ChromaDB persists in `chroma_db/` (mounted volume); uploaded files persist under `backend/uploads/`.

#### Option B: Cloud Run (serverless) — optional

Cloud Run doesn’t run docker-compose; deploy the services separately:

1) Build and push two images (from repo root)

```bash
gcloud auth configure-docker

# Backend image
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/rag-backend ./backend

# Frontend image
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/rag-frontend ./frontend
```

2) Deploy Backend to Cloud Run

```bash
gcloud run deploy rag-backend \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/rag-backend \
  --platform managed \
  --region <your-region> \
  --allow-unauthenticated \
  --set-env-vars MONGODB_URI="<your-mongodb-uri>",MONGODB_DB_NAME="rag_documents",GEMINI_API_KEY="<your-gemini-key>",CHROMA_PERSIST_DIR="/tmp/chroma_db"
```

3) Deploy Frontend to Cloud Run (point it to backend URL)

```bash
BACKEND_URL="https://$(gcloud run services describe rag-backend --region <your-region> --format='value(status.url)')"

gcloud run deploy rag-frontend \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/rag-frontend \
  --platform managed \
  --region <your-region> \
  --allow-unauthenticated \
  --set-env-vars BACKEND_URL="$BACKEND_URL"
```

4) Access the frontend service URL printed by Cloud Run.

Important notes for Cloud Run
- Cloud Run storage is ephemeral; setting `CHROMA_PERSIST_DIR=/tmp/chroma_db` keeps data only for the lifetime of the instance. For persistence, consider:
  - Switching to a managed vector DB (e.g., Qdrant Cloud, Pinecone) OR
  - Running Chroma on a VM with attached disk (Compute Engine) OR
  - Using GKE with a PersistentVolume.
- Uploaded files should be stored in a durable location (e.g., Google Cloud Storage) in production. The current setup writes to local disk; for Cloud Run you’d adapt the upload code to write to GCS.

## 📝 License

MIT License - feel free to use for your projects!

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Support

For issues and questions:
- Open a GitHub issue
- Check existing issues first
- Provide detailed error messages and logs

---

**Built with ❤️ using FastAPI, LangChain, ChromaDB, and Gemini**