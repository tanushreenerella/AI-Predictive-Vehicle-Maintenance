'use client';

import { AlertTriangle, Info, CheckCircle, X, Bell, ExternalLink,Car } from 'lucide-react';
import { useState } from 'react';

interface AlertCardProps {
  alert: {
    id: number;
    type: 'warning' | 'info' | 'success' | 'critical';
    title: string;
    message: string;
    time: string;
    vehicle: string;
    priority?: 'low' | 'medium' | 'high';
    actionRequired?: boolean;
  };
}

export default function AlertCard({ alert }: AlertCardProps) {
  const [dismissed, setDismissed] = useState(false);

  const getAlertConfig = () => {
    switch (alert.type) {
      case 'warning':
        return {
          icon: <AlertTriangle className="w-5 h-5" />,
          bgColor: 'bg-yellow-500/10',
          borderColor: 'border-yellow-500/30',
          textColor: 'text-yellow-400',
          iconBg: 'bg-yellow-500/20',
        };
      case 'critical':
        return {
          icon: <AlertTriangle className="w-5 h-5" />,
          bgColor: 'bg-red-500/10',
          borderColor: 'border-red-500/30',
          textColor: 'text-red-400',
          iconBg: 'bg-red-500/20',
        };
      case 'success':
        return {
          icon: <CheckCircle className="w-5 h-5" />,
          bgColor: 'bg-green-500/10',
          borderColor: 'border-green-500/30',
          textColor: 'text-green-400',
          iconBg: 'bg-green-500/20',
        };
      case 'info':
      default:
        return {
          icon: <Info className="w-5 h-5" />,
          bgColor: 'bg-blue-500/10',
          borderColor: 'border-blue-500/30',
          textColor: 'text-blue-400',
          iconBg: 'bg-blue-500/20',
        };
    }
  };

  const getPriorityColor = () => {
    switch (alert.priority) {
      case 'high': return 'bg-red-500/20 text-red-400';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400';
      case 'low': return 'bg-green-500/20 text-green-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const config = getAlertConfig();

  if (dismissed) return null;

  return (
    <div className={`p-4 rounded-xl border ${config.borderColor} ${config.bgColor} transition-all duration-300 hover:scale-[1.02]`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1">
          <div className={`p-2 rounded-lg ${config.iconBg}`}>
            {config.icon}
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3 className={`font-semibold ${config.textColor}`}>{alert.title}</h3>
              
              {alert.priority && (
                <span className={`px-2 py-0.5 text-xs rounded-full ${getPriorityColor()}`}>
                  {alert.priority.toUpperCase()}
                </span>
              )}
              
              {alert.actionRequired && (
                <span className="px-2 py-0.5 text-xs bg-red-500/20 text-red-400 rounded-full flex items-center gap-1">
                  <Bell className="w-3 h-3" />
                  Action Required
                </span>
              )}
            </div>
            
            <p className="text-sm text-gray-300 mb-2">{alert.message}</p>
            
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <Car className="w-3 h-3" />
                {alert.vehicle}
              </span>
              <span>•</span>
              <span>{alert.time}</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-start gap-2 ml-2">
          <button className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800/50 rounded-lg transition-colors">
            <ExternalLink className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => setDismissed(true)}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800/50 rounded-lg transition-colors"
            title="Dismiss alert"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Action buttons for critical alerts */}
      {alert.actionRequired && (
        <div className="mt-4 pt-4 border-t border-gray-800/50">
          <div className="flex gap-3">
            <button className="px-4 py-2 bg-linear-to-br from-blue-600 to-cyan-600 text-white rounded-lg font-medium hover:shadow-lg hover:shadow-blue-500/30 transition-all">
              Schedule Inspection
            </button>
            <button className="px-4 py-2 bg-gray-800 text-gray-300 rounded-lg font-medium hover:bg-gray-700 transition-colors">
              View Details
            </button>
            <button className="px-4 py-2 bg-gray-800 text-gray-300 rounded-lg font-medium hover:bg-gray-700 transition-colors">
              Contact Support
            </button>
          </div>
        </div>
      )}
    </div>
  );
}