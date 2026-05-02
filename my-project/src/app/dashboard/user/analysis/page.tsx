"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { analyzeapi } from "@/lib/analyzeapi";
import { fetchWithAuth } from "@/lib/fetchWithAuth";
import { AlertTriangle, CheckCircle, Activity, ChevronRight } from "lucide-react";

const API_BASE = "https://ai-predictive-vehicle-maintenance-production.up.railway.app";

type SensorData = {
  engine_rpm: string;
  lub_oil_pressure: string;
  fuel_pressure: string;
  coolant_pressure: string;
  lub_oil_temp: string;
  coolant_temp: string;
};

const fields: { key: keyof SensorData; label: string; placeholder: string }[] = [
  { key: "engine_rpm",        label: "Engine RPM",              placeholder: "e.g. 3000" },
  { key: "lub_oil_pressure",  label: "Lub Oil Pressure (bar)",  placeholder: "e.g. 2.0" },
  { key: "fuel_pressure",     label: "Fuel Pressure (bar)",     placeholder: "e.g. 2.5" },
  { key: "coolant_pressure",  label: "Coolant Pressure (bar)",  placeholder: "e.g. 1.2" },
  { key: "lub_oil_temp",      label: "Lub Oil Temp (°C)",       placeholder: "e.g. 90" },
  { key: "coolant_temp",      label: "Coolant Temp (°C)",       placeholder: "e.g. 85" },
];

export default function PredictiveAnalysisPage() {
  const searchParams = useSearchParams();
  const [sensorData, setSensorData] = useState<SensorData>({
    engine_rpm: "", lub_oil_pressure: "", fuel_pressure: "",
    coolant_pressure: "", lub_oil_temp: "", coolant_temp: "",
  });
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState<string>("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWithAuth(`${API_BASE}/vehicles/health/me`)
      .then(r => r.ok ? r.json() : [])
      .then((data: any[]) => {
        setVehicles(data);
        // Pre-select vehicle from URL param
        const paramId = searchParams.get("vehicle_id");
        if (paramId) {
          setSelectedVehicleId(paramId);
        } else if (data.length > 0) {
          setSelectedVehicleId(String(data[0].id));
        }
      })
      .catch(() => {});
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSensorData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleAnalyze = async () => {
    const hasInvalid = Object.values(sensorData).some(v => v === "" || isNaN(Number(v)));
    if (hasInvalid) { setError("Please fill in all sensor fields with valid numbers."); return; }

    setError(null);
    setLoading(true);
    try {
      const payload = Object.fromEntries(
        Object.entries(sensorData).map(([k, v]) => [k, Number(v)])
      );
      const res = await analyzeapi(payload, selectedVehicleId || undefined);
      setResult(res);
    } catch (e: any) {
      setError(e.message || "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const riskColor = (level: string) => {
    if (level === "HIGH") return "text-red-400";
    if (level === "MEDIUM") return "text-yellow-400";
    return "text-green-400";
  };

  const riskBg = (level: string) => {
    if (level === "HIGH") return "bg-red-600/20 border-red-600/40";
    if (level === "MEDIUM") return "bg-yellow-600/20 border-yellow-600/40";
    return "bg-green-600/20 border-green-600/40";
  };

  const probPercent = result ? Math.round(result.failureProbability * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">AI Predictive Analysis</h1>
        <p className="text-gray-400">Enter sensor readings to predict engine failure probability</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <div className="bg-gray-800/40 rounded-2xl p-6 border border-gray-700/50 space-y-5">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-400" />
            Sensor Readings
          </h2>

          {/* Vehicle selector */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Link to vehicle <span className="text-gray-500">(optional — saves result to that vehicle)</span>
            </label>
            <select
              value={selectedVehicleId}
              onChange={e => setSelectedVehicleId(e.target.value)}
              className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">— No vehicle selected —</option>
              {vehicles.map(v => (
                <option key={v.id} value={v.id}>{v.name} ({v.model})</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {fields.map(({ key, label, placeholder }) => (
              <div key={key}>
                <label className="block text-xs text-gray-400 mb-1">{label}</label>
                <input
                  name={key}
                  type="number"
                  step="any"
                  placeholder={placeholder}
                  value={sensorData[key]}
                  onChange={handleChange}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
          </div>

          {error && (
            <div className="flex items-center gap-2 text-red-400 text-sm bg-red-600/10 border border-red-600/30 rounded-lg px-3 py-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full bg-linear-to-r from-blue-600 to-cyan-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Analyzing…" : "Run AI Analysis"}
          </button>
        </div>

        {/* Result Panel */}
        <div className="bg-gray-800/40 rounded-2xl p-6 border border-gray-700/50 space-y-5">
          <h2 className="text-lg font-semibold text-white">Prediction Result</h2>

          {!result && !loading && (
            <div className="flex flex-col items-center justify-center h-48 text-gray-500 space-y-2">
              <Activity className="w-10 h-10 opacity-30" />
              <p>Fill in sensor readings and click Run Analysis</p>
            </div>
          )}

          {loading && (
            <div className="flex flex-col items-center justify-center h-48 text-gray-400 space-y-2">
              <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <p>Running ML analysis…</p>
            </div>
          )}

          {result && !loading && (
            <div className="space-y-4">
              {/* Risk level banner */}
              <div className={`rounded-xl p-4 border ${riskBg(result.riskLevel)}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Risk Level</p>
                    <p className={`text-2xl font-bold ${riskColor(result.riskLevel)}`}>
                      {result.riskLevel}
                    </p>
                  </div>
                  {result.riskLevel === "HIGH"
                    ? <AlertTriangle className="w-8 h-8 text-red-400" />
                    : result.riskLevel === "MEDIUM"
                    ? <AlertTriangle className="w-8 h-8 text-yellow-400" />
                    : <CheckCircle className="w-8 h-8 text-green-400" />
                  }
                </div>
              </div>

              {/* Failure probability bar */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Failure Probability</span>
                  <span className={`font-semibold ${riskColor(result.riskLevel)}`}>{probPercent}%</span>
                </div>
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      result.riskLevel === "HIGH" ? "bg-red-500" :
                      result.riskLevel === "MEDIUM" ? "bg-yellow-500" : "bg-green-500"
                    }`}
                    style={{ width: `${probPercent}%` }}
                  />
                </div>
              </div>

              {/* Details grid */}
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-gray-900/50 rounded-lg p-3">
                  <p className="text-gray-500 text-xs">Component</p>
                  <p className="text-white font-medium">{result.component}</p>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-3">
                  <p className="text-gray-500 text-xs">Failure Window</p>
                  <p className="text-white font-medium">{result.estimatedFailureWindow}</p>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-3">
                  <p className="text-gray-500 text-xs">Confidence</p>
                  <p className="text-white font-medium">{Math.round(result.confidence * 100)}%</p>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-3">
                  <p className="text-gray-500 text-xs">Model</p>
                  <p className="text-white font-medium capitalize">{result.model_status}</p>
                </div>
              </div>

              {/* Message */}
              <p className="text-gray-400 text-sm">{result.message}</p>

              {/* High risk action */}
              {result.riskLevel === "HIGH" && (
                <div className="bg-red-600/10 border border-red-600/30 rounded-xl p-4 space-y-2">
                  <p className="text-red-300 font-semibold text-sm flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" />
                    Immediate action recommended
                  </p>
                  <p className="text-red-300/80 text-xs">
                    Engine failure predicted within 1-3 days. Schedule an inspection immediately.
                    {selectedVehicleId && " This result has been saved to your vehicle and will appear as an alert on your dashboard."}
                  </p>
                  <a
                    href="/dashboard/user/schedule"
                    className="flex items-center gap-1 text-xs text-red-300 underline hover:text-red-200"
                  >
                    Schedule service now <ChevronRight className="w-3 h-3" />
                  </a>
                </div>
              )}

              {result.riskLevel === "MEDIUM" && selectedVehicleId && (
                <p className="text-yellow-400/70 text-xs">
                  This result has been saved to your vehicle and will appear as an alert on your dashboard.
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
