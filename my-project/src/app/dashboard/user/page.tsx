'use client';
import { useState, useEffect } from 'react';
import {
  Car, AlertTriangle, CheckCircle, Calendar,
  Activity, Battery, Zap, Download, Bot, FileText, ArrowRight
} from 'lucide-react';
import VehicleCard from '@/components/dashboard/VehicleCard';
import AlertCard from '@/components/dashboard/AlertCard';
import { normalizeDashboardVehicle } from '@/lib/normalizers/vehicle';
import { useRouter } from 'next/navigation';
import { fetchWithAuth } from '@/lib/fetchWithAuth';

const API_BASE = 'https://ai-predictive-vehicle-maintenance-production.up.railway.app';

export default function UserDashboard() {
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [userName, setUserName] = useState('');
  const router = useRouter();

  useEffect(() => {
    const load = async () => {
      try {
        const [vRes, aRes, uRes] = await Promise.all([
          fetchWithAuth(`${API_BASE}/vehicles/health/me`),
          fetchWithAuth(`${API_BASE}/alerts/me`).catch(() => null),
          fetchWithAuth(`${API_BASE}/auth/me`).catch(() => null),
        ]);

        if (!vRes.ok) {
          if (vRes.status === 401) { router.replace('/login'); return; }
          throw new Error();
        }

        const vData = await vRes.json();
        setVehicles(vData.map(normalizeDashboardVehicle));

        if (aRes?.ok) {
          const aData = await aRes.json();
          setAlerts(aData.map((a: any) => ({ ...a, type: a.type === 'error' ? 'critical' : a.type })));
        }
        if (uRes?.ok) {
          const uData = await uRes.json();
          setUserName(uData.name || uData.email?.split('@')[0] || '');
        }
      } catch {
        // non-fatal
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [router]);

  const totalVehicles = vehicles.length;
  const atRisk = vehicles.filter(v => v.status === 'warning' || v.status === 'critical').length;
  const analysed = vehicles.filter(v => v.riskLevel).length;
  const avgHealth = totalVehicles > 0
    ? Math.round(vehicles.reduce((s, v) => s + v.health, 0) / totalVehicles)
    : 0;
  const avgFuel = totalVehicles > 0
    ? Math.round(vehicles.reduce((s, v) => s + (v.fuelLevel || 0), 0) / totalVehicles)
    : 0;

  const highRisk = vehicles.find(v => v.status === 'critical') || vehicles.find(v => v.status === 'warning');

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-400">Loading your dashboard…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">

      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">
            {userName ? `Welcome back, ${userName}` : 'Vehicle Dashboard'}
          </h1>
          <p className="text-gray-400 mt-1">Here's your fleet health overview</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => router.push('/dashboard/user/reports')}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl text-gray-300 text-sm transition-colors"
          >
            <FileText className="w-4 h-4" />
            Reports
          </button>
          <button
            onClick={() => router.push('/dashboard/user/analysis')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-xl text-white text-sm font-medium transition-colors"
          >
            <Activity className="w-4 h-4" />
            Run Analysis
          </button>
        </div>
      </div>

      {/* ── Stat cards ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            label: 'Total Vehicles', value: totalVehicles, icon: Car,
            color: 'from-blue-900/40 to-blue-800/20 border-blue-800/40', iconColor: 'text-blue-400',
          },
          {
            label: 'Vehicles at Risk', value: atRisk, icon: AlertTriangle,
            color: 'from-red-900/30 to-red-800/10 border-red-800/30', iconColor: 'text-red-400',
            valueColor: atRisk > 0 ? 'text-red-400' : 'text-white',
          },
          {
            label: 'Fleet Health', value: `${avgHealth}%`, icon: Activity,
            color: 'from-green-900/30 to-green-800/10 border-green-800/30', iconColor: 'text-green-400',
            valueColor: avgHealth > 70 ? 'text-green-400' : avgHealth > 40 ? 'text-yellow-400' : 'text-red-400',
          },
          {
            label: 'Active Alerts', value: alerts.length, icon: Calendar,
            color: 'from-purple-900/30 to-purple-800/10 border-purple-800/30', iconColor: 'text-purple-400',

          },
        ].map(({ label, value, icon: Icon, color, iconColor, valueColor }) => (
          <div key={label} className={`bg-linear-to-br ${color} border rounded-2xl p-5`}>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-gray-400 text-sm">{label}</p>
                <p className={`text-3xl font-bold mt-2 ${valueColor || 'text-white'}`}>{value}</p>
              </div>
              <div className="p-2 bg-black/20 rounded-xl">
                <Icon className={`w-5 h-5 ${iconColor}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* ── Main grid ── */}
      <div className="grid lg:grid-cols-3 gap-6">

        {/* Left 2/3 */}
        <div className="lg:col-span-2 space-y-6">

          {/* Vehicles */}
          <section className="bg-gray-800/40 rounded-2xl border border-gray-700/60 p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold text-white">My Vehicles</h2>
              <button
                onClick={() => router.push('/dashboard/user/vehicles')}
                className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
              >
                View all <ArrowRight className="w-3 h-3" />
              </button>
            </div>
            {totalVehicles === 0 ? (
              <div className="flex flex-col items-center py-10 text-center">
                <Car className="w-12 h-12 text-gray-600 mb-3" />
                <p className="text-gray-400 mb-4">No vehicles added yet</p>
                <button
                  onClick={() => router.push('/dashboard/user/vehicles/add')}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-medium"
                >
                  Add Your First Vehicle
                </button>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 gap-4">
                {vehicles.map(v => <VehicleCard key={v.id} vehicle={v} />)}
              </div>
            )}
          </section>

          {/* Quick-access strips */}
          <div className="grid sm:grid-cols-2 gap-4">
            <button
              onClick={() => router.push('/dashboard/user/analysis')}
              className="flex items-center gap-4 bg-linear-to-br from-blue-900/40 to-cyan-900/20 border border-blue-700/40 rounded-2xl p-5 hover:border-blue-500/60 transition-colors text-left"
            >
              <div className="p-3 bg-blue-500/20 rounded-xl">
                <Activity className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <p className="font-semibold text-white">AI Analysis</p>
                <p className="text-gray-400 text-sm">Run ML prediction on sensor data</p>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-500 ml-auto shrink-0" />
            </button>

            <button
              onClick={() => router.push('/dashboard/user/reports')}
              className="flex items-center gap-4 bg-linear-to-br from-purple-900/40 to-pink-900/20 border border-purple-700/40 rounded-2xl p-5 hover:border-purple-500/60 transition-colors text-left"
            >
              <div className="p-3 bg-purple-500/20 rounded-xl">
                <FileText className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <p className="font-semibold text-white">RCA Reports</p>
                <p className="text-gray-400 text-sm">Root cause analysis for your fleet</p>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-500 ml-auto shrink-0" />
            </button>
          </div>
        </div>

        {/* Right 1/3 */}
        <div className="space-y-5">

          {/* Fleet health summary */}
          <section className="bg-gray-800/40 rounded-2xl border border-gray-700/60 p-5">
            <h2 className="text-base font-semibold text-white mb-4">Fleet Health</h2>
            <div className="space-y-4">
              {[
                { label: 'Overall Health', value: avgHealth, icon: Activity, color: avgHealth > 70 ? 'bg-green-500' : avgHealth > 40 ? 'bg-yellow-500' : 'bg-red-500' },
                { label: 'Avg Fuel Level', value: avgFuel, icon: Battery, color: avgFuel > 50 ? 'bg-blue-500' : avgFuel > 20 ? 'bg-yellow-500' : 'bg-red-500' },
              ].map(({ label, value, icon: Icon, color }) => (
                <div key={label}>
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-2">
                      <Icon className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-300">{label}</span>
                    </div>
                    <span className="text-sm font-semibold text-white">{value}%</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${color} transition-all duration-700`} style={{ width: `${value}%` }} />
                  </div>
                </div>
              ))}

              <div className="flex items-center justify-between pt-1">
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-300">Vehicles Analysed</span>
                </div>
                <span className="text-sm font-semibold text-white">{analysed}/{totalVehicles}</span>
              </div>

              {totalVehicles > 0 && analysed === 0 && (
                <button
                  onClick={() => router.push('/dashboard/user/analysis')}
                  className="w-full mt-1 text-xs text-blue-400 underline text-left"
                >
                  Run AI Analysis to populate health data →
                </button>
              )}
            </div>
          </section>

          {/* Alerts */}
          <section className="bg-gray-800/40 rounded-2xl border border-gray-700/60 p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-white">Recent Alerts</h2>
              <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${alerts.length > 0 ? 'bg-red-500/20 text-red-400' : 'bg-gray-700 text-gray-400'}`}>
                {alerts.length} total
              </span>
            </div>
            {alerts.length === 0 ? (
              <div className="text-center py-4">
                <CheckCircle className="w-8 h-8 text-green-500/50 mx-auto mb-2" />
                <p className="text-gray-500 text-sm">No alerts — all clear</p>
                {totalVehicles > 0 && analysed === 0 && (
                  <p className="text-gray-600 text-xs mt-1">Run AI Analysis to generate alerts</p>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                {alerts.slice(0, 3).map(alert => (
                  <AlertCard key={alert.id} alert={alert} />
                ))}
                {alerts.length > 3 && (
                  <p className="text-xs text-gray-500 text-center pt-1">+{alerts.length - 3} more alerts</p>
                )}
              </div>
            )}
          </section>

          {/* AI Recommendation */}
          <section className={`rounded-2xl border p-5 ${highRisk
            ? highRisk.status === 'critical'
              ? 'bg-red-900/20 border-red-700/40'
              : 'bg-yellow-900/20 border-yellow-700/40'
            : 'bg-linear-to-br from-blue-900/30 to-cyan-900/20 border-blue-700/40'
          }`}>
            <div className="flex items-center gap-2 mb-3">
              <Bot className={`w-5 h-5 ${highRisk?.status === 'critical' ? 'text-red-400' : highRisk?.status === 'warning' ? 'text-yellow-400' : 'text-blue-400'}`} />
              <h2 className="text-base font-semibold text-white">AI Recommendation</h2>
            </div>

            {highRisk ? (
              <>
                <p className="text-gray-300 text-sm mb-3">
                  Your <span className="text-white font-medium">{highRisk.name}</span> shows{' '}
                  <span className={`font-semibold ${highRisk.status === 'critical' ? 'text-red-400' : 'text-yellow-400'}`}>
                    {highRisk.riskLevel || highRisk.status.toUpperCase()} risk
                  </span>
                  {highRisk.failureProbability !== null && (
                    <> · <span className="text-white font-medium">{Math.round(highRisk.failureProbability * 100)}%</span> failure probability</>
                  )}
                  {highRisk.affectedComponent && <> · {highRisk.affectedComponent} system</>}.
                </p>
                <ul className="space-y-1.5 mb-4">
                  {[
                    highRisk.status === 'critical' ? 'Schedule inspection within 48 hours' : 'Schedule service this week',
                    'Avoid long-distance drives until serviced',
                    'Monitor engine temperature and warning lights',
                  ].map(t => (
                    <li key={t} className="flex items-start gap-2 text-sm text-gray-300">
                      <CheckCircle className="w-4 h-4 text-green-500 shrink-0 mt-0.5" />
                      {t}
                    </li>
                  ))}
                </ul>
                <div className="flex gap-2">
                  <button
                    onClick={() => router.push('/dashboard/user/schedule')}
                    className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2.5 rounded-xl text-sm font-semibold transition-colors"
                  >
                    Book Service
                  </button>
                  <button
                    onClick={() => router.push('/dashboard/user/reports')}
                    className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2.5 rounded-xl text-sm font-semibold transition-colors"
                  >
                    View RCA
                  </button>
                </div>
              </>
            ) : totalVehicles === 0 ? (
              <>
                <p className="text-gray-400 text-sm mb-4">Add a vehicle and run AI Analysis to get personalised recommendations.</p>
                <button
                  onClick={() => router.push('/dashboard/user/vehicles/add')}
                  className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2.5 rounded-xl text-sm font-semibold transition-colors"
                >
                  Add Vehicle
                </button>
              </>
            ) : (
              <>
                <p className="text-gray-400 text-sm mb-4">
                  {analysed > 0 ? 'All vehicles are in good health.' : 'Run AI Analysis for personalised insights.'}
                </p>
                <button
                  onClick={() => router.push('/dashboard/user/analysis')}
                  className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2.5 rounded-xl text-sm font-semibold transition-colors"
                >
                  Run AI Analysis
                </button>
              </>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
