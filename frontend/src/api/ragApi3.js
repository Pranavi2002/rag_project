// async with raw input

import axios from "axios";

const BASE_URL = "http://localhost:8000";

// Upload documents
export const uploadDocs = async (texts) => {
  return axios.post(`${BASE_URL}/upload`, { texts });
};

// Ask question → only answer
export const askQuestion = async (question) => {
  return axios.post(`${BASE_URL}/query`, { question });
};

// Fetch metrics for a question asynchronously
export const getMetrics = async (question) => {
  return axios.post(`${BASE_URL}/metrics`, { question });
};