# UK Legal/Regulatory Document Q&A Assistant

**Production-Ready RAG Pipeline | Cloud Deployed | Built for UK Placement Applications**

![Python 3.10](https://img.shields.io/badge/Python-3.10-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white) ![License: MIT](https://img.shields.io/badge/License-MIT-green)

---

## What This Project Does

This is an end-to-end **Retrieval-Augmented Generation (RAG)** system that allows users to ask natural language questions about UK regulatory documents and receive accurate, fact-checked answers with source citations.

### [Live Demo → uklegalrag.me](http://uklegalrag.me)

Think of it as a **custom ChatGPT trained on UK legal documents** that can't hallucinate — if the answer isn't in the documents, it says "I don't know" instead of making things up.

Users can also **upload their own PDFs** and query them alongside pre-loaded UK regulatory data in real time.

---

## Architecture

```
┌─────────────┐
│   User      │
│ (Browser)   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────────────────┐
│  Streamlit Frontend (Port 80)   │  ◄── Chat UI, PDF Upload, Source Display
└────────────┬────────────────────┘
             │ POST /ask, /upload, /cleanup
             ▼
┌─────────────────────────────────┐
│   FastAPI Backend               │  ◄── REST API, Request Validation
└────────────┬────────────────────┘
             │
             ├─► ChromaDB ──────────► Retrieve Top 4 Chunks
             │   (Vector Database)
             │
             └─► Hugging Face API ──► Meta-Llama-3-8B-Instruct
                 (LLM Inference)
```

**Data Flow:**

1. User asks: *"What are the changes to zero hours contracts?"*
2. Streamlit sends question to FastAPI
3. FastAPI converts question to vector → searches ChromaDB for similar paragraphs
4. Top 4 relevant paragraphs sent to LLM with strict system prompt
5. LLM generates answer using **ONLY** the provided context
6. Answer + source citations returned to user

---

## Why This Project Matters

**Business Value:** Enterprises have thousands of pages of compliance documents, HR policies, and regulatory handbooks. Employees waste hours manually searching through PDFs. This system reduces that search time from hours to seconds.

**Technical Achievement:** This isn't just an API call to ChatGPT. It demonstrates:

- **Data engineering** — PDF parsing, text chunking, vector embeddings
- **Backend development** — RESTful API with FastAPI, async-ready endpoints
- **Frontend development** — Streamlit chat UI with session state management
- **MLOps** — Docker containerisation, cloud deployment, process management
- **Production considerations** — error handling, conversation memory, anti-hallucination safeguards, dynamic document ingestion

---

## Tech Stack

| Layer | Technology | Why This Choice |
|-------|-----------|-----------------|
| LLM | Meta-Llama-3-8B-Instruct (HF Inference API) | Free tier, production-quality responses |
| Embeddings | all-MiniLM-L6-v2 (Sentence Transformers) | Runs locally, no API costs, fast inference |
| Vector DB | ChromaDB | Persistent storage, built-in similarity search |
| Backend | FastAPI | Auto-generated Swagger docs, async support |
| Frontend | Streamlit | Rapid prototyping, built-in chat components |
| Parsing | PyMuPDF | Handles complex table layouts better than PyPDF2 |
| Orchestration | LangChain | Industry-standard RAG framework |
| Containerisation | Docker + supervisord | Single-container deployment, process management |
| Cloud | DigitalOcean Droplet | Student credits, predictable pricing, full control |

---

## Features

- **Conversational Q&A** with 5-exchange memory for follow-up questions
- **Source citations** displayed with every answer (expandable panel)
- **Anti-hallucination safeguards** — refuses to answer questions outside document scope
- **Dynamic PDF upload** — users can upload their own documents for real-time indexing
- **Session-scoped uploads** — uploaded documents are temporary and cleared on cleanup
- **Backend health monitoring** — sidebar indicator shows connection status
- **Legal disclaimer** prominently displayed in UI

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Deployment Status | ✅ Live at [uklegalrag.me](http://uklegalrag.me) |
| Chunk Retrieval Time | ~200ms |
| End-to-End Response Time | 2–8 seconds |
| Database Size | 32 chunks (12-page UK Employment Rights PDF) |
| Anti-Hallucination Rate | 100% tested |
| Conversation Memory | 5 exchanges |
| Cost per 1,000 queries | £0 (free tier) |

---

## Key Engineering Challenges Solved

This project forced me to solve real production challenges:

- **Dependency conflicts** — Resolved complex version conflicts between `langchain-huggingface`, `transformers`, and `huggingface_hub` during Docker builds
- **Path resolution** — Fixed ChromaDB loading failures across different working directories using `os.path.dirname(__file__)`
- **CORS configuration** — Added middleware to enable frontend-backend communication
- **Session state management** — Implemented persistent chat history in Streamlit's stateless re-run model
- **Cold start optimisation** — Pre-populated vector database during Docker build (19.6s) to avoid runtime delays
- **Import path resolution** — Debugged FastAPI crash-loop caused by `ModuleNotFoundError` in containerised environment
- **Orphaned data cleanup** — Solved session-scoped ChromaDB chunk management for dynamic PDF uploads
- **Cost control** — Set hard API billing limits to prevent runaway costs

---

## Getting Started (Local Development)

### Prerequisites

- Python 3.10+
- Docker Desktop (for containerised testing)
- Hugging Face account (free tier)

### Setup

```bash
# Clone the repository
git clone https://github.com/NakuSurrey/uk-legal-rag.git
cd uk-legal-rag

# Create virtual environment
python -m venv venv
source venv/Scripts/activate   # Git Bash on Windows
# OR: venv\Scripts\activate    # PowerShell

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo "HUGGINGFACE_API_KEY=hf_your_key_here" > .env

# Build the vector database (one-time)
python src/build_db.py

# Terminal 1 — Start backend
cd src && python api.py

# Terminal 2 — Start frontend
cd src && streamlit run app.py
```

Visit `http://localhost:8501` to use the app.

### Docker (Local)

```bash
docker build -t uk-legal-rag .
docker run -p 5000:8000 -p 5001:8501 --env-file .env uk-legal-rag
```

Visit `http://localhost:5001`

---

## Project Structure

```
uk-legal-rag/
├── src/
│   ├── pdf_loader.py      # PyMuPDF document reader
│   ├── chunker.py         # Text splitting with overlap
│   ├── vectorstore.py     # ChromaDB embedding & storage
│   ├── rag_chain.py       # LLM integration, conversation memory, PDF ingestion
│   ├── api.py             # FastAPI REST endpoints (/ask, /upload, /cleanup)
│   ├── app.py             # Streamlit chat UI with upload support
│   └── build_db.py        # Database pre-population script
├── data/                  # UK regulatory PDFs
├── tests/                 # Evaluation scripts
├── Dockerfile             # Container build recipe
├── supervisord.conf       # Process manager (FastAPI + Streamlit)
├── requirements.txt       # Python dependencies
├── .dockerignore
├── .gitignore
└── README.md
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Server health check |
| `/ask` | POST | Submit a question, receive answer + sources |
| `/upload` | POST | Upload a PDF for real-time indexing |
| `/cleanup` | POST | Remove all uploaded document chunks |
| `/docs` | GET | Interactive Swagger UI |

---

## Security & Best Practices

- API keys never committed to Git (`.env` in `.gitignore`)
- ChromaDB excluded from version control (regenerated from source)
- Hard billing limits set on API accounts
- Anti-hallucination system prompt enforced
- Legal disclaimer displayed in UI
- CORS properly configured
- Docker image optimised (slim base, layer caching, `.dockerignore`)
- WHOIS privacy enabled on domain

---

## Known Limitations & Future Improvements

**Current Limitations:**
- Free-tier LLM occasionally too conservative with anti-hallucination prompt
- Source metadata shows 'Unknown' (PDF metadata not enriched during ingestion)
- Single-language support (English only)
- Cold start delays on free HF Inference API (30–60s after inactivity)

**Planned Enhancements:**
- Hybrid Search (BM25 + vector similarity) for exact-match queries
- Semantic Chunking (split at natural paragraph/heading breaks)
- Async endpoints in FastAPI for concurrent user support
- RAGAS evaluation framework for automated quality metrics
- Metadata filtering (filter by document date, type, section)
- Document reordering to combat "lost in the middle" problem

---

## Try It Yourself

**[Live Demo → uklegalrag.me](http://uklegalrag.me)**

Test questions to try:
1. *"What are the changes to zero hours contracts?"* — factual question
2. *"When do these changes take effect?"* — follow-up (tests conversation memory)
3. *"What is the capital of France?"* — anti-hallucination test (should refuse)

---

## License

MIT License — See [LICENSE](LICENSE) file for details.

---

## Contact

**Nakul** — MSc Artificial Intelligence, University of Surrey

GitHub: [@NakuSurrey](https://github.com/NakuSurrey)

---

*Built as a portfolio piece demonstrating production-ready AI engineering for UK placement applications.*
