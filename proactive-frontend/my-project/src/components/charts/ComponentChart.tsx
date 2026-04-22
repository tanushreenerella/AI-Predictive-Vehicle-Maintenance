'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const componentData = [
  { component: 'Engine', health: 92, risk: 8, failures: 2 },
  { component: 'Brakes', health: 78, risk: 22, failures: 5 },
  { component: 'Battery', health: 85, risk: 15, failures: 3 },
  { component: 'Transmission', health: 88, risk: 12, failures: 1 },
  { component: 'Cooling', health: 72, risk: 28, failures: 4 },
  { component: 'Electrical', health: 91, risk: 9, failures: 1 },
];

export default function ComponentChart() {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900 border border-gray-800 p-3 rounded-lg shadow-xl">
          <p className="font-semibold text-white mb-2">{label}</p>
          <div className="space-y-1">
            <div className="flex items-center justify-between gap-4">
              <span className="text-gray-300">Health:</span>
              <span className="font-medium text-white">{payload[0].value}%</span>
            </div>
            <div className="flex items-center justify-between gap-4">
              <span className="text-gray-300">Risk:</span>
              <span className="font-medium text-white">{payload[1].value}%</span>
            </div>
            <div className="flex items-center justify-between gap-4">
              <span className="text-gray-300">Failures:</span>
              <span className="font-medium text-white">{payload[2].value}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  const getHealthColor = (value: number) => {
    if (value >= 80) return '#10b981'; // green
    if (value >= 60) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  const getRiskColor = (value: number) => {
    if (value <= 15) return '#10b981'; // green
    if (value <= 25) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={componentData}
        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        barSize={35}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
        
        <XAxis 
          dataKey="component" 
          stroke="#6b7280"
          tick={{ fill: '#9ca3af', fontSize: 12 }}
          angle={-45}
          textAnchor="end"
          height={60}
        />
        
        <YAxis 
          stroke="#6b7280"
          tick={{ fill: '#9ca3af' }}
          label={{ 
            value: 'Percentage (%)', 
            angle: -90, 
            position: 'insideLeft',
            style: { fill: '#9ca3af' }
          }}
        />
        
        <Tooltip content={<CustomTooltip />} />
        
        <Legend 
          wrapperStyle={{ paddingTop: '10px' }}
          formatter={(value) => (
            <span className="text-gray-300 text-sm">{value}</span>
          )}
        />
        
        <Bar 
          dataKey="health" 
          name="Health Score"
          radius={[4, 4, 0, 0]}
        >
          {componentData.map((entry, index) => (
            <Cell key={`health-${index}`} fill={getHealthColor(entry.health)} />
          ))}
        </Bar>
        
        <Bar 
          dataKey="risk" 
          name="Risk Level"
          radius={[4, 4, 0, 0]}
        >
          {componentData.map((entry, index) => (
            <Cell key={`risk-${index}`} fill={getRiskColor(entry.risk)} />
          ))}
        </Bar>
        
        <Bar 
          dataKey="failures" 
          name="Past Failures"
          radius={[4, 4, 0, 0]}
          fill="#8b5cf6"
        />
      </BarChart>
    </ResponsiveContainer>
  );
}