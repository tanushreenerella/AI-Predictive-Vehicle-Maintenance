'use client';

import { useState, useEffect } from 'react';
import { 
  Users, Car, Server, AlertTriangle, 
  BarChart3, Activity, Cpu, Zap,
  TrendingUp, Settings, Download, Filter
} from 'lucide-react';
import RiskChart from '@/components/charts/RiskChart';

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    totalVehicles: 0,
    vehiclesAtRisk: 0,
    activeAlerts: 0,
    systemHealth: 0
  });
  const [agentStatus, setAgentStatus] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data
      setStats({
        totalVehicles: 156,
        vehiclesAtRisk: 12,
        activeAlerts: 47,
        systemHealth: 98.5
      });

      setAgentStatus([
        { name: 'Master Orchestrator', status: 'active', cpu: 45, memory: 72, latency: 120 },
        { name: 'Failure Prediction', status: 'active', cpu: 28, memory: 56, latency: 85 },
        { name: 'Diagnostic Agent', status: 'active', cpu: 32, memory: 48, latency: 95 },
        { name: 'Service Recommender', status: 'active', cpu: 24, memory: 41, latency: 110 },
        { name: 'RCA Analysis', status: 'warning', cpu: 68, memory: 79, latency: 250 }
      ]);
    } catch (error) {
      console.error('Failed to fetch admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const recentActivities = [
    { id: 1, action: 'Engine failure predicted', vehicle: 'VIN-12345', time: '2 mins ago', type: 'prediction' },
    { id: 2, action: 'Service scheduled', vehicle: 'VIN-67890', time: '15 mins ago', type: 'service' },
    { id: 3, action: 'High risk alert triggered', vehicle: 'VIN-11223', time: '1 hour ago', type: 'alert' },
    { id: 4, action: 'System backup completed', vehicle: 'System', time: '2 hours ago', type: 'system' },
    { id: 5, action: 'ML model retrained', vehicle: 'System', time: '4 hours ago', type: 'system' }
  ];

  const systemMetrics = [
    { label: 'API Response Time', value: '245ms', target: '<500ms', status: 'good' },
    { label: 'Prediction Accuracy', value: '92.4%', target: '>90%', status: 'good' },
    { label: 'System Uptime', value: '99.8%', target: '99.9%', status: 'warning' },
    { label: 'Data Processing', value: '1.2M/day', target: '2M/day', status: 'good' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">System Administration</h1>
          <p className="text-gray-400">Monitor and manage the ProactiveAI system</p>
        </div>
        <div className="flex items-center gap-4">
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors">
            <Filter className="w-4 h-4" />
            <span>Filter</span>
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-linear-to-br from-blue-600 to-cyan-600 rounded-lg hover:shadow-lg hover:shadow-blue-500/30 transition-all">
            <Settings className="w-4 h-4" />
            <span>System Settings</span>
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

        <div className="bg-linear-to-br from-red-900/20 to-red-800/10 p-6 rounded-2xl border border-red-800/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Vehicles at Risk</p>
              <p className="text-3xl font-bold mt-2 text-red-400">{stats.vehiclesAtRisk}</p>
            </div>
            <AlertTriangle className="w-10 h-10 text-red-500/50" />
          </div>
        </div>

        <div className="bg-linear-to-br from-green-900/20 to-green-800/10 p-6 rounded-2xl border border-green-800/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Alerts</p>
              <p className="text-3xl font-bold mt-2 text-green-400">{stats.activeAlerts}</p>
            </div>
            <Activity className="w-10 h-10 text-green-500/50" />
          </div>
        </div>

        <div className="bg-linear-to-br from-cyan-900/20 to-cyan-800/10 p-6 rounded-2xl border border-cyan-800/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">System Health</p>
              <p className="text-3xl font-bold mt-2 text-cyan-400">{stats.systemHealth}%</p>
            </div>
            <Server className="w-10 h-10 text-cyan-500/50" />
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Agent Status */}
        <div className="lg:col-span-2 space-y-6">
          {/* Agent Status */}
          <div className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700/50">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">🤖 AI Agent Status</h2>
              <span className="text-sm text-gray-400">{agentStatus.filter(a => a.status === 'active').length}/{agentStatus.length} Active</span>
            </div>
            
            <div className="space-y-4">
              {agentStatus.map((agent, index) => (
                <div key={index} className="bg-gray-900/50 p-4 rounded-xl border border-gray-700/30">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${agent.status === 'active' ? 'bg-green-500' : 'bg-yellow-500'}`} />
                      <div>
                        <h3 className="font-semibold text-white">{agent.name}</h3>
                        <p className="text-sm text-gray-400">Status: {agent.status}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-6">
                      <div className="text-center">
                        <div className="text-sm text-gray-400">CPU</div>
                        <div className={`font-semibold ${agent.cpu > 60 ? 'text-yellow-400' : 'text-green-400'}`}>
                          {agent.cpu}%
                        </div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-sm text-gray-400">Memory</div>
                        <div className={`font-semibold ${agent.memory > 70 ? 'text-yellow-400' : 'text-green-400'}`}>
                          {agent.memory}%
                        </div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-sm text-gray-400">Latency</div>
                        <div className={`font-semibold ${agent.latency > 200 ? 'text-yellow-400' : 'text-green-400'}`}>
                          {agent.latency}ms
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* System Metrics */}
          <div className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700/50">
            <h2 className="text-xl font-semibold mb-6 text-white">System Metrics</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {systemMetrics.map((metric, index) => (
                <div key={index} className="bg-gray-900/50 p-4 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300">{metric.label}</span>
                    <div className={`px-2 py-1 rounded text-xs font-medium ${
                      metric.status === 'good' ? 'bg-green-500/20 text-green-400' :
                      metric.status === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {metric.status}
                    </div>
                  </div>
                  <div className="flex items-baseline justify-between">
                    <div className="text-2xl font-bold text-white">{metric.value}</div>
                    <div className="text-sm text-gray-500">Target: {metric.target}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Recent Activity */}
          <div className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700/50">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Recent Activity</h2>
              <button className="text-sm text-blue-400 hover:text-blue-300">
                View All →
              </button>
            </div>
            
            <div className="space-y-4">
              {recentActivities.map(activity => (
                <div key={activity.id} className="flex items-start gap-3 p-3 bg-gray-900/30 rounded-lg">
                  <div className={`p-2 rounded ${
                    activity.type === 'prediction' ? 'bg-blue-500/20' :
                    activity.type === 'service' ? 'bg-green-500/20' :
                    activity.type === 'alert' ? 'bg-red-500/20' : 'bg-gray-500/20'
                  }`}>
                    {activity.type === 'prediction' && <Cpu className="w-4 h-4 text-blue-400" />}
                    {activity.type === 'service' && <Zap className="w-4 h-4 text-green-400" />}
                    {activity.type === 'alert' && <AlertTriangle className="w-4 h-4 text-red-400" />}
                    {activity.type === 'system' && <Server className="w-4 h-4 text-gray-400" />}
                  </div>
                  
                  <div className="flex-1">
                    <p className="text-sm text-white">{activity.action}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-500">{activity.vehicle}</span>
                      <span className="text-xs text-gray-600">•</span>
                      <span className="text-xs text-gray-500">{activity.time}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-linear-to-br from-blue-900/40 to-cyan-900/20 rounded-2xl p-6 border border-blue-500/30">
            <h2 className="text-xl font-semibold mb-4 text-white">⚡ Quick Actions</h2>
            <div className="space-y-3">
              <button className="w-full flex items-center justify-between p-3 bg-blue-600/20 hover:bg-blue-600/30 rounded-lg transition-colors">
                <div className="flex items-center gap-3">
                  <BarChart3 className="w-5 h-5" />
                  <span>Run System Diagnostics</span>
                </div>
                <TrendingUp className="w-4 h-4" />
              </button>
              
              <button className="w-full flex items-center justify-between p-3 bg-blue-600/20 hover:bg-blue-600/30 rounded-lg transition-colors">
                <div className="flex items-center gap-3">
                  <Activity className="w-5 h-5" />
                  <span>Check API Status</span>
                </div>
                <Zap className="w-4 h-4" />
              </button>
              
              <button className="w-full flex items-center justify-between p-3 bg-blue-600/20 hover:bg-blue-600/30 rounded-lg transition-colors">
                <div className="flex items-center gap-3">
                  <Download className="w-5 h-5" />
                  <span>Generate Reports</span>
                </div>
                <BarChart3 className="w-4 h-4" />
              </button>
              
              <button className="w-full flex items-center justify-between p-3 bg-blue-600/20 hover:bg-blue-600/30 rounded-lg transition-colors">
                <div className="flex items-center gap-3">
                  <Users className="w-5 h-5" />
                  <span>Manage Users</span>
                </div>
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Risk Distribution */}
          <div className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700/50">
            <h2 className="text-xl font-semibold mb-4 text-white">Risk Distribution</h2>
            <div className="h-48">
              <RiskChart />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}