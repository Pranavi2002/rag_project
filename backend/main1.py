"""
FastAPI app to serve RAG system
- /upload : add documents
- /query  : ask questions, return answer + metrics synchronously
"""

from fastapi import FastAPI
from pydantic import BaseModel
from rag_engine import add_documents, query_rag
from deepeval_utils import evaluate_rag
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Simple RAG + DeepEval API")  # Create app first

# CORS setup for frontend
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class Docs(BaseModel):
    texts: list[str]

class Question(BaseModel):
    question: str

# Endpoint to upload documents
@app.post("/upload")
def upload_docs(req: Docs):
    add_documents(req.texts)
    return {"status": "Documents added", "count": len(req.texts)}

# Endpoint to query RAG
@app.post("/query")
def query(req: Question):
    # Generate answer from RAG
    answer, context = query_rag(req.question)

    # Evaluate answer with DeepEval
    eval_scores = evaluate_rag(req.question, answer, context)

    return {
        "question": req.question,
        "answer": answer,
        "context": context,
        "metrics": eval_scores
    }

# Simple health check
@app.get("/health")
def health():
    return {"status": "ok"}