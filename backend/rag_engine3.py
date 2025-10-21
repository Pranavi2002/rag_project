"""
- async with raw, text, pdf upload and removal
- summarization metric is very low making the test fail
- short answer
"""

from openai import OpenAI
import numpy as np
import faiss
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
import io
import textwrap

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- In-memory storage ---
documents = []  # now store as dict: {"filename": str, "chunk": str}
embeddings = None
index = None


# -----------------------------
# Helper: Extract text from PDF or TXT
# -----------------------------
def extract_text_from_file(filename: str, content: bytes) -> str:
    text = ""
    try:
        if filename.lower().endswith(".pdf"):
            reader = PdfReader(io.BytesIO(content))
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
        elif filename.lower().endswith(".txt"):
            text = content.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
    return text.strip()

# -----------------------------
# Helper: Chunk large text
# -----------------------------
def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]

# -----------------------------
# Add documents to FAISS (with filename tracking)
# -----------------------------
def add_documents(docs: list[str], filenames: list[str] = None):
    """
    docs: list of raw text or extracted text
    filenames: list of filenames corresponding to docs (optional)
    """
    global documents, embeddings, index

    expanded_docs = []
    doc_records = []

    for i, d in enumerate(docs):
        chunks = chunk_text(d)
        expanded_docs.extend(chunks)

        # Track filenames per chunk
        fname = filenames[i] if filenames and i < len(filenames) else f"doc_{len(documents)+i}"
        for chunk in chunks:
            doc_records.append({"filename": fname, "chunk": chunk})

    documents.extend(doc_records)

    # Generate embeddings for all new chunks
    doc_embeds = [
        client.embeddings.create(model="text-embedding-3-small", input=doc["chunk"]).data[0].embedding
        for doc in doc_records
    ]
    doc_embeds = np.array(doc_embeds).astype("float32")

    if embeddings is None:
        embeddings = doc_embeds
        index = faiss.IndexFlatL2(len(doc_embeds[0]))
        index.add(embeddings)
    else:
        index.add(doc_embeds)

# -----------------------------
# Remove documents by filenames
# -----------------------------
def remove_documents(filenames: list[str]):
    """
    Remove documents by their original filenames.
    Returns list of removed filenames.
    """
    global documents, embeddings, index

    filenames_set = set(filenames)
    removed_files = set(doc["filename"] for doc in documents if doc["filename"] in filenames_set)

    # Remove the documents
    documents = [doc for doc in documents if doc["filename"] not in filenames_set]

    # Rebuild FAISS index
    if documents:
        doc_embeds = [
            client.embeddings.create(model="text-embedding-3-small", input=doc["chunk"]).data[0].embedding
            for doc in documents
        ]
        doc_embeds = np.array(doc_embeds).astype("float32")
        embeddings = doc_embeds
        index = faiss.IndexFlatL2(len(doc_embeds[0]))
        index.add(embeddings)
    else:
        embeddings = None
        index = None

    return list(removed_files)

# -----------------------------
# Query RAG
# -----------------------------
def query_rag(question: str, k: int = 3, max_sentences_per_chunk: int = 2):
    """
    Retrieve relevant chunks from FAISS, show concise context with filenames,
    and generate an answer using GPT-3.5-turbo.
    """
    global index, documents
    if not documents:
        return "", [], False

    # Get question embedding
    q_embed = client.embeddings.create(
        model="text-embedding-3-small", input=question
        ).data[0].embedding
    q_embed = np.array([q_embed]).astype("float32")

    # Search in FAISS
    D, I = index.search(q_embed, k)
    retrieved = [documents[i] for i in I[0]]  # documents[i] is a dict {"filename":..., "chunk":...}

    # Function to extract first N sentences from a chunk
    def summarize_chunk(chunk, max_sentences=max_sentences_per_chunk):
        sentences = chunk.split(". ")
        return ". ".join(sentences[:max_sentences]) + ("" if len(sentences) <= max_sentences else "...")

    # Prepare context list with filenames for frontend display
    
    # retrieved_context = [f"[{doc['filename']}] {doc['chunk']}" for doc in retrieved]

    # to limit the context text
    seen_files = set()
    retrieved_context = []
    for doc in retrieved:
        if doc["filename"] not in seen_files:
            short_chunk = summarize_chunk(doc["chunk"])
            retrieved_context.append(f"[{doc['filename']}] {short_chunk}")
            seen_files.add(doc["filename"])

    relevant = len(retrieved_context) > 0 and any(c.strip() for c in retrieved_context)

    if not relevant:
        return "", retrieved_context, False

    # Combine chunks for the prompt
    context_text = " ".join([doc["chunk"] for doc in retrieved])
    prompt = f"Answer the question based on the context below.\n\nContext:\n{context_text}\n\nQuestion: {question}\nAnswer:"

     # Generate answer with GPT
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content, retrieved_context, True