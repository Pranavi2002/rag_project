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

* `ragApi.js` handles requests to the backend endpoints:

  * `/upload` – Upload documents for RAG retrieval.
  * `/query` – Send a question and retrieve an answer with metrics.

## Notes

* The frontend is designed to work with **React 18+**.
* Metrics visualization is powered by the `MetricsCard.jsx` component.
* The app assumes that the backend is hosted locally or at the URL defined in `ragApi.js`.