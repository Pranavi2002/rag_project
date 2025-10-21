import React, { useState } from "react";

function ChatBox({ onAsk, disabled }) {
  const [question, setQuestion] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim() === "") return;
    onAsk(question);
    setQuestion("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex mb-4">
      <input
        type="text"
        placeholder="Ask your question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        className="border p-2 flex-1 rounded"
        disabled={disabled}
      />
      <button
        type="submit"
        className={`px-4 ml-2 rounded text-white ${
          disabled ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500"
        }`}
        disabled={disabled}
      >
        Ask
      </button>
    </form>
  );
}

export default ChatBox;