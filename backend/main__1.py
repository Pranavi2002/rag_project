"""
- async ragas and deepeval
- both ragas metrics + deepeval metrics
- includes ragas reasoning
"""

import asyncio
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from rag_engine import add_documents, remove_documents, extract_text_from_file
from ragas_engine import ragas_generate, evaluate_ragas
from deepeval_utils import evaluate_rag
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Async RAG + DeepEval + RAGAS")

# -----------------------------
# CORS
# -----------------------------
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Cache
# -----------------------------
answers_cache = {}

# -----------------------------
# Models
# -----------------------------
class Docs(BaseModel):
    texts: list[str]

class Question(BaseModel):
    question: str


# -----------------------------
# Upload documents
# -----------------------------
@app.post("/upload")
async def upload_docs(req: Docs):
    add_documents(req.texts)
    return {"status": "Documents added", "count": len(req.texts)}

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

        if extracted_text.strip():
            all_texts.append(extracted_text)
            filenames.append(file.filename)

    if not all_texts:
        return {"status": "No valid text extracted from uploaded files."}

    add_documents(all_texts, filenames=filenames)
    return {"status": "Files processed", "count": len(all_texts), "files": filenames}


# -----------------------------
# Remove uploaded documents
# -----------------------------
@app.post("/remove_files")
async def remove_files(filenames: list[str]):
    removed_files = remove_documents(filenames)
    if not removed_files:
        return {"status": "No documents removed. Check filenames."}
    return {"status": f"Removed {', '.join(removed_files)} successfully."}


# -----------------------------
# Query endpoint (RAGAS reasoning)
# -----------------------------
@app.post("/query")
async def query_ragas(req: Question):
    # Generate RAGAS reasoning + answer
    answer, context, reasoning, relevant = await ragas_generate(req.question)

    # Cache everything
    answers_cache[req.question] = {
        "answer": answer,
        "context": context,
        "relevant": relevant,
        "deepeval_metrics": None,
        "ragas_metrics": None,
        "reasoning": reasoning,
    }

    return {
        "question": req.question,
        "answer": answer,
        "context": context,
        "reasoning": reasoning,
        "deepeval_metrics": None,
        "ragas_metrics": None,
        "message": "Metrics will appear shortly.",
    }


# -----------------------------
# Metrics endpoint (DeepEval + RAGAS)
# -----------------------------
@app.post("/metrics")
async def metrics(req: Question):
    cached = answers_cache.get(req.question)
    if not cached:
        return {"error": "No answer found for this question. Ask first."}

    if not cached["relevant"]:
        return {
            "deepeval_metrics": {
                "FaithfulnessMetric": {"value": 0.0, "reason": "No relevant context retrieved.", "pass": False},
                "AnswerRelevancyMetric": {"value": 0.0, "reason": "No relevant context retrieved.", "pass": False},
            },
            "ragas_metrics": None,
            "reasoning": cached.get("reasoning"),
        }

    # If metrics are already cached → return instantly
    if cached["deepeval_metrics"] and cached["ragas_metrics"]:
        return {
            "deepeval_metrics": cached["deepeval_metrics"],
            "ragas_metrics": cached["ragas_metrics"],
            "reasoning": cached.get("reasoning"),
        }

    # Otherwise → run evaluations concurrently
    question = req.question
    answer = cached["answer"]
    contexts = cached["context"]
    reference = cached.get("reasoning")  # this acts as RAGAS reference

    deepeval_task = asyncio.create_task(evaluate_rag(question, answer, contexts))
    ragas_task = asyncio.create_task(evaluate_ragas(question, answer, contexts, reference))

    deepeval_result, ragas_result = await asyncio.gather(deepeval_task, ragas_task)

    # Cache metrics
    cached["deepeval_metrics"] = deepeval_result
    cached["ragas_metrics"] = ragas_result

    return {
        "deepeval_metrics": deepeval_result,
        "ragas_metrics": ragas_result,
        "reasoning": cached.get("reasoning"),
    }


# -----------------------------
# Health check
# -----------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}