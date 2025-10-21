# RAG Project Backend

This repository contains the **backend for a Retrieval-Augmented Generation (RAG) application** that supports:

- Answer generation based on uploaded documents
- Evaluation of answers using **DeepEval** and **RAGAS** metrics
- Retrieval of context using **FAISS vector store**
- FastAPI endpoints for uploading, querying, and retrieving metrics

---

## Features

- **Document Upload:** Upload PDFs or text files for context retrieval
- **RAG Engine:** Embeds documents, performs FAISS search, and generates answers
- **Evaluation Metrics:**
  - **DeepEval:** Faithfulness, Answer Relevancy, Contextual Relevancy, Hallucination, Fluency
  - **RAGAS:** Faithfulness, Answer Relevancy, Context Precision & Recall, Answer Correctness & Similarity, Multi-Modal metrics
- **FastAPI Endpoints:**
  - `/upload` – Upload documents
  - `/query` – Ask questions
  - `/metrics` – Retrieve evaluation metrics
  - `/health` – Check server health

---

## Project Structure

```
backend/
│
├── main.py             # FastAPI app with endpoints
├── rag_engine.py       # RAG logic: chunking, embedding, FAISS search, generation
├── ragas_engine.py     # RAGAS metrics integration
├── deepeval_utils.py   # DeepEval metrics integration
├── data/               # Optional: Folder for PDF or text files
│   └── sample_docs/
├── vectorstore/        # Optional: store FAISS index files here
├── requirements.txt
├── .env                # Contains secret keys
└── README.md           # This file
```

---

## Quick Start

Follow these steps to run the backend locally:

1. **Open terminal and navigate to the backend folder:**
```bash
cd path/to/rag_project/backend
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Create and configure your `.env` file:**

```
OPENAI_API_KEY=your_actual_api_key_here
```

4. **Run the FastAPI server:**

```bash
uvicorn main:app --reload
```

* You should see output like:

```
Uvicorn running on http://127.0.0.1:8000
```

5. **Test the health endpoint** in your browser or Postman:

```
http://127.0.0.1:8000/health
```

* Expected response:

```json
{"status":"ok"}
```

✅ This means your backend is running successfully!

---

## Usage

* **Upload documents** via `/upload` endpoint
* **Ask questions** via `/query` endpoint
* **Retrieve evaluation metrics** via `/metrics` endpoint

The backend generates:

1. Full answers using RAG (retrieved context + LLM)
2. Extractive summaries for evaluation purposes
3. DeepEval and RAGAS scores for monitoring answer quality

---

## Evaluation Metrics

**DeepEval Metrics:**

| Metric               | Description                                             |
| -------------------- | ------------------------------------------------------- |
| Faithfulness         | Checks if answer contradicts the retrieved context      |
| Answer Relevancy     | Measures relevance of the answer to the question        |
| Contextual Relevancy | Measures how well the answer uses the retrieved context |
| Hallucination        | Detects unsupported statements or hallucinated content  |
| Fluency [GEval]      | Measures grammar, readability, and logical flow         |

**RAGAS Metrics:**

| Metric                   | Description                                   |
| ------------------------ | --------------------------------------------- |
| Faithfulness             | Alignment with provided context               |
| Answer Relevancy         | Degree to which answer addresses the question |
| Context Precision        | Precision of retrieved context used           |
| Context Recall           | Fraction of relevant context captured         |
| Answer Correctness       | Correctness of answer compared to context     |
| Answer Similarity        | Similarity to reference answer (if available) |
| Multi-Modal Faithfulness | Faithfulness for multi-modal inputs           |
| Multi-Modal Relevance    | Relevance for multi-modal inputs              |

---

## Notes

* Make sure you **upload documents before querying** to ensure proper context retrieval.
* The backend is designed to **support multiple evaluation runs** efficiently.
* Frontend can call these endpoints for a complete UI experience.
* The backend uses **GPT-3.5-turbo** for generation and optional summaries.
* Retrieval-augmented generation (RAG) ensures that answers are grounded in uploaded documents.
* Metrics provide both automated evaluation and insights for testing and debugging AI responses.

