"""
RAG Engine: Core Retrieval-Augmented Generation logic
- Add documents
- Embed text
- Store in FAISS vector index
- Query with a question
- Generate answer using OpenAI LLM

- synchronous and async hallucinated
"""

from openai import OpenAI
import numpy as np
import faiss
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- In-memory storage for simplicity ---
documents = []       # list of documents (strings)
embeddings = None    # numpy array of embeddings
index = None         # FAISS index

def add_documents(docs: list[str]):
    """
    Adds documents to in-memory store and updates FAISS index
    """
    global documents, embeddings, index

    documents.extend(docs)

    # Generate embeddings for each document
    doc_embeds = [
        client.embeddings.create(
            model="text-embedding-3-small",
            input=d
        ).data[0].embedding
        for d in docs
    ]

    doc_embeds = np.array(doc_embeds).astype("float32")

    if embeddings is None:
        embeddings = doc_embeds
        # Initialize FAISS index
        index = faiss.IndexFlatL2(len(doc_embeds[0]))
        index.add(embeddings)
    else:
        index.add(doc_embeds)

def query_rag(question: str, k: int = 2):
    """
    Given a question:
    - Generate embedding
    - Retrieve top-k documents from FAISS
    - Build prompt with retrieved context
    - Generate answer using GPT model
    """
    global index, documents

    # Create embedding for the question
    q_embed = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding
    q_embed = np.array([q_embed]).astype("float32")

    # Search FAISS index for top-k similar docs
    _, I = index.search(q_embed, k)
    retrieved = [documents[i] for i in I[0]]

    # Combine retrieved docs as context
    context = " ".join(retrieved)

    # Build prompt for GPT
    prompt = f"Answer the question based on the context below.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"

    # Generate answer
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content, retrieved