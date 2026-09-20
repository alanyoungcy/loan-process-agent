import React from 'react';
import { clsx } from 'clsx';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'primary',
  className,
}) => {
  const variantStyles = {
    primary: 'badge-primary',
    success: 'badge-success',
    warning: 'badge-warning',
    danger: 'badge-danger',
    info: 'badge-info',
  };

  return (
    <span className={clsx('badge', variantStyles[variant], className)}>
      {children}
    </span>
  );
};

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const getVariant = (status: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' => {
    const statusMap: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
      new: 'info',
      in_progress: 'warning',
      contacted: 'primary',
      promised_to_pay: 'success',
      payment_plan: 'success',
      dispute: 'danger',
      legal: 'danger',
      closed: 'success',
      written_off: 'danger',
    };
    return statusMap[status] || 'primary';
  };

  const formatStatus = (status: string): string => {
    return status
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <Badge variant={getVariant(status)} className={className}>
      {formatStatus(status)}
    </Badge>
  );
};

interface PriorityBadgeProps {
  priority: number;
  className?: string;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ priority, className }) => {
  const getVariant = (priority: number): 'primary' | 'success' | 'warning' | 'danger' | 'info' => {
    if (priority >= 8) return 'danger';
    if (priority >= 6) return 'warning';
    if (priority >= 4) return 'info';
    return 'success';
  };

  return (
    <Badge variant={getVariant(priority)} className={className}>
      Priority {priority}
    </Badge>
  );
};
