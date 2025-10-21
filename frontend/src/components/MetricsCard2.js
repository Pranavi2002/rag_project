// handles both DeepEval and RAGAS results

import React from "react";

function MetricsCard({ metrics, reasoning }) {
  if ((!metrics || Object.keys(metrics).length === 0) && !reasoning) return null;

  return (
    <div className="bg-gray-100 p-4 rounded mt-4">
      {metrics && (
        <>
          <h3 className="font-semibold mb-2">Evaluation Metrics</h3>
          {Object.entries(metrics).map(([name, data]) => {
            // If metric is still computing
            if (typeof data === "string") {
              return (
                <div key={name} className="mb-2">
                  <strong>{name}:</strong> {data}
                </div>
              );
            }

            // If DeepEval (objects with value/reason/pass)
            if (
              Object.values(data).some(
                (v) => v && typeof v === "object" && "value" in v
              )
            ) {
              return (
                <div key={name} className="mb-2">
                  <strong>{name}:</strong>
                  <ul className="ml-4 list-disc">
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
                        <li key={metricName}>
                          <strong>{metricName.replace(/Metric$/, "")}:</strong>{" "}
                          {val} ({passed}) - <em>{reason}</em>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              );
            }

            // If RAGAS (numeric values)
            return (
              <div key={name} className="mb-2">
                <strong>{name}:</strong>
                <ul className="ml-4 list-disc">
                  {Object.entries(data).map(([metricName, val]) => (
                    <li key={metricName}>
                      <strong>{metricName}:</strong>{" "}
                      {typeof val === "number" ? (val * 100).toFixed(1) + "%" : val}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </>
      )}

      {reasoning && (
        <div className="mt-4 p-2 border-l-4 border-green-400 bg-green-50 text-sm">
          <h3 className="font-semibold mb-1">RAGAS Reasoning:</h3>
          <div className="whitespace-pre-wrap break-words">{reasoning}</div>
        </div>
      )}
    </div>
  );
}

export default MetricsCard;