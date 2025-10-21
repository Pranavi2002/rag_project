// hanldes only deepeval results

import React from "react";

/**
 * Displays evaluation metrics returned by DeepEval
 * @param {Object} metrics - dynamic metrics dictionary from backend
 */
function MetricsCard({ metrics }) {
  // If no metrics or empty, render nothing
  if (!metrics || Object.keys(metrics).length === 0) return null;

  return (
    <div className="bg-gray-100 p-4 rounded mt-4">
      <h3 className="font-semibold mb-2">Evaluation Metrics</h3>

      {Object.entries(metrics).map(([name, data]) => {
        // Convert metric value to percentage string, fallback to N/A
        const value =
          data?.value !== null && data?.value !== undefined
            ? (data.value * 100).toFixed(1) + "%"
            : "N/A";

        const reason = data?.reason || "N/A";
        const passed = data?.pass !== undefined
          ? (data.pass ? "✅ Pass" : "❌ Fail")
          : "N/A";

        return (
          <div key={name} className="mb-2">
            <p>
              <strong>{name.replace("Metric", "")}:</strong> {value} ({passed})
            </p>
            <p className="text-sm text-gray-600">
              <strong>Reason:</strong> {reason}
            </p>
          </div>
        );
      })}
    </div>
  );
}

export default MetricsCard;