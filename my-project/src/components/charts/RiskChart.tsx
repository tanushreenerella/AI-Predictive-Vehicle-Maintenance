'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';

const riskData = [
  { day: 'Mon', risk: 65, prediction: 68, threshold: 70 },
  { day: 'Tue', risk: 70, prediction: 72, threshold: 70 },
  { day: 'Wed', risk: 72, prediction: 75, threshold: 70 },
  { day: 'Thu', risk: 68, prediction: 71, threshold: 70 },
  { day: 'Fri', risk: 75, prediction: 78, threshold: 70 },
  { day: 'Sat', risk: 78, prediction: 81, threshold: 70 },
  { day: 'Sun', risk: 72, prediction: 74, threshold: 70 },
];

const componentData = [
  { component: 'Engine', health: 92, risk: 8, failures: 2 },
  { component: 'Brakes', health: 78, risk: 22, failures: 5 },
  { component: 'Battery', health: 85, risk: 15, failures: 3 },
  { component: 'Transmission', health: 88, risk: 12, failures: 1 },
  { component: 'Cooling', health: 72, risk: 28, failures: 4 },
  { component: 'Electrical', health: 91, risk: 9, failures: 1 },
];

export default function RiskChart() {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900 border border-gray-800 p-3 rounded-lg shadow-xl">
          <p className="font-semibold text-white">{label}</p>
          <div className="space-y-1 mt-2">
            {payload.map((entry: any, index: number) => (
              <div key={index} className="flex items-center gap-2 text-sm">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-gray-300">{entry.dataKey}: </span>
                <span className="font-medium text-white">{entry.value}%</span>
              </div>
            ))}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={riskData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="colorPrediction" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
          </linearGradient>
        </defs>
        
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
        
        <XAxis 
          dataKey="day" 
          stroke="#6b7280"
          tick={{ fill: '#9ca3af' }}
        />
        
        <YAxis 
          stroke="#6b7280"
          tick={{ fill: '#9ca3af' }}
          label={{ 
            value: 'Risk Level (%)', 
            angle: -90, 
            position: 'insideLeft',
            style: { fill: '#9ca3af' }
          }}
        />
        
        <Tooltip content={<CustomTooltip />} />
        
        <Legend 
          wrapperStyle={{ paddingTop: '20px' }}
          formatter={(value) => (
            <span className="text-gray-300 text-sm">{value}</span>
          )}
        />
        
        <Area
          type="monotone"
          dataKey="threshold"
          stroke="#f59e0b"
          strokeWidth={2}
          strokeDasharray="5 5"
          fill="none"
          name="Safety Threshold"
        />
        
        <Area
          type="monotone"
          dataKey="risk"
          stroke="#ef4444"
          strokeWidth={2}
          fill="url(#colorRisk)"
          name="Current Risk"
        />
        
        <Area
          type="monotone"
          dataKey="prediction"
          stroke="#3b82f6"
          strokeWidth={2}
          fill="url(#colorPrediction)"
          name="Predicted Risk"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}