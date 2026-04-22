"use client";
import { useState } from "react";
import { analyzeapi } from "@/lib/analyzeapi";


export default function AnalyzePage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const [sensorData, setSensorData] = useState({
    engine_rpm: 3000,
    lub_oil_pressure: 2.0,
    fuel_pressure: 2.5,
    coolant_pressure: 1.2,
    lub_oil_temp: 90,
    coolant_temp: 85
  });

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const data = await analyzeapi(sensorData);
      setResult(data);
    } catch (err) {
      alert("Analysis failed");
    }
    setLoading(false);
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">AI Vehicle Health Analysis</h1>

      {/* SENSOR INPUT */}
      <div className="grid grid-cols-2 gap-4 bg-white p-4 rounded-xl shadow">
        {Object.keys(sensorData).map(key => (
          <input
            key={key}
            type="number"
            value={(sensorData as any)[key]}
            onChange={e =>
              setSensorData({ ...sensorData, [key]: Number(e.target.value) })
            }
            className="border px-3 py-2 rounded"
            placeholder={key}
          />
        ))}
      </div>

      <button
        onClick={handleAnalyze}
        className="bg-blue-600 text-white px-6 py-2 rounded-lg"
      >
        {loading ? "Analyzing..." : "Run AI Analysis"}
      </button>

      {/* RESULTS */}
      {result && (
        <div className="bg-gray-50 p-6 rounded-xl space-y-4">
          <h2 className="text-xl font-semibold">Analysis Result</h2>

          <pre className="text-sm whitespace-pre-wrap">
            {result.analysis}
          </pre>
        </div>
      )}
    </div>
  );
}
