// synchronous

import axios from "axios";

const BASE_URL = "http://localhost:8000";

// Upload documents to the RAG backend
export const uploadDocs = async (texts) => {
  return axios.post(`${BASE_URL}/upload`, { texts });
};

// Ask a question to the RAG backend (answer + metrics)
export const askQuestion = async (question) => {
  return axios.post(`${BASE_URL}/query`, { question });
};