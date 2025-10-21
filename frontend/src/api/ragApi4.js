// async with raw, text, pdf upload and removal
// no ragas

import axios from "axios";

const BASE_URL = "http://localhost:8000";

export const uploadDocs = async (texts) => {
  return axios.post(`${BASE_URL}/upload`, { texts });
};

export const uploadFiles = async (files) => {
  const formData = new FormData();
  for (let file of files) {
    formData.append("files", file);
  }
  return axios.post(`${BASE_URL}/upload_files`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const askQuestion = async (question) => {
  return axios.post(`${BASE_URL}/query`, { question });
};

export const getMetrics = async (question) => {
  return axios.post(`${BASE_URL}/metrics`, { question });
};

export const removeFiles = async (filenames) => {
  return axios.post(`${BASE_URL}/remove_files`, filenames);
};