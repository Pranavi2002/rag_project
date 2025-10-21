import React, { useState } from "react";
import { askQuery, uploadFiles, removeFiles } from "./api/ragApi";
import ChatBox from "./components/ChatBox";
import MetricsCard from "./components/MetricsCard";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [context, setContext] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [reasoning, setReasoning] = useState(null);
  const [loadingAnswer, setLoadingAnswer] = useState(false);
  const [loadingMetrics, setLoadingMetrics] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // -------------------------
  // Polling function for metrics
  // -------------------------
  const fetchMetrics = async (q) => {
    setLoadingMetrics(true);
    let done = false;
    let currentMetrics = { DeepEval: "Computing...", RAGAS: "Computing..." };

    while (!done) {
      try {
        const res = await fetch("http://localhost:8000/metrics", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: q }),
        });
        const data = await res.json();
        const m = data.metrics || {};

        // Merge with current metrics to retain "Computing..." for pending
        currentMetrics = {
          DeepEval:
            m.DeepEval !== undefined ? m.DeepEval : currentMetrics.DeepEval,
          RAGAS: m.RAGAS !== undefined ? m.RAGAS : currentMetrics.RAGAS,
        };

        setMetrics(currentMetrics);
        setReasoning(data.reasoning);

        const deepevalDone = currentMetrics.DeepEval !== "Computing...";
        const ragasDone = currentMetrics.RAGAS !== "Computing...";
        done = deepevalDone && ragasDone;
      } catch (err) {
        console.error("Error fetching metrics:", err);
        done = true;
      }

      if (!done) {
        await new Promise((r) => setTimeout(r, 2000)); // poll every 2s
      }
    }

    setLoadingMetrics(false);
  };

  // -------------------------
  // Handle ask question
  // -------------------------
  const handleAsk = async (q) => {
    setQuestion(q);
    setAnswer("");
    setContext([]);
    setMetrics(null);
    setReasoning(null);
    setLoadingAnswer(true);
    setLoadingMetrics(true);

    try {
      const res = await askQuery(q);
      setAnswer(res.data.answer || "No relevant information found.");
      setContext(res.data.context || []);
      setReasoning(res.data.reasoning || null);
      setLoadingAnswer(false);

      // Start polling metrics
      fetchMetrics(q);
    } catch (err) {
      console.error("API error:", err);
      setAnswer("Error fetching answer.");
      setContext([]);
      setMetrics(null);
      setReasoning(null);
      setLoadingAnswer(false);
      setLoadingMetrics(false);
    }
  };

  // -------------------------
  // Handle file upload
  // -------------------------
  const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files.length) return;

    setUploading(true);
    setUploadMessage("");

    try {
      const res = await uploadFiles(files);
      setUploadMessage(`✅ Uploaded ${res.data.count} documents successfully!`);
      setUploadedFiles((prev) => [
        ...prev,
        ...Array.from(files).map((f) => f.name),
      ]);
    } catch (err) {
      console.error("Upload error:", err);
      setUploadMessage("❌ Error uploading files.");
    } finally {
      setUploading(false);
    }
  };

  // -------------------------
  // Handle remove file
  // -------------------------
  const handleRemoveFile = async (filename) => {
    setUploading(true);
    setUploadMessage("");

    try {
      const res = await removeFiles([filename]);
      setUploadMessage(res.data.status);
      setUploadedFiles((prev) => prev.filter((f) => f !== filename));
    } catch (err) {
      console.error("Remove error:", err);
      setUploadMessage("❌ Error removing file.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">
        AskMyDocs — RAG + DeepEval + RAGAS
      </h1>

      {/* File Upload Section */}
      <div className="mb-6 p-4 border rounded-lg shadow-sm bg-gray-50">
        <label className="block text-sm font-semibold mb-2">
          Upload PDF or Text Files:
        </label>
        <input
          type="file"
          multiple
          accept=".pdf,.txt"
          onChange={handleFileUpload}
          disabled={uploading}
          className="block w-full text-sm border border-gray-300 rounded p-2"
        />
        {uploading && (
          <p className="text-sm text-gray-600 mt-2">Uploading files...</p>
        )}
        {uploadMessage && <p className="text-sm mt-2">{uploadMessage}</p>}

        {uploadedFiles.length > 0 && (
          <div className="mt-3">
            <p className="text-sm font-semibold">Uploaded Files:</p>
            <ul className="list-disc list-inside text-sm">
              {uploadedFiles.map((name, idx) => (
                <li key={idx} className="flex justify-between items-center">
                  {name}
                  <button
                    onClick={() => handleRemoveFile(name)}
                    className="ml-2 text-red-500 text-sm hover:underline"
                    disabled={uploading}
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Ask Question Section */}
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
          <p>
            <strong>Question:</strong> {question}
          </p>
        </div>
      )}

      {answer && (
        <div className="mt-2">
          <p>
            <strong>Answer:</strong> {answer}
          </p>

          {context.length > 0 && (
            <div className="mt-2 p-2 border-l-4 border-blue-400 bg-blue-50 text-sm">
              <p className="font-semibold">Context:</p>
              <ul className="list-disc list-inside">
                {context.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </div>
          )}
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

      {(metrics || reasoning) && (
        <MetricsCard metrics={metrics} reasoning={reasoning} />
      )}
    </div>
  );
}

export default App;