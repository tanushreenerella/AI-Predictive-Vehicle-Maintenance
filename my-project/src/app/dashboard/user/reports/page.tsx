'use client';

import { useState, useEffect } from 'react';
import { fetchWithAuth } from '@/lib/fetchWithAuth';
import {
  FileText, AlertTriangle, CheckCircle, Clock, Wrench,
  ChevronRight, Activity, Car, RefreshCw
} from 'lucide-react';

const API_BASE = 'https://ai-predictive-vehicle-maintenance-production.up.railway.app';

type RCAReport = {
  vehicle: { id: string; name: string; model: string; year: number; registration: string; mileage: number };
  risk_level: string;
  failure_probability: number;
  component: string;
  last_analyzed: string | null;
  generated_at: string;
  root_cause: string;
  contributing_factors: string[];
  recommendations: string[];
  severity: string;
  action_timeline: string;
  summary: string;
  generated_by: string;
};

export default function ReportsPage() {
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [report, setReport] = useState<RCAReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchWithAuth(`${API_BASE}/reports/vehicles`)
      .then(r => r.ok ? r.json() : [])
      .then((data: any[]) => {
        setVehicles(data);
        if (data.length > 0) setSelectedId(String(data[0].id));
      })
      .catch(() => {});
  }, []);

  const generate = async () => {
    if (!selectedId) return;
    setLoading(true);
    setError('');
    setReport(null);
    try {
      const res = await fetchWithAuth(`${API_BASE}/reports/rca/${selectedId}`);
      if (!res.ok) throw new Error('Failed to generate report');
      setReport(await res.json());
    } catch {
      setError('Could not generate report. Please ensure AI Analysis has been run on this vehicle first.');
    } finally {
      setLoading(false);
    }
  };

  const severityStyle = (s: string) => {
    if (s === 'Critical') return { badge: 'bg-red-500/20 text-red-400 border-red-500/40', icon: 'text-red-400', bar: 'bg-red-500' };
    if (s === 'Moderate') return { badge: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40', icon: 'text-yellow-400', bar: 'bg-yellow-500' };
    return { badge: 'bg-green-500/20 text-green-400 border-green-500/40', icon: 'text-green-400', bar: 'bg-green-500' };
  };

  const riskPct = report ? Math.round(report.failure_probability * 100) : 0;
  const style = report ? severityStyle(report.severity) : null;

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <FileText className="w-8 h-8 text-blue-400" />
          Reports & RCA
        </h1>
        <p className="text-gray-400 mt-1">AI-generated Root Cause Analysis for your vehicles</p>
      </div>

      {/* Generator card */}
      <div className="bg-gray-800/50 rounded-2xl border border-gray-700 p-6 space-y-4">
        <h2 className="text-lg font-semibold text-white">Generate RCA Report</h2>

        {vehicles.length === 0 ? (
          <p className="text-gray-400 text-sm">No vehicles found. Add a vehicle and run AI Analysis first.</p>
        ) : (
          <>
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Select Vehicle</label>
                <select
                  value={selectedId}
                  onChange={e => setSelectedId(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-600 rounded-xl px-3 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {vehicles.map(v => (
                    <option key={v.id} value={String(v.id)}>
                      {v.name} ({v.model})
                      {v.ai_risk_level ? ` — ${v.ai_risk_level} risk` : ' — not analysed'}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={generate}
                  disabled={loading || !selectedId}
                  className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white py-2.5 px-5 rounded-xl font-semibold transition-colors"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Generating…
                    </>
                  ) : (
                    <>
                      <Activity className="w-4 h-4" />
                      Generate RCA Report
                    </>
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                {error}
              </div>
            )}
          </>
        )}
      </div>

      {/* Report output */}
      {report && style && (
        <div className="space-y-5">
          {/* Vehicle + severity header */}
          <div className="bg-gray-800/50 rounded-2xl border border-gray-700 p-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-blue-500/10 rounded-xl border border-blue-500/30">
                  <Car className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">{report.vehicle.name}</h3>
                  <p className="text-gray-400 text-sm">
                    {report.vehicle.model} · {report.vehicle.year} · {report.vehicle.registration} · {report.vehicle.mileage.toLocaleString()} km
                  </p>
                </div>
              </div>
              <span className={`px-4 py-1.5 rounded-full text-sm font-semibold border ${style.badge}`}>
                {report.severity} Severity
              </span>
            </div>

            {/* Failure probability bar */}
            <div className="mt-5">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Engine Failure Probability</span>
                <span className={`font-bold text-lg ${style.icon}`}>{riskPct}%</span>
              </div>
              <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${style.bar}`}
                  style={{ width: `${riskPct}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-5">
              <div className="bg-gray-900/60 rounded-xl p-3 text-center">
                <p className="text-xs text-gray-500">Risk Level</p>
                <p className={`font-bold mt-1 ${style.icon}`}>{report.risk_level}</p>
              </div>
              <div className="bg-gray-900/60 rounded-xl p-3 text-center">
                <p className="text-xs text-gray-500">Component</p>
                <p className="font-semibold text-white mt-1 text-sm">{report.component}</p>
              </div>
              <div className="bg-gray-900/60 rounded-xl p-3 text-center">
                <p className="text-xs text-gray-500">Action By</p>
                <p className="font-semibold text-white mt-1 text-sm">{report.action_timeline}</p>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-blue-900/20 border border-blue-500/30 rounded-2xl p-5">
            <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-400" />
              Executive Summary
            </h4>
            <p className="text-gray-300 text-sm leading-relaxed">{report.summary}</p>
          </div>

          {/* Root cause + contributing factors */}
          <div className="grid sm:grid-cols-2 gap-5">
            <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-5">
              <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                <AlertTriangle className={`w-4 h-4 ${style.icon}`} />
                Root Cause
              </h4>
              <p className="text-gray-300 text-sm leading-relaxed">{report.root_cause}</p>
            </div>

            <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-5">
              <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                <Activity className="w-4 h-4 text-orange-400" />
                Contributing Factors
              </h4>
              <ul className="space-y-2">
                {report.contributing_factors.map((f, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                    <ChevronRight className="w-4 h-4 text-orange-400 shrink-0 mt-0.5" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-5">
            <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
              <Wrench className="w-4 h-4 text-green-400" />
              Recommended Actions
            </h4>
            <div className="space-y-3">
              {report.recommendations.map((r, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-green-500/20 border border-green-500/40 flex items-center justify-center shrink-0 mt-0.5">
                    <span className="text-green-400 text-xs font-bold">{i + 1}</span>
                  </div>
                  <p className="text-gray-300 text-sm">{r}</p>
                </div>
              ))}
            </div>

            <div className="mt-5 flex gap-3">
              <a
                href="/dashboard/user/schedule"
                className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white py-2.5 rounded-xl font-semibold text-sm transition-colors"
              >
                <Clock className="w-4 h-4" />
                Schedule Service
              </a>
              <a
                href="/dashboard/user/agent-chat"
                className="flex-1 flex items-center justify-center gap-2 bg-gray-700 hover:bg-gray-600 text-white py-2.5 rounded-xl font-semibold text-sm transition-colors"
              >
                Ask AI Assistant
              </a>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between text-xs text-gray-600 px-1">
            <span>Generated {new Date(report.generated_at).toLocaleString()}</span>
            <span className="flex items-center gap-1">
              <CheckCircle className="w-3 h-3" />
              {report.generated_by === 'llm' ? 'AI-powered analysis' : 'Rule-based analysis'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
