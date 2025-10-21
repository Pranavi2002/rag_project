"""
- async with raw input
"""

from openai import OpenAI
import numpy as np
import faiss
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- In-memory storage ---
documents = []
embeddings = None
index = None

def add_documents(docs: list[str]):
    global documents, embeddings, index
    documents.extend(docs)

    doc_embeds = [
        client.embeddings.create(model="text-embedding-3-small", input=d).data[0].embedding
        for d in docs
    ]
    doc_embeds = np.array(doc_embeds).astype("float32")

    if embeddings is None:
        embeddings = doc_embeds
        index = faiss.IndexFlatL2(len(doc_embeds[0]))
        index.add(embeddings)
    else:
        index.add(doc_embeds)

def query_rag(question: str, k: int = 2):
    """
    Returns:
      - answer (str)
      - retrieved context (list[str])
      - relevant (bool)
    """
    global index, documents
    if not documents:
        return "", [], False

    q_embed = client.embeddings.create(model="text-embedding-3-small", input=question).data[0].embedding
    q_embed = np.array([q_embed]).astype("float32")

    D, I = index.search(q_embed, k)
    retrieved = [documents[i] for i in I[0]]

    # Consider relevant if at least one doc retrieved
    relevant = len(retrieved) > 0 and any(d.strip() for d in retrieved)

    if not relevant:
        return "", retrieved, False

    context = " ".join(retrieved)
    prompt = f"Answer the question based on the context below.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content, retrieved, True