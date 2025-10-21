// hallucinated answers for out-of-context queries

import axios from "axios";

const BASE_URL = "http://localhost:8000";

// -----------------------------
// Upload documents to backend
// -----------------------------
export const uploadDocs = async (texts) => {
  return axios.post(`${BASE_URL}/upload`, { texts });
};

// -----------------------------
// Ask a question to RAG (answer only)
// -----------------------------
export const askQuestion = async (question) => {
  return axios.post(`${BASE_URL}/query`, { question });
};

// -----------------------------
// Fetch DeepEval metrics separately
// -----------------------------
export const getMetrics = async (question) => {
  return axios.post(`${BASE_URL}/metrics`, { question });
};