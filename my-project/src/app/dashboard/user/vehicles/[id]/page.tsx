"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { Activity, ArrowLeft, Car } from "lucide-react";
import { fetchWithAuth } from "@/lib/fetchWithAuth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://ai-predictive-vehicle-maintenance-qdst.onrender.com";

type Vehicle = {
  id: string;
  name: string;
  model: string;
  year?: number;
  registration_number?: string;
  mileage?: number;
  fuel_level?: number;
  analyzed?: boolean;
  health?: number | null;
  ai_risk_level?: string | null;
  ai_failure_probability?: number | null;
  ai_component?: string | null;
  ai_last_analyzed?: string | null;
};

export default function VehicleDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const vehicleId = Array.isArray(params.id) ? params.id[0] : params.id;
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!vehicleId) return;
    // This ownership-scoped endpoint includes vehicles with no saved analysis.
    fetchWithAuth(`${API_BASE}/vehicles/health/${encodeURIComponent(vehicleId)}`)
      .then(async response => {
        if (!response.ok) throw new Error("Unable to load vehicle");
        setVehicle(await response.json());
      })
      .catch(() => setVehicle(null))
      .finally(() => setLoading(false));
  }, [vehicleId]);

  if (loading) {
    return <div className="flex h-48 items-center justify-center"><div className="h-7 w-7 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" /></div>;
  }

  if (!vehicle) {
    return (
      <div className="rounded-2xl border border-gray-700/60 bg-gray-800/40 p-10 text-center">
        <Car className="mx-auto mb-3 h-10 w-10 text-gray-600" />
        <h1 className="text-xl font-semibold text-white">Vehicle not found</h1>
        <p className="mt-2 text-sm text-gray-400">This vehicle is unavailable or does not belong to your account.</p>
        <Link href="/dashboard/user/vehicles" className="mt-5 inline-flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300"><ArrowLeft className="h-4 w-4" />Back to vehicles</Link>
      </div>
    );
  }

  const probability = vehicle.ai_failure_probability;
  const health = vehicle.health ?? (typeof probability === "number" ? Math.max(0, Math.round(100 - probability * 100)) : null);
  const risk = vehicle.ai_risk_level ?? "Not analysed";
  const riskClass = risk === "HIGH" ? "text-red-400" : risk === "MEDIUM" ? "text-yellow-400" : risk === "LOW" ? "text-green-400" : "text-gray-400";

  return (
    <div className="space-y-6">
      <Link href="/dashboard/user/vehicles" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white"><ArrowLeft className="h-4 w-4" />All vehicles</Link>
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
        <div className="flex gap-4"><div className="rounded-xl bg-blue-500/15 p-3"><Car className="h-7 w-7 text-blue-400" /></div><div><h1 className="text-3xl font-bold text-white">{vehicle.name}</h1><p className="mt-1 text-gray-400">{vehicle.model}{vehicle.year ? ` · ${vehicle.year}` : ""}</p></div></div>
        <button onClick={() => router.push(`/dashboard/user/analysis?vehicle_id=${vehicle.id}`)} className="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-500">Run Analysis</button>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <section className="rounded-2xl border border-gray-700/60 bg-gray-800/40 p-5"><p className="text-sm text-gray-400">Risk level</p><p className={`mt-2 text-2xl font-bold ${riskClass}`}>{risk}</p></section>
        <section className="rounded-2xl border border-gray-700/60 bg-gray-800/40 p-5"><p className="text-sm text-gray-400">Failure probability</p><p className="mt-2 text-2xl font-bold text-white">{typeof probability === "number" ? `${Math.round(probability * 100)}%` : "—"}</p></section>
        <section className="rounded-2xl border border-gray-700/60 bg-gray-800/40 p-5"><p className="text-sm text-gray-400">Health score</p><p className="mt-2 text-2xl font-bold text-white">{health == null ? "Not analysed" : `${health}%`}</p></section>
      </div>
      <section className="rounded-2xl border border-gray-700/60 bg-gray-800/40 p-6"><h2 className="mb-4 text-lg font-semibold text-white">Vehicle details</h2><div className="grid gap-4 text-sm sm:grid-cols-2"><p className="text-gray-400">Registration <span className="ml-2 text-white">{vehicle.registration_number ?? "—"}</span></p><p className="text-gray-400">Mileage <span className="ml-2 text-white">{vehicle.mileage?.toLocaleString() ?? "—"}</span></p><p className="text-gray-400">Fuel level <span className="ml-2 text-white">{vehicle.fuel_level ?? "—"}%</span></p><p className="text-gray-400">Last analysis <span className="ml-2 text-white">{vehicle.ai_last_analyzed ? new Date(vehicle.ai_last_analyzed).toLocaleString() : "Not analysed"}</span></p></div></section>
      {!vehicle.analyzed && <div className="flex items-center gap-2 rounded-xl border border-blue-500/25 bg-blue-500/10 p-4 text-sm text-blue-200"><Activity className="h-5 w-5" />Run an analysis to see this vehicle’s ML risk assessment.</div>}
    </div>
  );
}
