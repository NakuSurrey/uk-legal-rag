"""
Phase 3: FastAPI server for the RAG pipeline.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# from rag_chain import ask
# import sys
# import os
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_chain import ask

# from rag_chain import ask, initialize  # your existing import stays the same

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: list
    num_chunks: int

app = FastAPI(
    title="UK Legal RAG API",
    description="Ask questions about UK regulatory documents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Quick check that the server is running."""
    return {"status": "healthy"}

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

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)