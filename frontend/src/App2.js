// hallucinated answers for out-of-context queries

import React, { useState } from "react";
import { askQuestion, getMetrics } from "./api/ragApi";
import ChatBox from "./components/ChatBox";
import MetricsCard from "./components/MetricsCard";

/**
 * Main App component for AskMyDocs
 * Features:
 *  - Answer shows immediately after querying RAG
 *  - Metrics load asynchronously after answer is received
 *  - Separate loading indicators for answer and metrics
 */
function App() {
  const [question, setQuestion] = useState("");       // Last asked question
  const [answer, setAnswer] = useState("");           // RAG answer
  const [metrics, setMetrics] = useState(null);       // DeepEval metrics
  const [loadingAnswer, setLoadingAnswer] = useState(false);
  const [loadingMetrics, setLoadingMetrics] = useState(false);

  const handleAsk = async (q) => {
    setQuestion(q);
    setAnswer("");
    setMetrics(null);
    setLoadingAnswer(true);
    setLoadingMetrics(false);

    try {
      // -----------------------------
      // 1️⃣ Call backend for answer only
      // -----------------------------
      const res = await askQuestion(q);
      setAnswer(res.data.answer);
      setLoadingAnswer(false);

      // -----------------------------
      // 2️⃣ Fetch metrics asynchronously
      // -----------------------------
      setLoadingMetrics(true);
      const metricsRes = await getMetrics(q);
      setMetrics(metricsRes.data.metrics);
      setLoadingMetrics(false);
    } catch (err) {
      console.error("API call failed:", err);
      setAnswer("Error fetching answer.");
      setMetrics(null);
      setLoadingAnswer(false);
      setLoadingMetrics(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">AskMyDocs — RAG + DeepEval</h1>

      {/* ChatBox input */}
      <ChatBox onAsk={handleAsk} disabled={loadingAnswer || loadingMetrics} />

      {/* Answer loading spinner */}
      {loadingAnswer && (
        <div className="flex justify-center my-4">
          <img
            src="https://i.gifer.com/ZZ5H.gif"
            alt="Loading answer..."
            className="w-12 h-12"
          />
        </div>
      )}

      {/* Show last question */}
      {question && (
        <div className="mt-4">
          <p><strong>Question:</strong> {question}</p>
        </div>
      )}

      {/* Show answer */}
      {answer && (
        <div className="mt-2">
          <p><strong>Answer:</strong> {answer}</p>
        </div>
      )}

      {/* Metrics loading spinner */}
      {loadingMetrics && (
        <div className="flex justify-center my-2">
          <img
            src="https://i.gifer.com/ZZ5H.gif"
            alt="Loading metrics..."
            className="w-8 h-8"
          />
        </div>
      )}

      {/* Show metrics */}
      {metrics && <MetricsCard metrics={metrics} />}
    </div>
  );
}

export default App;