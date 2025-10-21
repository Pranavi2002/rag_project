"""
- with ragas, synchronous with deepeval
"""

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from rag_engine import add_documents, query_rag, extract_text_from_file
from deepeval_utils import evaluate_rag
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from ragas_engine import ragas_generate

app = FastAPI(title="Async RAG + DeepEval + RAGAS")

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
# Upload plain text documents
# -----------------------------
@app.post("/upload")
async def upload_docs(req: Docs):
    add_documents(req.texts)
    return {"status": "Documents added", "count": len(req.texts)}


# -----------------------------
# Upload PDF / TXT files
# -----------------------------
@app.post("/upload_files")
async def upload_files(files: list[UploadFile] = File(...)):
    all_texts = []
    filenames = []

    for file in files:
        try:
            content = await file.read()
            extracted_text = extract_text_from_file(file.filename, content)
        except Exception as e:
            print(f"Error reading file {file.filename}: {e}")
            continue

        if extracted_text.strip():  # only add if text is not empty
            all_texts.append(extracted_text)
            filenames.append(file.filename)
        else:
            print(f"No text extracted from {file.filename}")

    if not all_texts:
        # Return 200 with a proper message so frontend can handle it gracefully
        return {"status": "No valid text extracted from uploaded files."}

    print(f"Adding documents: {filenames}")
    add_documents(all_texts, filenames=filenames)
    return {"status": "Files processed", "count": len(all_texts), "files": filenames}

# -----------------------------
# Remove uploaded documents
# -----------------------------
from rag_engine import remove_documents  # create this in rag_engine.py

@app.post("/remove_files")
async def remove_files(filenames: list[str]):
    removed_files = remove_documents(filenames)
    if not removed_files:
        return {"status": "No documents removed. Check filenames."}
    return {"status": f"Removed {', '.join(removed_files)} successfully."}

# -----------------------------
# Query RAG endpoint (answer only)
# -----------------------------
@app.post("/query")
async def query_ragas(req: Question):
    answer, context, reasoning, relevant = await ragas_generate(req.question)

    if not relevant:
        answer = "No relevant information found in the uploaded documents."

    # Save initial response in cache
    answers_cache[req.question] = {
        "answer": answer,
        "context": context,
        "relevant": relevant,
        "metrics": None,
        "reasoning": None
    }

    return {
        "question": req.question,
        "answer": answer,
        "context": context,
        "message": "Metrics and reasoning will appear shortly.",
    }

# -----------------------------
# Metrics endpoint
# -----------------------------
@app.post("/metrics")
async def metrics(req: Question):
    cached = answers_cache.get(req.question)
    if not cached:
        return {"error": "No answer found for this question. Ask first."}

    if not cached["relevant"]:
        eval_scores = {
            "FaithfulnessMetric": {"value": 0.0, "reason": "No relevant context retrieved.", "pass": False},
            "AnswerRelevancyMetric": {"value": 0.0, "reason": "No relevant context retrieved.", "pass": False},
        }
    else:
        eval_scores = cached["metrics"] if cached["metrics"] else None

    return {
        "question": req.question,
        "metrics": eval_scores,
        "reasoning": cached.get("reasoning")
    }

# -----------------------------
# Health check
# -----------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}