"""
- async with raw, text, pdf upload and removal
- answer generated from all relevant docs
- answer is small if asked
- retrieved context is short per doc for frontend display
- reasoning is summarized always
- Strict Grounding Prompt: good ragas faithfulness score but less ragas contextual recall and less deepeval context relevancy scores
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
def query_rag(question: str, k: int = 3, mode: str = "auto"):
    """
    Retrieve relevant chunks from FAISS, generate full or summarized answers using GPT-3.5-turbo,
    and handle extractive summary requests for accurate metrics.

    Modes:
    - "auto": Normal behavior. Generates a summary only if the question asks for it.
    - "always": Evaluation mode. Generates both a full answer and an extractive summary for metrics.

    Returns:
    - answer_to_show: Full or summarized answer, for display.
    - retrieved_context: List of concise context snippets for frontend display.
    - success: True if relevant context found, False otherwise.
    - answer_summary (only in 'always' mode): Separate summary for metric evaluation (extractive).
    """
    global index, documents
    if not documents:
        # There are no indexed documents, so cannot answer.
        return "", [], False

    # Step 1: Embed the user's question and search FAISS for most relevant chunks.
    q_embed = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding
    q_embed = np.array([q_embed]).astype("float32")
    D, I = index.search(q_embed, k)
    retrieved = [documents[i] for i in I[0]]

    # Step 2: Prepare concise context snippets for the frontend.
    def summarize_chunk(chunk, max_sentences=2):
        sentences = chunk.split(". ")
        # Take first max_sentences and add "..." if truncated.
        return ". ".join(sentences[:max_sentences]) + (
            "" if len(sentences) <= max_sentences else "..."
        )

    seen_files = set()
    retrieved_context = []
    for doc in retrieved:
        if doc["filename"] not in seen_files:
            short_chunk = summarize_chunk(doc["chunk"])
            retrieved_context.append(f"[{doc['filename']}] {short_chunk}")
            seen_files.add(doc["filename"])

    if not retrieved_context:
        return "", retrieved_context, False

    # Step 3: Combine full retrieved context for answering.
    context_text = " ".join([doc["chunk"] for doc in retrieved])

    # Step 4: Detect requests for summarization.
    summary_triggers = ["summarize", "in short", "concise", "briefly", "summary"]
    is_summary_request = any(word in question.lower() for word in summary_triggers)

    # Step 5: Construct prompts for full and summary answers with grounding instructions.
    normal_prompt = f"""
    You are an AI assistant that must answer questions using only the retrieved context below.
    Do not include any examples, facts, or information that are not explicitly mentioned in the context.
    If the context does not contain enough information to answer, say "The context does not provide that information."

    Context:
    {context_text}

    Question:
    {question}

    Answer (in 4-5 sentences):
    """

    summary_prompt = f"""
    Write a short summary (1-2 sentences) that only uses exact phrases or sentences from the provided context.
    Do not paraphrase or add any new information that is not present in the context.

    Context:
    {context_text}

    Question:
    {question}

    Strict Extractive Summary:
    """

    # Step 6: Handle answer generation based on mode and summary request.
    if mode == "always":
        # For evaluation: get both full answer and extractive summary.
        full_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": normal_prompt}]
        ).choices[0].message.content

        summary_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": summary_prompt}]
        ).choices[0].message.content

        return full_response, retrieved_context, True, summary_response

    elif is_summary_request:
        # For summary requests: return only the extractive summary.
        summary_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": summary_prompt}]
        ).choices[0].message.content

        return summary_response, retrieved_context, True

    else:
        # For normal requests: return the full answer.
        full_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": normal_prompt}]
        ).choices[0].message.content

        return full_response, retrieved_context, True