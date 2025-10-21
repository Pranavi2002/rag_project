"""
- async ragas and deepeval
- only ragas reasoning
"""

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from rag_engine import add_documents, remove_documents, extract_text_from_file
from ragas_engine import ragas_generate
from fastapi.middleware.cors import CORSMiddleware
from cache import answers_cache

app = FastAPI(title="Async RAG + DeepEval + RAGAS")

# CORS
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
    answer, context, reasoning, relevant = await ragas_generate(req.question)

    # Save initial response in cache
    answers_cache[req.question] = {
        "answer": answer,
        "context": context,
        "relevant": relevant,
        "metrics": None,       # metrics will be updated asynchronously
        "reasoning": reasoning
    }

    return {
        "question": req.question,
        "answer": answer,
        "context": context,
        "reasoning": reasoning,
        "metrics": None,        # frontend will poll /metrics
        "message": "Metrics and reasoning will appear shortly."
    }


# -----------------------------
# Metrics endpoint (DeepEval)
# -----------------------------
@app.post("/metrics")
async def metrics(req: Question):
    cached = answers_cache.get(req.question)
    if not cached:
        return {"error": "No answer found for this question. Ask first."}

    metrics = cached.get("metrics")
    reasoning = cached.get("reasoning")

    # Show partial metrics if computation is still ongoing
    deepeval = metrics.get("DeepEval") if metrics else None
    ragas = metrics.get("RAGAS") if metrics else None

    return {
        "question": req.question,
        "metrics": {
            "DeepEval": deepeval if deepeval else "Computing...",
            "RAGAS": ragas if ragas else "Computing..."
        },
        "reasoning": reasoning
    }

# -----------------------------
# Health check
# -----------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}