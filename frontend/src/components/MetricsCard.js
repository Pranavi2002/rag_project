// handles both DeepEval and RAGAS results in tabular format

import React from "react";

function MetricsCard({ metrics, reasoning }) {
  if ((!metrics || Object.keys(metrics).length === 0) && !reasoning) return null;

  return (
    <div className="bg-gray-100 p-4 rounded mt-4">
      {metrics && (
        <>
          <h3 className="font-semibold mb-3 text-lg">Evaluation Metrics</h3>

          {/* Loop through each metric type */}
          {Object.entries(metrics).map(([name, data]) => {
            // If metric is still computing
            if (typeof data === "string") {
              return (
                <div key={name} className="mb-3">
                  <strong>{name}:</strong> {data}
                </div>
              );
            }

            // DeepEval metrics (object with value, reason, pass)
            if (
              Object.values(data).some(
                (v) => v && typeof v === "object" && "value" in v
              )
            ) {
              return (
                <div key={name} className="mb-4">
                  <strong className="block mb-2">{name}</strong>
                  <table className="min-w-full bg-white border border-gray-300">
                    <thead className="bg-gray-200">
                      <tr>
                        <th className="py-1 px-2 border">Metric</th>
                        <th className="py-1 px-2 border">Score</th>
                        <th className="py-1 px-2 border">Status</th>
                        <th className="py-1 px-2 border">Reason</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(data).map(([metricName, metricData]) => {
                        const val =
                          metricData.value !== undefined
                            ? (metricData.value * 100).toFixed(1) + "%"
                            : "Computing...";
                        const reason = metricData.reason || "Computing...";
                        const passed =
                          metricData.pass !== undefined
                            ? metricData.pass
                              ? "✅ Pass"
                              : "❌ Fail"
                            : "Computing...";
                        return (
                          <tr key={metricName} className="text-sm">
                            <td className="py-1 px-2 border">{metricName.replace(/Metric$/, "")}</td>
                            <td className="py-1 px-2 border">{val}</td>
                            <td className="py-1 px-2 border">{passed}</td>
                            <td className="py-1 px-2 border">{reason}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              );
            }

            // RAGAS metrics (numeric)
            return (
              <div key={name} className="mb-4">
                <strong className="block mb-2">{name}</strong>
                <table className="min-w-full bg-white border border-gray-300">
                  <thead className="bg-gray-200">
                    <tr>
                      <th className="py-1 px-2 border">Metric</th>
                      <th className="py-1 px-2 border">Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(data).map(([metricName, val]) => (
                      <tr key={metricName} className="text-sm">
                        <td className="py-1 px-2 border">{metricName}</td>
                        <td className="py-1 px-2 border">
                          {typeof val === "number" ? (val * 100).toFixed(1) + "%" : val}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          })}
        </>
      )}

      {reasoning && (
        <div className="mt-4 p-2 border-l-4 border-green-400 bg-green-50 text-sm rounded">
          <h3 className="font-semibold mb-1">RAGAS Reasoning:</h3>
          <div className="whitespace-pre-wrap break-words">{reasoning}</div>
        </div>
      )}
    </div>
  );
}

export default MetricsCard;