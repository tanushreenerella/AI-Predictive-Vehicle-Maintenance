'use client';

import { Car, AlertTriangle, CheckCircle, Battery, Thermometer, Zap, Calendar } from 'lucide-react';
import { useRouter } from 'next/navigation';

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

export default function VehicleCard({ vehicle }: VehicleCardProps) {
  const router = useRouter();

  const getStatusBorderAccent = () => {
    switch (vehicle.status) {
      case 'warning': return 'border-l-4 border-l-yellow-500';
      case 'critical': return 'border-l-4 border-l-red-500';
      default: return '';
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
      year: 'numeric',
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
    <div
      onClick={() => router.push(`/dashboard/user/vehicles/${vehicle.id}`)}
      className={`bg-gray-800/40 rounded-2xl p-5 border border-gray-700/60 hover:border-gray-600 transition-colors cursor-pointer ${getStatusBorderAccent()}`}
    >
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
            className={`h-full rounded-full ${
              vehicle.health > 80 ? 'bg-blue-500' :
              vehicle.health > 60 ? 'bg-yellow-500' :
              'bg-red-500'
            }`}
            style={{ width: `${vehicle.health}%` }}
          />
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-gray-700/60 rounded-lg">
            <Battery className="w-4 h-4 text-gray-400" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Fuel</p>
            <p className="text-sm font-semibold text-white">{vehicle.fuelLevel}%</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-gray-700/60 rounded-lg">
            <Thermometer className="w-4 h-4 text-gray-400" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Mileage</p>
            <p className="text-sm font-semibold text-white">
              {vehicle.mileage.toLocaleString()} km
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-gray-700/60 rounded-lg">
            <Zap className="w-4 h-4 text-gray-400" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Last Service</p>
            <p className="text-sm font-semibold text-white">
              {vehicle.lastService ? formatDate(vehicle.lastService) : '—'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {daysUntilService !== null && (
            <>
              <div className="p-1.5 bg-gray-700/60 rounded-lg">
                <Calendar className={`w-4 h-4 ${daysUntilService <= 7 ? 'text-red-400' : 'text-gray-400'}`} />
              </div>
              <div>
                <p className="text-xs text-gray-500">Next Service</p>
                <p className={`text-sm font-semibold ${daysUntilService <= 7 ? 'text-red-400' : 'text-white'}`}>
                  in {daysUntilService} days
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2" onClick={e => e.stopPropagation()}>
        <button
          onClick={() => router.push(`/dashboard/user/analysis?vehicle_id=${vehicle.id}`)}
          className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-xl text-sm font-medium transition-colors"
        >
          Run Analysis
        </button>
        <button
          onClick={() => router.push(`/dashboard/user/vehicles/${vehicle.id}`)}
          className="flex-1 py-2 bg-gray-700/60 hover:bg-gray-700 text-gray-300 rounded-xl text-sm font-medium transition-colors"
        >
          Details
        </button>
      </div>
    </div>
  );
}
