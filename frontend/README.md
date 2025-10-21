# RAG Project - Frontend

This folder contains the **React frontend** for the RAG Project, which interacts with the FastAPI backend to provide an AI assistant interface with DeepEval and RAGAS metrics evaluation.

## Project Structure

```
frontend/
│
├── src/
│   ├── App.jsx              # Main React app
│   ├── components/
│   │   ├── ChatBox.jsx      # Chat interface for asking questions
│   │   └── MetricsCard.jsx  # Displays DeepEval and RAGAS metrics
│   └── api/
│       └── ragApi.js        # Axios calls to FastAPI backend
├── package.json             # React dependencies and scripts
└── README.md                # This file
```

## Features

- **Chat Interface:** Users can ask questions to the AI assistant and get answers retrieved from the backend.
- **Metrics Display:** Shows DeepEval and RAGAS metrics for each answer, including faithfulness, relevancy, hallucination, and context recall.
- **Context Display:** Shows the retrieved context used by the AI to answer each question.
 **RAGAS Reasoning Display:** Shows the summarized RAGAS reasoning used by the RAG model to generate answer.
- **Seamless Backend Integration:** Communicates with FastAPI backend via Axios.

## Setup Instructions

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Start the frontend**

```bash
npm start
```

This will start the React app at `http://localhost:3000`.

3. Make sure the **backend FastAPI server** is running so the frontend can fetch answers and metrics.

## API Integration

The `ragApi.js` module handles requests to the backend FastAPI endpoints:

- **Document Upload**
  - `uploadDocs(texts)` – Upload plain text documents for RAG retrieval.
  - `uploadFiles(files)` – Upload PDF or text files using multipart/form-data.

- **Question & Answer**
  - `askQuery(question)` – Send a question to the backend and receive a generated answer using RAG.

- **Metrics**
  - `getMetrics(question)` – Retrieve evaluation metrics (DeepEval and RAGAS) for a specific question.

- **File Management**
  - `removeFiles(filenames)` – Remove previously uploaded files from the backend.

**Example Usage:**

```javascript
import { uploadFiles, askQuery, getMetrics } from './api/ragApi';

const files = [file1, file2];
await uploadFiles(files);

const answer = await askQuery("What is AI?");
const metrics = await getMetrics("What is AI?");
console.log(answer, metrics);
```

## Notes

* The frontend is designed to work with **React 18+**.
* Metrics visualization is powered by the `MetricsCard.jsx` component.
* The app assumes that the backend is hosted locally or at the URL defined in `ragApi.js`.