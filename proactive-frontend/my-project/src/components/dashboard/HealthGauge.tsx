'use client';

interface HealthGaugeProps {
  title: string;
  value?: number; // allow undefined safely
  type: 'health' | 'risk' | 'probability';
  size?: 'sm' | 'md' | 'lg';
}

export default function HealthGauge({
  title,
  value,
  type,
  size = 'md',
}: HealthGaugeProps) {
  // ✅ SAFE VALUE (single source of truth)
  const safeValue = Number.isFinite(value) ? value! : 0;

  const getColor = () => {
    if (type === 'risk' || type === 'probability') {
      if (safeValue < 30) return 'text-green-500';
      if (safeValue < 70) return 'text-yellow-500';
      return 'text-red-500';
    } else {
      if (safeValue > 80) return 'text-green-500';
      if (safeValue > 60) return 'text-yellow-500';
      return 'text-red-500';
    }
  };

  const getStrokeColor = () => {
    if (type === 'risk' || type === 'probability') {
      if (safeValue < 30) return '#10b981';
      if (safeValue < 70) return '#f59e0b';
      return '#ef4444';
    } else {
      if (safeValue > 80) return '#10b981';
      if (safeValue > 60) return '#f59e0b';
      return '#ef4444';
    }
  };

  const getBackgroundColor = () => {
    if (type === 'risk' || type === 'probability') {
      if (safeValue < 30) return 'bg-green-500/10';
      if (safeValue < 70) return 'bg-yellow-500/10';
      return 'bg-red-500/10';
    } else {
      if (safeValue > 80) return 'bg-green-500/10';
      if (safeValue > 60) return 'bg-yellow-500/10';
      return 'bg-red-500/10';
    }
  };

  const getSizes = () => {
    switch (size) {
      case 'sm':
        return { svg: 80, text: 'text-lg', title: 'text-sm' };
      case 'lg':
        return { svg: 120, text: 'text-2xl', title: 'text-base' };
      default:
        return { svg: 100, text: 'text-xl', title: 'text-sm' };
    }
  };

  const sizes = getSizes();
  const radius = 40;
  const circumference = 2 * Math.PI * radius;

  return (
    <div
      className={`p-4 rounded-2xl ${getBackgroundColor()} border border-gray-800/50`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className={`text-gray-400 ${sizes.title} mb-1`}>{title}</p>

          {/* ✅ SAFE toFixed */}
          <div className={`font-bold ${getColor()} ${sizes.text}`}>
            {safeValue.toFixed(1)}%
          </div>

          <p className="text-xs text-gray-500 mt-1">
            {type === 'probability'
              ? 'Failure chance'
              : type === 'risk'
              ? 'Risk level'
              : 'Health score'}
          </p>
        </div>

        <div
          className="relative"
          style={{ width: sizes.svg, height: sizes.svg }}
        >
          <svg className="w-full h-full" viewBox="0 0 100 100">
            {/* Background */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke="#1f2937"
              strokeWidth="8"
            />

            {/* Progress */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke={getStrokeColor()}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={`${circumference - (safeValue / 100) * circumference}`}
              transform="rotate(-90 50 50)"
            />
          </svg>

          {/* Center text */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              className={`font-bold ${getColor()} ${
                size === 'sm'
                  ? 'text-2xl'
                  : size === 'lg'
                  ? 'text-3xl'
                  : 'text-2xl'
              }`}
            >
              {Math.round(safeValue)}%
            </div>
          </div>
        </div>
      </div>

      {/* Status */}
      <div className="flex items-center gap-2 mt-4">
        <div
          className={`w-2 h-2 rounded-full ${getColor().replace(
            'text-',
            'bg-'
          )}`}
        />
        <span className="text-sm text-gray-400">
          {type === 'probability'
            ? 'Probability of failure'
            : type === 'risk'
            ? 'Overall risk assessment'
            : 'Current health status'}
        </span>
      </div>
    </div>
  );
}
