// synchronous code

import React, { useState } from "react";
import { askQuestion } from "./api/ragApi";
import ChatBox from "./components/ChatBox";
import MetricsCard from "./components/MetricsCard";

function App() {
  const [question, setQuestion] = useState(""); // last asked question
  const [answer, setAnswer] = useState("");
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAsk = async (q) => {
    setQuestion(q);
    setAnswer("");
    setMetrics(null);
    setLoading(true);

    try {
      const res = await askQuestion(q);
      setAnswer(res.data.answer);
      setMetrics(res.data.metrics);
    } catch (err) {
      console.error("API call failed:", err);
      setAnswer("Error fetching answer.");
      setMetrics(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">AskMyDocs — RAG + DeepEval</h1>

      <ChatBox onAsk={handleAsk} disabled={loading} />

      {loading && (
        <div className="flex justify-center my-4">
          <img
            src="https://i.gifer.com/ZZ5H.gif"
            alt="Loading..."
            className="w-12 h-12"
          />
        </div>
      )}

      {!loading && question && (
        <div className="mt-4">
          <p><strong>Question:</strong> {question}</p>
        </div>
      )}

      {!loading && answer && (
        <div className="mt-2">
          <p><strong>Answer:</strong> {answer}</p>
        </div>
      )}

      {!loading && metrics && <MetricsCard metrics={metrics} />}
    </div>
  );
}

export default App;