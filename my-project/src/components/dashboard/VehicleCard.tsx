'use client';

import { Car, AlertTriangle, CheckCircle, Battery, Thermometer, Zap, Settings,Calendar } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
interface VehicleCardProps {
  vehicle: {
    id: number;
    name: string;
    registration: string;
    health: number;
    status: 'optimal' | 'warning' | 'critical';
    lastService?: string;
    nextService?: string;
    mileage: number;
    fuelLevel: number;
  };
}
const API_BASE = "http://localhost:8000";

export default function VehicleCard({ vehicle }: VehicleCardProps) {
  const router = useRouter();
const [running, setRunning] = useState(false);

  const runAI = async () => {
    try {
      setRunning(true);
      await fetch(
        `${API_BASE}/vehicles/run/${vehicle.id}`,
        {
          method: "POST",
          credentials: "include",
        }
      );
      // refresh dashboard data
      window.location.reload();
    } catch (err) {
      console.error("AI run failed", err);
    } finally {
      setRunning(false);
    }
  };
  const getStatusColor = () => {
    switch (vehicle.status) {
      case 'optimal': return 'border-green-500/50 bg-green-500/10';
      case 'warning': return 'border-yellow-500/50 bg-yellow-500/10';
      case 'critical': return 'border-red-500/50 bg-red-500/10';
    }
  };

  const getStatusIcon = () => {
    switch (vehicle.status) {
      case 'optimal': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'critical': return <AlertTriangle className="w-5 h-5 text-red-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

const getDaysUntilService = () => {
  if (!vehicle.nextService) return null;

  const today = new Date();
  const serviceDate = new Date(vehicle.nextService);
  const diffTime = serviceDate.getTime() - today.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

const daysUntilService = getDaysUntilService();
  return (
    <div className={`bg-gray-800/30 rounded-2xl p-5 border ${getStatusColor()} hover:border-blue-500/50 transition-all duration-300`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gray-800/50 rounded-lg">
            <Car className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h3 className="font-bold text-white">{vehicle.name}</h3>
            <p className="text-sm text-gray-400">{vehicle.registration}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <button className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Health Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-gray-400">Health Score</span>
          <span className="font-semibold text-white">{vehicle.health}%</span>
        </div>
        <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
          <div 
            className={`h-full ${
              vehicle.health > 80 ? 'bg-linear-to-r from-green-500 to-emerald-500' :
              vehicle.health > 60 ? 'bg-linear-to-r from-yellow-500 to-amber-500' :
              'bg-linear-to-r from-red-500 to-pink-500'
            }`}
            style={{ width: `${vehicle.health}%` }}
          />
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-blue-900/30 rounded-lg">
            <Battery className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <p className="text-xs text-gray-400">Fuel</p>
            <p className="text-sm font-semibold text-white">{vehicle.fuelLevel}%</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-cyan-900/30 rounded-lg">
            <Thermometer className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <p className="text-xs text-gray-400">Mileage</p>
            <p className="text-sm font-semibold text-white">
              {vehicle.mileage.toLocaleString()} km
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-purple-900/30 rounded-lg">
            <Zap className="w-4 h-4 text-purple-400" />
          </div>
          <div>
            <p className="text-xs text-gray-400">Last Service</p>
            <p className="text-sm font-semibold text-white">
  {vehicle.lastService ? formatDate(vehicle.lastService) : "—"}
</p>

          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {daysUntilService !== null && (
  <>
    <div className={`p-1.5 rounded-lg ${
      daysUntilService <= 7 ? 'bg-red-900/30' : 'bg-green-900/30'
    }`}>
      <Calendar className={`w-4 h-4 ${
        daysUntilService <= 7 ? 'text-red-400' : 'text-green-400'
      }`} />
    </div>

    <div>
      <p className="text-xs text-gray-400">Next Service</p>
      <p className={`text-sm font-semibold ${
        daysUntilService <= 7 ? 'text-red-400' : 'text-green-400'
      }`}>
        in {daysUntilService} days
      </p>
    </div>
  </>
)}

        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          onClick={() => router.push(`/dashboard/user/vehicles/${vehicle.id}`)}
          className="flex-1 bg-linear-to-r from-blue-600 to-cyan-600 text-white py-2.5 rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/30 transition-all"
        >
          View Details
        </button>
        
        <button
          onClick={() => router.push(`/dashboard/user/services?vehicle=${vehicle.id}`)}
          className="px-4 py-2.5 bg-gray-800 text-gray-300 rounded-xl font-medium hover:bg-gray-700 transition-colors"
        >
          Service
        </button>
         <button
        onClick={runAI}
        disabled={running}
        className="mt-4 w-full px-4 py-2 rounded-lg
                   bg-blue-600 hover:bg-blue-500
                   disabled:bg-gray-600"
      >
        {running ? "Running AI..." : "Run AI Analysis"}
      </button>
      </div>
    </div>
  );
}