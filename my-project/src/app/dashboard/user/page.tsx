'use client';
import { useState, useEffect } from 'react';
import {
  Car, AlertTriangle, CheckCircle, Calendar,
  Activity, Battery, Thermometer,
  Zap, Download, Settings
} from 'lucide-react';
import VehicleCard from '@/components/dashboard/VehicleCard';
import HealthGauge from '@/components/dashboard/HealthGauge';
import AlertCard from '@/components/dashboard/AlertCard';
import RiskChart from '@/components/charts/RiskChart';
import ComponentChart from '@/components/charts/ComponentChart';
import { normalizeDashboardVehicle } from '@/lib/normalizers/vehicle';
import { useRouter } from 'next/navigation';
import { fetchWithAuth } from '@/lib/fetchWithAuth';

const API_BASE = 'https://ai-predictive-vehicle-maintenance-production.up.railway.app';

export default function UserDashboard() {
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      const vehiclesRes = await fetchWithAuth(`${API_BASE}/vehicles/health/me`);
      if (!vehiclesRes.ok) {
        if (vehiclesRes.status === 401) {
          router.replace('/login');
          return;
        }
        throw new Error('Failed to load vehicles');
      }
      const vehiclesData = await vehiclesRes.json();
      setVehicles(vehiclesData.map(normalizeDashboardVehicle));

      try {
        const alertsRes = await fetchWithAuth(`${API_BASE}/alerts/me`);
        if (alertsRes.ok) {
          const alertsData = await alertsRes.json();
          setAlerts(
            alertsData.map((a: any) => ({
              ...a,
              type: a.type === 'error' ? 'critical' : a.type,
            }))
          );
        }
      } catch {
        // alerts failure is non-fatal
      }
    } catch (e) {
      console.error('Dashboard load failed', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Computed stats from real data
  const avgHealth = vehicles.length > 0
    ? Math.round(vehicles.reduce((s, v) => s + v.health, 0) / vehicles.length)
    : 0;
  const avgFuel = vehicles.length > 0
    ? Math.round(vehicles.reduce((s, v) => s + (v.fuelLevel || 0), 0) / vehicles.length)
    : 0;
  const avgEngine = vehicles.length > 0
    ? Math.round(vehicles.reduce((s, v) => s + v.health, 0) / vehicles.length)
    : 0;

  // Highest-risk vehicle for AI recommendation
  const highRiskVehicle =
    vehicles.find(v => v.status === 'critical') ||
    vehicles.find(v => v.status === 'warning') ||
    null;

  const stats = {
    totalVehicles: vehicles.length,
    vehiclesAtRisk: vehicles.filter(v => v.status === 'warning' || v.status === 'critical').length,
    upcomingServices: vehicles.filter(v => {
      if (!v.nextService) return false;
      const days = Math.ceil((new Date(v.nextService).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
      return days <= 30;
    }).length,
    totalAlerts: alerts.length,
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[60vh] text-white">
        Loading dashboard...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Vehicle Health Dashboard</h1>
          <p className="text-gray-400">Welcome back! Here's your vehicle status overview</p>
        </div>
        <div className="flex items-center gap-4">
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors">
            <Download className="w-4 h-4" />
            <span>Export Report</span>
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-lg hover:shadow-lg hover:shadow-blue-500/30 transition-all">
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 p-6 rounded-2xl border border-blue-800/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Vehicles</p>
              <p className="text-3xl font-bold mt-2">{stats.totalVehicles}</p>
            </div>
            <Car className="w-10 h-10 text-blue-500/50" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-900/20 to-yellow-800/10 p-6 rounded-2xl border border-yellow-800/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Vehicles at Risk</p>
              <p className="text-3xl font-bold mt-2 text-yellow-400">{stats.vehiclesAtRisk}</p>
            </div>
            <AlertTriangle className="w-10 h-10 text-yellow-500/50" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-cyan-900/20 to-cyan-800/10 p-6 rounded-2xl border border-cyan-800/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Upcoming Services</p>
              <p className="text-3xl font-bold mt-2 text-cyan-400">{stats.upcomingServices}</p>
            </div>
            <Calendar className="w-10 h-10 text-cyan-500/50" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-900/20 to-green-800/10 p-6 rounded-2xl border border-green-800/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Alerts</p>
              <p className="text-3xl font-bold mt-2 text-green-400">{stats.totalAlerts}</p>
            </div>
            <Activity className="w-10 h-10 text-green-500/50" />
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Vehicle Cards */}
          <div className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700/50">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">My Vehicles</h2>
              <button
                onClick={() => router.push('/dashboard/user/vehicles')}
                className="text-sm text-blue-400 hover:text-blue-300"
              >
                View All →
              </button>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              {vehicles.length === 0 ? (
                <div className="col-span-full text-center py-8 text-gray-400">
                  <p className="mb-4">No vehicles added yet.</p>
                  <button
                    onClick={() => router.push('/dashboard/user/vehicles/add')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500"
                  >
                    Add Your First Vehicle
                  </button>
                </div>
              ) : (
                vehicles.map(vehicle => (
                  <VehicleCard key={vehicle.id} vehicle={vehicle} />
                ))
              )}
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700/50">
              <h3 className="text-lg font-semibold mb-4 text-white">Failure Risk Trend</h3>
              <div className="h-64">
                <RiskChart />
              </div>
            </div>
            <div className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700/50">
              <h3 className="text-lg font-semibold mb-4 text-white">Component Health</h3>
              <div className="h-64">
                <ComponentChart />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Health Overview */}
          <div className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700/50">
            <h2 className="text-xl font-semibold mb-6 text-white">Health Overview</h2>
            <div className="space-y-6">
              <HealthGauge
                title="Overall Fleet Health"
                value={avgHealth}
                type="health"
              />

              {vehicles.length === 0 ? (
                <p className="text-gray-500 text-sm text-center">Add vehicles to see health metrics.</p>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Zap className="w-5 h-5 text-green-500" />
                      <span className="text-gray-300">Engine Health</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${avgEngine > 70 ? 'bg-green-500' : avgEngine > 40 ? 'bg-yellow-500' : 'bg-red-500'}`}
                          style={{ width: `${avgEngine}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{avgEngine}%</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Battery className="w-5 h-5 text-blue-500" />
                      <span className="text-gray-300">Avg Fuel Level</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${avgFuel > 50 ? 'bg-blue-500' : avgFuel > 20 ? 'bg-yellow-500' : 'bg-red-500'}`}
                          style={{ width: `${avgFuel}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{avgFuel}%</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Thermometer className="w-5 h-5 text-yellow-500" />
                      <span className="text-gray-300">Vehicles Analysed</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-white">
                        {vehicles.filter(v => v.riskLevel).length}/{vehicles.length}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Alerts Panel */}
          <div className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700/50">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Recent Alerts</h2>
              <span className="text-sm text-gray-400">{alerts.length} total</span>
            </div>
            <div className="space-y-4">
              {alerts.length === 0 ? (
                <p className="text-gray-500 text-sm">
                  No alerts.{vehicles.length > 0 && !vehicles.some(v => v.riskLevel) && (
                    <span> Run AI Analysis on your vehicles to generate alerts.</span>
                  )}
                </p>
              ) : (
                alerts.map(alert => (
                  <AlertCard key={alert.id} alert={alert} />
                ))
              )}
            </div>
          </div>

          {/* AI Recommendation */}
          <div className="bg-gradient-to-br from-blue-900/40 to-cyan-900/20 rounded-2xl p-6 border border-blue-500/30">
            <h2 className="text-xl font-semibold mb-4 text-white">AI Recommendation</h2>

            {highRiskVehicle ? (
              <div className="space-y-3">
                <p className="text-gray-300 text-sm">
                  Your <span className="text-white font-medium">{highRiskVehicle.name}</span> shows{' '}
                  <span className={highRiskVehicle.status === 'critical' ? 'text-red-400 font-semibold' : 'text-yellow-400 font-semibold'}>
                    {highRiskVehicle.riskLevel || highRiskVehicle.status.toUpperCase()} risk
                  </span>
                  {highRiskVehicle.affectedComponent && (
                    <> in the {highRiskVehicle.affectedComponent} system</>
                  )}.
                  {highRiskVehicle.failureProbability !== null && (
                    <> Engine failure probability: <span className="text-white font-medium">{Math.round(highRiskVehicle.failureProbability * 100)}%</span>.</>
                  )}
                </p>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 shrink-0" />
                    <span>
                      {highRiskVehicle.status === 'critical'
                        ? 'Schedule immediate inspection within 2–3 days'
                        : 'Schedule inspection within the week'}
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 shrink-0" />
                    <span>Avoid long-distance drives until serviced</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 shrink-0" />
                    <span>Monitor warning lights and engine temperature</span>
                  </li>
                </ul>
                <button
                  onClick={() => router.push(`/dashboard/user/schedule`)}
                  className="w-full mt-2 bg-gradient-to-br from-blue-600 to-cyan-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/30 transition-all"
                >
                  Schedule Inspection
                </button>
              </div>
            ) : vehicles.length === 0 ? (
              <div className="space-y-3">
                <p className="text-gray-400 text-sm">Add a vehicle and run AI analysis to get personalised recommendations.</p>
                <button
                  onClick={() => router.push('/dashboard/user/vehicles/add')}
                  className="w-full bg-gradient-to-br from-blue-600 to-cyan-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transition-all"
                >
                  Add Vehicle
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-gray-400 text-sm">
                  All vehicles are in good health.{' '}
                  {!vehicles.some(v => v.riskLevel) && 'Run AI Analysis for detailed insights.'}
                </p>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 shrink-0" />
                    <span>Keep up with scheduled maintenance</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 shrink-0" />
                    <span>Run AI analysis regularly for early detection</span>
                  </li>
                </ul>
                <button
                  onClick={() => router.push('/dashboard/user/analysis')}
                  className="w-full mt-2 bg-gradient-to-br from-blue-600 to-cyan-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transition-all"
                >
                  Run AI Analysis
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
