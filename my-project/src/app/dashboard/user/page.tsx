'use client';
import { useState, useEffect } from 'react';
import { 
  Car, AlertTriangle, CheckCircle, Calendar, 
  TrendingUp, Activity, Battery, Thermometer,
  Zap, Settings, Download
} from 'lucide-react';
import VehicleCard from '@/components/dashboard/VehicleCard';
import HealthGauge from '@/components/dashboard/HealthGauge';
import AlertCard from '@/components/dashboard/AlertCard';
import RiskChart from '@/components/charts/RiskChart';
import ComponentChart from '@/components/charts/ComponentChart';
import { normalizeDashboardVehicle } from "@/lib/normalizers/vehicle";
import { useRouter } from "next/navigation";
const API_BASE = "http://localhost:8000";
export default function UserDashboard() {
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
const fetchDashboardData = async () => {
  try {
    setLoading(true);

    const [vehiclesRes, alertsRes] = await Promise.all([
      fetch(`${API_BASE}/vehicles/health/me`, { credentials: 'include' }),
      fetch(`${API_BASE}/alerts/me`, { credentials: 'include' }),
    ]);

    if (!vehiclesRes.ok || !alertsRes.ok) {
      throw new Error("Unauthorized");
    }

    const vehiclesData = await vehiclesRes.json();
    const alertsData = await alertsRes.json();

    setVehicles(vehiclesData.map(normalizeDashboardVehicle));
    setAlerts(
      alertsData.map((a: any) => ({
        ...a,
        type: a.type === "error" ? "critical" : a.type,
      }))
    );
  } catch (e) {
    console.error("Dashboard load failed", e);
    router.replace("/login");
  } finally {
    setLoading(false);
  }
};

 useEffect(() => {
    // Fetch user data
    fetchDashboardData();
  }, []);

const stats = {
  totalVehicles: vehicles?.length ?? 0,

  vehiclesAtRisk:
    vehicles?.filter(
      v => v.status === "warning" || v.status === "critical"
    ).length ?? 0,

  upcomingServices:
    vehicles?.filter(v => {
      if (!v.nextService) return false;
      const days = Math.ceil(
        (new Date(v.nextService).getTime() - Date.now()) /
        (1000 * 60 * 60 * 24)
      );
      return days <= 30;
    }).length ?? 0,

  totalAlerts: alerts?.length ?? 0
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
          <button className="flex items-center gap-2 px-4 py-2 bg-linear-to-br from-blue-600 to-cyan-600 rounded-lg hover:shadow-lg hover:shadow-blue-500/30 transition-all">
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-linear-to-br from-blue-900/30 to-blue-800/20 p-6 rounded-2xl border border-blue-800/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Vehicles</p>
              <p className="text-3xl font-bold mt-2">{stats.totalVehicles}</p>
            </div>
            <Car className="w-10 h-10 text-blue-500/50" />
          </div>
        </div>

        <div className="bg-linear-to-br from-yellow-900/20 to-yellow-800/10 p-6 rounded-2xl border border-yellow-800/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Vehicles at Risk</p>
              <p className="text-3xl font-bold mt-2 text-yellow-400">{stats.vehiclesAtRisk}</p>
            </div>
            <AlertTriangle className="w-10 h-10 text-yellow-500/50" />
          </div>
        </div>

        <div className="bg-linear-to-br from-cyan-900/20 to-cyan-800/10 p-6 rounded-2xl border border-cyan-800/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Upcoming Services</p>
              <p className="text-3xl font-bold mt-2 text-cyan-400">{stats.upcomingServices}</p>
            </div>
            <Calendar className="w-10 h-10 text-cyan-500/50" />
          </div>
        </div>

        <div className="bg-linear-to-br from-green-900/20 to-green-800/10 p-6 rounded-2xl border border-green-800/30">
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
              <button className="text-sm text-blue-400 hover:text-blue-300">
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
        ➕ Add Your First Vehicle
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
                value={vehicles.length > 0 ? vehicles.reduce((acc, v) => acc + v.health, 0) / vehicles.length : 0}
                type="health"
              />
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Battery className="w-5 h-5 text-green-500" />
                    <span className="text-gray-300">Battery Systems</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500" style={{ width: '85%' }}></div>
                    </div>
                    <span className="text-sm font-medium">85%</span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Thermometer className="w-5 h-5 text-yellow-500" />
                    <span className="text-gray-300">Cooling System</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-yellow-500" style={{ width: '72%' }}></div>
                    </div>
                    <span className="text-sm font-medium">72%</span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-blue-500" />
                    <span className="text-gray-300">Electrical System</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500" style={{ width: '91%' }}></div>
                    </div>
                    <span className="text-sm font-medium">91%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Alerts Panel */}
          <div className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700/50">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Recent Alerts</h2>
              <span className="text-sm text-gray-400">{alerts.length} total</span>
            </div>
            
            <div className="space-y-4">
              {alerts.map(alert => (
                <AlertCard key={alert.id} alert={alert} />
              ))}
            </div>
          </div>

          {/* AI Recommendations */}
          <div className="bg-linear-to-br from-blue-900/40 to-cyan-900/20 rounded-2xl p-6 border border-blue-500/30">
            <h2 className="text-xl font-semibold mb-4 text-white">🤖 AI Recommendation</h2>
            <div className="space-y-3">
              <p className="text-gray-300 text-sm">
                Based on current data, your BMW X5 shows signs of cooling system stress. 
                Recommended action:
              </p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>Schedule coolant system inspection within 7 days</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>Avoid long drives until inspection</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>Monitor engine temperature gauge</span>
                </li>
              </ul>
            </div>
            <button className="w-full mt-6 bg-linear-to-br from-blue-600 to-cyan-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/30 transition-all">
              Schedule Inspection
            </button>

          </div>
        </div>
      </div>
    </div>
  );
}