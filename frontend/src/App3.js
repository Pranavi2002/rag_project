// async with raw input

import React, { useState } from "react";
import { askQuestion, getMetrics } from "./api/ragApi";
import ChatBox from "./components/ChatBox";
import MetricsCard from "./components/MetricsCard";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [metrics, setMetrics] = useState(null);
  const [loadingAnswer, setLoadingAnswer] = useState(false);
  const [loadingMetrics, setLoadingMetrics] = useState(false);

  const handleAsk = async (q) => {
    setQuestion(q);
    setAnswer("");
    setMetrics(null);
    setLoadingAnswer(true);
    setLoadingMetrics(false);

    try {
      // Get answer only
      const res = await askQuestion(q);
      setAnswer(res.data.answer || "No relevant information found.");
      setLoadingAnswer(false);

      // Fetch metrics asynchronously
      setLoadingMetrics(true);
      const metricsRes = await getMetrics(q);
      setMetrics(metricsRes.data.metrics);
      setLoadingMetrics(false);
    } catch (err) {
      console.error("API error:", err);
      setAnswer("Error fetching answer.");
      setMetrics(null);
      setLoadingAnswer(false);
      setLoadingMetrics(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">AskMyDocs — RAG + DeepEval</h1>

      <ChatBox onAsk={handleAsk} disabled={loadingAnswer || loadingMetrics} />

      {loadingAnswer && (
        <div className="flex justify-center my-4">
          <img
            src="https://i.gifer.com/ZZ5H.gif"
            alt="Loading answer..."
            className="w-12 h-12"
          />
        </div>
      )}

      {question && (
        <div className="mt-4">
          <p><strong>Question:</strong> {question}</p>
        </div>
      )}

      {answer && (
        <div className="mt-2">
          <p><strong>Answer:</strong> {answer}</p>
        </div>
      )}

      {loadingMetrics && (
        <div className="flex justify-center my-2">
          <img
            src="https://i.gifer.com/ZZ5H.gif"
            alt="Loading metrics..."
            className="w-8 h-8"
          />
        </div>
      )}

      {metrics && <MetricsCard metrics={metrics} />}
    </div>
  );
}

export default App;