import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { DollarSign, FileText, Clock, TrendingUp } from 'lucide-react';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { Card, CardTitle, CardContent, LoadingSpinner } from '@/components/ui';
import { caseService } from '@/services/caseService';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { data: cases, isLoading } = useQuery({
    queryKey: ['cases'],
    queryFn: () => caseService.getCases({ limit: 100 }),
  });

  if (isLoading) {
    return <LoadingSpinner size="lg" className="mt-20" />;
  }

  const stats = {
    totalCases: cases?.length || 0,
    activeCases: cases?.filter(c => c.status === 'in_progress').length || 0,
    overdueAmount: cases?.reduce((sum, c) => sum + c.overdue_amount, 0) || 0,
    avgPriority: cases?.length ?
      (cases.reduce((sum, c) => sum + c.priority, 0) / cases.length).toFixed(1) : 0,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-capco-navy mb-2">Dashboard</h1>
        <p className="text-capco-gray-600">Welcome back! Here's your collection overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Cases"
          value={stats.totalCases}
          icon={FileText}
          color="capco-blue"
          change={12}
        />
        <StatsCard
          title="Active Cases"
          value={stats.activeCases}
          icon={Clock}
          color="capco-yellow"
          change={-5}
        />
        <StatsCard
          title="Total Overdue"
          value={`$${stats.overdueAmount.toLocaleString()}`}
          icon={DollarSign}
          color="capco-red"
          change={-8}
        />
        <StatsCard
          title="Avg Priority"
          value={stats.avgPriority}
          icon={TrendingUp}
          color="capco-green"
          change={3}
        />
      </div>

      {/* Recent Cases */}
      <Card>
        <CardTitle>Recent Cases</CardTitle>
        <CardContent>
          <div className="space-y-3">
            {cases?.slice(0, 5).map((caseItem) => (
              <div
                key={caseItem.id}
                onClick={() => navigate(`/cases/${caseItem.id}`)}
                className="flex items-center justify-between p-4 border border-capco-gray-200 rounded-capco hover:bg-capco-gray-50 transition-colors cursor-pointer"
              >
                <div>
                  <p className="font-medium text-capco-navy">{caseItem.case_id}</p>
                  <p className="text-sm text-capco-gray-600">{caseItem.customer_id}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-capco-red">
                    ${caseItem.overdue_amount.toLocaleString()}
                  </p>
                  <p className="text-sm text-capco-gray-600">
                    {caseItem.overdue_days} days overdue
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
