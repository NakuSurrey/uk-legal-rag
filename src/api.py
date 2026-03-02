"""
Phase 3: FastAPI server for the RAG pipeline.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, UploadFile, File
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
    
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), session_id: str = "default"):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
        
        pdf_bytes = await file.read()
        
        if len(pdf_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")
        
        if len(pdf_bytes) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum 50MB.")
        
        from rag_chain import ingest_pdf_bytes
        result = ingest_pdf_bytes(pdf_bytes, file.filename, session_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "message": f"Successfully processed {file.filename}",
            "chunks_added": result["chunks_added"],
            "filename": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@app.post("/cleanup")
async def cleanup_session(session_id: str = "default"):
    try:
        from rag_chain import cleanup_session_chunks
        result = cleanup_session_chunks(session_id)
        return {
            "message": f"Cleaned up {result['chunks_removed']} uploaded chunks",
            "chunks_removed": result["chunks_removed"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

# @app.get("/debug_db")
# async def debug_db():
#     from rag_chain import vectorstore
#     collection = vectorstore._collection
#     count = collection.count()
#     # Get all chunks with "uploaded" metadata
#     all_data = collection.get(include=["metadatas"])
#     # uploaded = [m for m in all_data["metadatas"] if m.get("uploaded") == "true"]
#     uploaded = [m for m in all_data["metadatas"] if m and m.get("uploaded") == "true"]
#     return {
#         "total_chunks": count,
#         "uploaded_chunks": len(uploaded),
#         "uploaded_details": uploaded[:5]  # Show first 5
#     }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)