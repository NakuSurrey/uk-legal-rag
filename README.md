# UK Legal/Regulatory Document Q&A Assistant

> **Production-Ready RAG Pipeline** | Deployed on DigitalOcean | Built for UK Placement Applications

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-enabled-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What This Project Does

This is an **end-to-end Retrieval-Augmented Generation (RAG) system** that allows users to ask natural language questions about UK regulatory documents and receive accurate, fact-checked answers with source citations.

**🚀 Live Demo:** http://167.71.142.107

Think of it as a custom ChatGPT trained on UK legal documents that can't hallucinate — if the answer isn't in the documents, it says "I don't know" instead of making things up.

---

## 🏗️ Architecture

```
┌─────────────┐
│   User      │
│ (Browser)   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────────────────┐
│  Streamlit Frontend (Port 8501) │  ◄── Chat UI, Source Display
└────────────┬────────────────────┘
             │ POST /ask
             ▼
┌─────────────────────────────────┐
│   FastAPI Backend (Port 8000)   │  ◄── REST API, Request Routing
└────────────┬────────────────────┘
             │
             ├─► ChromaDB ──────────► Retrieve Top 4 Chunks
             │   (Vector Database)
             │
             └─► Hugging Face API ──► Meta-Llama-3-8B-Instruct
                 (LLM Inference)
```

**Data Flow:**
1. User asks: "What are the changes to zero hours contracts?"
2. Streamlit sends question to FastAPI
3. FastAPI converts question to vector → searches ChromaDB for similar paragraphs
4. Top 4 relevant paragraphs sent to LLM with strict system prompt
5. LLM generates answer using ONLY the provided context
6. Answer + source citations returned to user

---

## 🚀 Why This Project Matters

**Business Value:** Enterprises have thousands of pages of compliance documents, HR policies, and regulatory handbooks. Employees waste hours manually searching through PDFs. This system reduces that search time from hours to seconds.

**Technical Achievement:** This isn't just an API call to ChatGPT. It demonstrates:
- Data engineering (PDF parsing, text chunking, vector embeddings)
- Backend development (RESTful API with FastAPI)
- Frontend development (Streamlit chat UI)
- MLOps (Docker containerization, cloud deployment, cost optimization)
- Production considerations (error handling, conversation memory, anti-hallucination safeguards)

---

## 🛠️ Tech Stack

| Layer | Technology | Why This Choice |
|-------|-----------|----------------|
| **LLM** | Meta-Llama-3-8B-Instruct (HF Inference API) | Free tier, production-quality responses, conversational capability |
| **Embeddings** | all-MiniLM-L6-v2 (Sentence Transformers) | Runs locally, no API costs, fast inference |
| **Vector DB** | ChromaDB | Persistent storage, built-in similarity search, lightweight |
| **Backend** | FastAPI | Auto-generated Swagger docs, async support, production-ready |
| **Frontend** | Streamlit | Rapid prototyping, built-in chat components, recruiter-friendly UI |
| **Parsing** | PyMuPDF | Handles complex table layouts better than PyPDF2 |
| **Orchestration** | LangChain | Industry-standard RAG framework, conversation memory |
| **Containerization** | Docker + supervisord | Single-container deployment, process management |
| **Cloud** | DigitalOcean Droplet (2GB RAM) | Student credits, predictable pricing, full control |

---

## 📊 Performance Metrics

| Metric | Value | How Measured |
|--------|-------|-------------|
| **Deployment Status** | ✅ Live | http://167.71.142.107 |
| **Chunk Retrieval Time** | ~200ms | Average latency for vector search |
| **End-to-End Response Time** | 2-8 seconds | Question → Answer (varies with LLM cold starts) |
| **Database Size** | 32 chunks | From 12-page UK Employment Rights PDF |
| **Anti-Hallucination Rate** | 100% tested | Refuses to answer questions outside document scope |
| **Conversation Memory** | 5 exchanges | Maintains context for follow-up questions |
| **Cost per 1000 queries** | £0 (free tier) | HF Inference API + local embeddings |

---

## 🎓 Key Learning Outcomes

This project forced me to solve real production challenges:

1. **Dependency Hell:** Resolved complex version conflicts between `langchain-huggingface`, `transformers`, and `huggingface_hub` during Docker builds by switching to unpinned dependencies
2. **Absolute vs Relative Paths:** Fixed ChromaDB loading failures when running code from different directories using `os.path.dirname(__file__)`
3. **CORS Configuration:** Added middleware to allow frontend-backend communication
4. **Session State Management:** Implemented persistent chat history in Streamlit's stateless re-run model
5. **Cold Start Optimization:** Pre-populated vector database during Docker build (19.6s) to avoid runtime delays
6. **Import Path Issues:** Debugged FastAPI crash-loop caused by `ModuleNotFoundError` — added `sys.path.insert` for proper module resolution
7. **Cost Control:** Set hard API billing limits to prevent surprise charges from spam/abuse

---

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- Docker Desktop (for local testing)
- Hugging Face account (free tier)

### Local Setup (Development)

```bash
# 1. Clone the repository
git clone https://github.com/NakuSurrey/uk-legal-rag.git
cd uk-legal-rag

# 2. Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Git Bash on Windows
# OR
venv\Scripts\activate         # PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
echo "HUGGINGFACE_API_KEY=hf_your_key_here" > .env

# 5. Build the vector database (one-time setup)
python src/build_db.py

# 6. Run FastAPI backend (Terminal 1)
cd src
python api.py

# 7. Run Streamlit frontend (Terminal 2 — new window)
cd src
streamlit run app.py
```

Visit `http://localhost:8501` to use the app.

---

## 🐳 Docker Deployment

### Build and Run Locally
```bash
# Build the image
docker build -t uk-legal-rag .

# Run the container (Windows — ports 5000/5001 to avoid Windows exclusion ranges)
docker run -p 5000:8000 -p 5001:8501 --env-file .env uk-legal-rag
```

Visit `http://localhost:5001`

### Deploy to DigitalOcean

```bash
# 1. SSH into your droplet
ssh root@167.71.142.107

# 2. Clone and setup
git clone https://github.com/NakuSurrey/uk-legal-rag.git
cd uk-legal-rag
nano .env  # Add your HUGGINGFACE_API_KEY

# 3. Build and run
docker build -t uk-legal-rag .
docker run -d -p 80:8501 -p 8000:8000 --env-file .env --restart always uk-legal-rag
```

Your app is now live at http://167.71.142.107

---

## 📁 Project Structure

```
uk-legal-rag/
├── src/
│   ├── pdf_loader.py      # PyMuPDF document reader
│   ├── chunker.py         # Text splitting with overlap
│   ├── vectorstore.py     # ChromaDB embedding & storage
│   ├── rag_chain.py       # LLM integration + conversation memory
│   ├── api.py             # FastAPI REST endpoints
│   ├── app.py             # Streamlit chat UI
│   └── build_db.py        # Database pre-population script
├── data/                  # UK regulatory PDFs
├── tests/                 # Evaluation scripts
├── Dockerfile             # Container build recipe
├── supervisord.conf       # Process manager (FastAPI + Streamlit)
├── requirements.txt       # Python dependencies
├── .dockerignore          # Files excluded from Docker build
├── .gitignore            # Files excluded from Git
└── README.md             # This file
```

---

## 🔒 Security & Best Practices

- ✅ **API keys never committed to Git** (`.env` in `.gitignore`)
- ✅ **ChromaDB excluded from version control** (too large, regenerated from source)
- ✅ **Hard billing limits set** on HF account (prevents runaway costs)
- ✅ **Anti-hallucination system prompt** (refuses to answer outside document scope)
- ✅ **Legal disclaimer** prominently displayed in UI
- ✅ **CORS properly configured** (allows legitimate frontend access only)
- ✅ **Docker image optimized** (slim base, layer caching, .dockerignore)

---

## 🐛 Known Limitations & Future Improvements

### Current Limitations
1. **Free-tier LLM occasionally too conservative:** The anti-hallucination prompt is aggressive — sometimes refuses valid questions. Tuning needed.
2. **Source metadata shows 'Unknown':** PDF metadata not enriched during ingestion. Only text previews are shown.
3. **Single-language support:** Currently English only.
4. **Cold start delays:** Free HF Inference API has 30-60s cold starts after inactivity.

### Planned Enhancements
- [ ] Implement **Hybrid Search** (BM25 + vector similarity) for exact-match queries
- [ ] Add **Semantic Chunking** (split at natural paragraph/heading breaks)
- [ ] Upgrade to **async endpoints** in FastAPI for concurrent user support
- [ ] Integrate **RAGAS evaluation framework** for automated quality metrics
- [ ] Add **metadata filtering** (filter by document date, type, section)
- [ ] Implement **document reordering** (combat "lost in the middle" problem)

---

## 💼 Commercial Awareness

**Cost Breakdown (Monthly):**
- DigitalOcean Droplet (2GB): $12/month → Covered by $200 GitHub Student Pack credits (16+ months free)
- Hugging Face Inference API: $0 (free tier, 30 req/hour limit)
- Total operational cost: **$0 during student period**

**If scaling to production:**
- Upgrade HF to Pro ($9/mo) for faster responses and no cold starts
- OR switch to OpenAI API (~$0.50 per 1000 queries)
- Total: **$12-21/month** for hundreds of daily users

**Alternative cost-saving strategy:** Host on Hugging Face Spaces (free 2GB RAM) if DigitalOcean credits expire.

---

## 🎯 Try It Yourself

**Live Demo:** http://167.71.142.107

**Test Questions:**
1. "What are the changes to zero hours contracts?" (factual question)
2. "When do these changes take effect?" (follow-up — tests conversation memory)
3. "What is the capital of France?" (anti-hallucination test — should refuse)

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- UK regulatory documents sourced from [GOV.UK](https://www.gov.uk/)
- Built following enterprise RAG best practices from LangChain documentation
- Deployment guide inspired by DigitalOcean's Docker deployment tutorials
- Project structure designed to meet UK placement year employer expectations

---

## 📫 Contact

**Nakul** - MSc Artificial Intelligence Student, University of Surrey  
GitHub: [@NakuSurrey](https://github.com/NakuSurrey)  
Email: na02153@surrey.ac.uk

*This project was built as a portfolio piece demonstrating production-ready AI engineering *

---

## 🌟 Star This Repository

If you found this project useful or learned something from the code, please consider giving it a star ⭐ on GitHub!
