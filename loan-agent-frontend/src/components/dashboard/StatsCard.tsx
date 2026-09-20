import React from 'react';
import { LucideIcon } from 'lucide-react';
import { Card } from '@/components/ui';

interface StatsCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: LucideIcon;
  color?: string;
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  icon: Icon,
  color = 'capco-blue',
}) => {
  return (
    <Card>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-capco-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-capco-navy">{value}</p>
          {change !== undefined && (
            <p className={`text-sm mt-1 ${change >= 0 ? 'text-capco-green' : 'text-capco-red'}`}>
              {change >= 0 ? '↑' : '↓'} {Math.abs(change)}% from last month
            </p>
          )}
        </div>
        <div className={`p-4 bg-${color}/10 rounded-capco`}>
          <Icon size={32} className={`text-${color}`} />
        </div>
      </div>
    </Card>
  );
};
