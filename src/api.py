"""
Phase 3: FastAPI server for the RAG pipeline.
Wraps the ask() function from rag_chain.py into a REST API endpoint.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import your working RAG chain from Phase 2
from rag_chain import ask

# --- Request/Response Models ---
class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: list
    num_chunks: int

# --- Create the FastAPI app ---
app = FastAPI(
    title="UK Legal RAG API",
    description="Ask questions about UK regulatory documents",
    version="1.0.0"
)

# --- CORS Middleware (THE TRAP FIX) ---
# Without this, your Streamlit frontend will REFUSE to talk to this backend.
# The error messages are incredibly confusing for beginners.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins (fine for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """Quick check that the server is running."""
    return {"status": "healthy"}

# --- Main Q&A Endpoint ---
@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Receives a question, runs it through the RAG pipeline,
    returns the answer with sources.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = ask(request.question)
        return AnswerResponse(
            answer=result["answer"],
            sources=result["sources"],
            num_chunks=result["num_chunks"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG pipeline error: {str(e)}")

# --- Run the server ---
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)