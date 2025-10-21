"""
FastAPI app to serve RAG system
- /upload : add documents
- /query  : ask questions, return answer + metrics asynchronously
but hallucinated answers
"""

from fastapi import FastAPI
from pydantic import BaseModel
from rag_engine import add_documents, query_rag
from deepeval_utils import evaluate_rag
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI(title="Async RAG + DeepEval")

# CORS setup for frontend
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for answers (question → {answer, context})
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
    answer, context = await asyncio.to_thread(query_rag, req.question)

    # Store in cache for metrics evaluation
    answers_cache[req.question] = {"answer": answer, "context": context}

    # Return answer immediately
    return {"question": req.question, "answer": answer, "context": context, "metrics": None}

# -----------------------------
# Metrics endpoint (evaluate separately)
# -----------------------------
@app.post("/metrics")
async def metrics(req: Question):
    cached = answers_cache.get(req.question)
    if not cached:
        return {"error": "No answer found for this question. Ask first."}

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

# query_rag(question) is called in a separate thread, 
# but it always generates an answer using the LLM.

# Even if there’s no relevant document in your indexed context, 
# the LLM will still produce a plausible answer based on its pretrained knowledge.

# The answer is returned immediately to the frontend.

# Metrics are calculated separately after the answer is already 
# returned.

# evaluate_rag currently doesn’t enforce a check on empty or 
# irrelevant context, so even when the context doesn’t contain the 
# requested info:

# Faithfulness: “No contradictions found” → scored 100%

# Relevance: Some implementations consider an answer that matches 
# some part of context or is non-contradictory → scored 100%


# Example: “Explain quantum mechanics”

# Context: ["This is a test doc about AI.", "Another document about football."]

# LLM input: query_rag doesn’t limit the LLM strictly to context. 
# The LLM knows about quantum mechanics from pretraining → it just 
# generates a detailed answer.

# DeepEval scoring: It looks at the retrieved context (football + AI) 
# vs answer:

# Faithfulness: No contradictions detected → 100%

# Relevance: Depending on implementation, relevance can be mis-scored
# as 100% if no strict negative checks exist.

# ✅ Result: Even though the answer is hallucinated, the metrics 
# wrongly say it’s fully faithful and relevant.