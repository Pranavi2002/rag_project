# RAG Project with DeepEval & RAGAS Metrics

This project is a **Retrieval-Augmented Generation (RAG) system** that allows users to upload documents (PDF or text), retrieve relevant information, and generate answers using OpenAI GPT-3.5-turbo embeddings. It includes evaluation of generated answers using **DeepEval** and **RAGAS** metrics.  

The project is structured as a **FastAPI backend** with a **React frontend** for interaction.

---

## 🗂 Project Structure

```
rag_project/
│
├── backend/
│   ├── main.py              # FastAPI app with endpoints (/upload, /query)
│   ├── rag_engine.py        # RAG logic: chunking, embedding, FAISS search, generation
│   ├── ragas_engine.py      # RAGAS metrics
│   ├── deepeval_utils.py    # DeepEval metrics
│   ├── data/                # Optional: Folder for PDF or text files
│   │   └── sample_docs/
│   ├── vectorstore/         # Optional: store FAISS index files here
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables / API keys
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React app
│   │   ├── components/
│   │   │   ├── ChatBox.jsx
│   │   │   └── MetricsCard.jsx
│   │   └── api/
│   │       └── ragApi.js    # Axios calls to FastAPI backend
│   ├── package.json
│   └── README.md

````

---

## ⚡ Features

### Backend
- **Document upload & removal**: Upload PDF or TXT files.
- **Chunking & embedding**: Text is split into manageable chunks and embedded using `text-embedding-3-small`.
- **FAISS vector store**: Stores embeddings for fast similarity search.
- **Answer generation**: GPT-3.5-turbo generates concise or full answers based on retrieved context.
- **Evaluation metrics**:
  - **DeepEval**: Faithfulness, Answer Relevancy, Hallucination, Contextual Relevancy, Fluency.
  - **RAGAS**: Faithfulness, Answer Relevancy, Context Precision & Recall, Answer Correctness, Multi-Modal metrics.

### Frontend
- **React UI** with:
  - Chat interface for querying the RAG system.
  - Metrics display for DeepEval & RAGAS evaluations.
- **Real-time interaction** with backend via Axios API calls.

---

## 🚀 Installation

### Backend
1. Create a Python virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
````

2. Install dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key
   ```
4. Run FastAPI server:

   ```bash
   uvicorn backend.main:app --reload
   ```

### Frontend

1. Navigate to frontend folder:

   ```bash
   cd frontend
   ```
2. Install npm dependencies:

   ```bash
   npm install
   ```
3. Run React app:

   ```bash
   npm start
   ```

---

## 🧩 Usage

1. Open the frontend React app in your browser.
2. Upload documents (PDF or TXT) via the UI.
3. Ask questions in the chatbox. Answers are generated from retrieved context.
4. View **DeepEval** and **RAGAS** metrics for each answer in the metrics card.

---

## 📝 Notes

* **Context handling**: Answers are generated based only on the retrieved context.
* **Summarization**: If the question asks for a summary, a strict extractive summary is returned.
* **Caching**: Repeated queries are cached for faster response times.

---

## 📦 Dependencies

* Backend:

  * `fastapi`
  * `uvicorn`
  * `openai`
  * `faiss`
  * `PyPDF2`
  * `numpy`
  * `python-dotenv`
* Frontend:

  * `react`
  * `axios`
  * `react-scripts` (Create React App)

---

## 🔗 Links

* [OpenAI API](https://platform.openai.com/)
* [FAISS Documentation](https://faiss.ai/)
* [FastAPI](https://fastapi.tiangolo.com/)

---

## ✅ Status

* Backend: ✅ Fully functional with RAG, embeddings, and metrics.
* Frontend: ✅ Chat interface with metrics display.
* Metrics: ✅ DeepEval and RAGAS integrated.

---

## 👩‍💻 Author
### Pranavi Kolipaka
Feel free to connect: 
- [LinkedIn] (https://www.linkedin.com/in/vns-sai-pranavi-kolipaka-489601208/) 
- [GitHub] (https://github.com/Pranavi2002)