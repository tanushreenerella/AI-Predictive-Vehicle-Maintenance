'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Car, Plus, CheckCircle, Activity, Calendar, Gauge } from 'lucide-react';
import { fetchWithAuth } from '@/lib/fetchWithAuth';

const API_BASE = 'https://ai-predictive-vehicle-maintenance-production.up.railway.app';

type Vehicle = {
  id: number | string;
  name: string;
  model: string;
  year?: number;
  registration_number?: string;
  ai_risk_level?: string | null;
  health?: number | null;
  ai_failure_probability?: number | null;
  ai_last_analyzed?: string | null;
};

function riskBadge(level?: string | null) {
  if (level === 'HIGH' || level === 'CRITICAL')
    return { label: level, cls: 'bg-red-500/10 text-red-400 border-red-500/20' };
  if (level === 'MEDIUM')
    return { label: 'MEDIUM', cls: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' };
  if (level === 'LOW')
    return { label: 'LOW', cls: 'bg-green-500/10 text-green-400 border-green-500/20' };
  return null;
}

function healthColor(score?: number | null) {
  if (score == null) return 'bg-gray-600';
  if (score > 75) return 'bg-blue-500';
  if (score > 50) return 'bg-yellow-500';
  return 'bg-red-500';
}

export default function MyVehiclesPage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchWithAuth(`${API_BASE}/vehicles/health/me`)
      .then(r => r.ok ? r.json() : [])
      .then(setVehicles)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="w-7 h-7 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">My Vehicles</h1>
          <p className="text-gray-500 text-sm mt-0.5">{vehicles.length} vehicle{vehicles.length !== 1 ? 's' : ''} registered</p>
        </div>
        <button
          onClick={() => router.push('/dashboard/user/vehicles/add')}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Vehicle
        </button>
      </div>

      {vehicles.length === 0 ? (
        <div className="bg-gray-800/40 border border-gray-700/60 rounded-2xl p-12 text-center">
          <Car className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400 mb-1">No vehicles registered yet</p>
          <p className="text-gray-600 text-sm mb-5">Add your first vehicle to start monitoring its health</p>
          <button
            onClick={() => router.push('/dashboard/user/vehicles/add')}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl transition-colors"
          >
            Add Your First Vehicle
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {vehicles.map(v => {
            const badge = riskBadge(v.ai_risk_level);
            const prob = v.ai_failure_probability;
            const health = typeof v.health === 'number'
              ? v.health
              : typeof prob === 'number'
                ? Math.max(0, Math.round(100 - prob * 100))
                : null;

            return (
              <div
                key={v.id}
                onClick={() => router.push(`/dashboard/user/vehicles/${v.id}`)}
                className="bg-gray-800/40 border border-gray-700/60 hover:border-gray-600 rounded-2xl p-5 cursor-pointer transition-colors group"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-700/60 rounded-xl group-hover:bg-gray-700 transition-colors">
                      <Car className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white text-sm leading-tight">{v.name}</h3>
                      <p className="text-gray-500 text-xs">{v.model}{v.year ? ` · ${v.year}` : ''}</p>
                    </div>
                  </div>
                  {badge ? (
                    <span className={`text-xs px-2 py-0.5 rounded-full border font-medium shrink-0 ${badge.cls}`}>
                      {badge.label}
                    </span>
                  ) : (
                    <CheckCircle className="w-4 h-4 text-gray-600 shrink-0" />
                  )}
                </div>

                {/* Health bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="text-gray-500">Health Score</span>
                    <span className="text-gray-300 font-medium">{health != null ? `${health}%` : 'Not analysed'}</span>
                  </div>
                  <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${healthColor(health)}`}
                      style={{ width: health != null ? `${health}%` : '0%' }}
                    />
                  </div>
                </div>

                {/* Stats row */}
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  {v.registration_number && (
                    <span className="flex items-center gap-1">
                      <Gauge className="w-3 h-3" />
                      {v.registration_number}
                    </span>
                  )}
                  {v.ai_last_analyzed ? (
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {new Date(v.ai_last_analyzed).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-gray-600">
                      <Activity className="w-3 h-3" />
                      Not analysed
                    </span>
                  )}
                </div>

                {/* CTA row */}
                <div className="flex gap-2 mt-4 pt-4 border-t border-gray-700/60">
                  <button
                    onClick={e => { e.stopPropagation(); router.push(`/dashboard/user/analysis?vehicle_id=${v.id}`); }}
                    className="flex-1 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition-colors"
                  >
                    Run Analysis
                  </button>
                  <button
                    onClick={e => { e.stopPropagation(); router.push(`/dashboard/user/vehicles/${v.id}`); }}
                    className="flex-1 py-2 bg-gray-700/60 hover:bg-gray-700 text-gray-300 text-xs font-medium rounded-lg transition-colors"
                  >
                    View Details
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
