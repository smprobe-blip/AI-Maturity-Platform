import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/utils/cn';

interface KpiCardProps {
  title: string;
  value: string | number;
  delta?: number;
  deltaLabel?: string;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
}

export function KpiCard({
  title,
  value,
  delta,
  deltaLabel,
  icon,
  trend = 'neutral',
}: KpiCardProps) {
  const trendColors = {
    up: 'text-green-600 bg-green-50',
    down: 'text-red-600 bg-red-50',
    neutral: 'text-gray-600 bg-gray-50',
  };

  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;

  return (
    <div className="card hover:shadow-xl transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="p-2 bg-primary-50 rounded-lg">
          {icon || <div className="w-5 h-5 text-primary-600" />}
        </div>
        {delta !== undefined && (
          <div
            className={cn(
              'flex items-center gap-1 px-2 py-1 rounded-md text-xs font-semibold',
              trendColors[trend]
            )}
          >
            <TrendIcon className="w-3 h-3" />
            {delta > 0 ? '+' : ''}
            {delta}%
          </div>
        )}
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-sm text-gray-600">{title}</div>
      {deltaLabel && (
        <div className="text-xs text-gray-500 mt-1">{deltaLabel}</div>
      )}
    </div>
  );
}