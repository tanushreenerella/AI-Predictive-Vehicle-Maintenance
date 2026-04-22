"use client";

import { useState } from "react";
import { analyzeapi } from "@/lib/analyzeapi";
import HealthGauge from "@/components/dashboard/HealthGauge";

type SensorData = {
  engine_rpm: string;
  lub_oil_pressure: string;
  fuel_pressure: string;
  coolant_pressure: string;
  lub_oil_temp: string;
  coolant_temp: string;
};

export default function PredictiveAnalysisPage() {
  const [sensorData, setSensorData] = useState<SensorData>({
    engine_rpm: "",
    lub_oil_pressure: "",
    fuel_pressure: "",
    coolant_pressure: "",
    lub_oil_temp: "",
    coolant_temp: "",
  });

  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fields: { key: keyof SensorData; label: string }[] = [
    { key: "engine_rpm", label: "Engine RPM" },
    { key: "lub_oil_pressure", label: "Lub Oil Pressure (bar)" },
    { key: "fuel_pressure", label: "Fuel Pressure (bar)" },
    { key: "coolant_pressure", label: "Coolant Pressure (bar)" },
    { key: "lub_oil_temp", label: "Lub Oil Temperature (°C)" },
    { key: "coolant_temp", label: "Coolant Temperature (°C)" },
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setSensorData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleAnalyze = async () => {
    const hasEmpty = Object.values(sensorData).some(
      (v) => v === "" || isNaN(Number(v))
    );

    if (hasEmpty) {
      alert("Fill all fields");
      return;
    }

    const payload = {
      engine_rpm: Number(sensorData.engine_rpm),
      lub_oil_pressure: Number(sensorData.lub_oil_pressure),
      fuel_pressure: Number(sensorData.fuel_pressure),
      coolant_pressure: Number(sensorData.coolant_pressure),
      lub_oil_temp: Number(sensorData.lub_oil_temp),
      coolant_temp: Number(sensorData.coolant_temp),
    };

    console.log("Payload sent to backend:", payload);

    try {
      setLoading(true);
      const result = await analyzeapi(payload);
      setAnalysis({
  failure_probability: Number(result.failureProbability) || 0,
  health_score:
    result.riskLevel === "HIGH"
      ? 30
      : result.riskLevel === "MEDIUM"
      ? 60
      : 90,
  risk_score:
    result.riskLevel === "HIGH"
      ? 80
      : result.riskLevel === "MEDIUM"
      ? 50
      : 20,
});

    } catch (e) {
      console.error(e);
      alert("Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Predictive Vehicle Analysis</h1>

      <div className="grid grid-cols-2 gap-4">
        {fields.map(({ key, label }) => (
          <input
            key={key}
            name={key}
            type="number"
            step="any"
            placeholder={label}
            value={sensorData[key]}
            onChange={handleChange}
            className="border p-2 rounded"
          />
        ))}
      </div>

      <button
        onClick={handleAnalyze}
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        {loading ? "Analyzing..." : "Run Analysis"}
      </button>

      {analysis && (
        <div className="grid grid-cols-3 gap-6 mt-6">
          <HealthGauge
            title="Failure Probability"
            value={(analysis.failure_probability ?? 0) * 100}
            type="probability"
          />
          <HealthGauge
            title="System Health"
            value={analysis.health_score ?? 0}
            type="health"
          />
          <HealthGauge
            title="Risk Score"
            value={analysis.risk_score ?? 0}
            type="risk"
          />
        </div>
      )}
    </div>
  );
}
