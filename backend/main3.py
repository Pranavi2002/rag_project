"""
- async with raw input
"""

from fastapi import FastAPI
from pydantic import BaseModel
from rag_engine import add_documents, query_rag
from deepeval_utils import evaluate_rag
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI(title="Async RAG + DeepEval")

# CORS for frontend
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for answers/context
answers_cache = {}

# Request models
class Docs(BaseModel):
    texts: list[str]

class Question(BaseModel):
    question: str

# -----------------------------
# Upload documents endpoint
# -----------------------------
@app.post("/upload")
async def upload_docs(req: Docs):
    add_documents(req.texts)
    return {"status": "Documents added", "count": len(req.texts)}

# -----------------------------
# Query RAG endpoint (answer only)
# -----------------------------
@app.post("/query")
async def query(req: Question):
    # Generate RAG answer asynchronously
    answer, context, relevant = await asyncio.to_thread(query_rag, req.question)

    # If no relevant docs retrieved, override answer
    if not relevant:
        answer = "No relevant information found in the uploaded documents."

    # Store in cache for metrics evaluation
    answers_cache[req.question] = {"answer": answer, "context": context, "relevant": relevant}

    # Return answer immediately
    return {"question": req.question, "answer": answer, "context": context, "metrics": None}

# -----------------------------
# Metrics endpoint
# -----------------------------
@app.post("/metrics")
async def metrics(req: Question):
    cached = answers_cache.get(req.question)
    if not cached:
        return {"error": "No answer found for this question. Ask first."}

    if not cached["relevant"]:
        # Return 0% metrics for out-of-context queries
        eval_scores = {
            "FaithfulnessMetric": {"value": 0.0, "reason": "No relevant context retrieved.", "pass": False},
            "AnswerRelevancyMetric": {"value": 0.0, "reason": "No relevant context retrieved.", "pass": False},
        }
    else:
        # Compute metrics asynchronously
        eval_scores = await asyncio.to_thread(
            evaluate_rag, req.question, cached["answer"], cached["context"]
        )

    return {"question": req.question, "metrics": eval_scores}

# -----------------------------
# Health check
# -----------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}