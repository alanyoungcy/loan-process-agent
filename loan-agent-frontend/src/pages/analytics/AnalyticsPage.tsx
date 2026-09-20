import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { BarChart3, TrendingUp, Users, DollarSign, Calendar, Download, AlertCircle } from 'lucide-react';
import { analyticsService } from '../../services/analyticsService';

export const AnalyticsPage: React.FC = () => {
  const [dateRange, setDateRange] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [stats, setStats] = useState({
    totalCases: 0,
    totalRecovered: 0,
    avgRecoveryTime: 0,
    successRate: 0,
  });

  const [collectionsByStatus, setCollectionsByStatus] = useState<Array<{status: string, count: number, percentage: number}>>([]);
  const [topCollectors, setTopCollectors] = useState<Array<{name: string, cases: number, recovered: number, rate: number}>>([]);
  const [monthlyTrends, setMonthlyTrends] = useState<Array<{month: string, cases: number, recovered: number}>>([]);
  const [insights, setInsights] = useState({
    bestPerformingTime: 'N/A',
    avgContactAttempts: 0,
    paymentPlanAdoption: 0,
  });

  useEffect(() => {
    loadAnalytics();
  }, [dateRange]);

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const dashboard = await analyticsService.getDashboard(dateRange);
      setStats(dashboard.stats);
      setCollectionsByStatus(dashboard.collectionsByStatus);
      setTopCollectors(dashboard.topCollectors);
      setMonthlyTrends(dashboard.monthlyTrends);
      setInsights(dashboard.insights);
    } catch (err) {
      console.error('Failed to load analytics:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const blob = await analyticsService.exportReport(dateRange, 'csv');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-report-${dateRange}-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Export failed:', err);
      alert('Failed to export report');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-1">Real-time performance insights and trends</p>
        </div>
        <div className="flex gap-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <Button variant="secondary" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <Card className="bg-red-50 border-red-200">
          <div className="flex items-center gap-3 p-4">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <div>
              <p className="text-red-900 font-semibold">Error Loading Analytics</p>
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          </div>
        </Card>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Cases</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.totalCases}</p>
              <p className="text-sm text-green-600 mt-2">↑ 12% from last period</p>
            </div>
            <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Recovered</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                ${(stats.totalRecovered / 1000000).toFixed(2)}M
              </p>
              <p className="text-sm text-green-600 mt-2">↑ 8% from last period</p>
            </div>
            <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
              <DollarSign className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Recovery Time</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.avgRecoveryTime} days</p>
              <p className="text-sm text-green-600 mt-2">↓ 3 days improvement</p>
            </div>
            <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Success Rate</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.successRate}%</p>
              <p className="text-sm text-green-600 mt-2">↑ 5% from last period</p>
            </div>
            <div className="h-12 w-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Collections by Status */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Collections by Status</h3>
          <div className="space-y-4">
            {collectionsByStatus.map((item) => (
              <div key={item.status}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">{item.status}</span>
                  <span className="font-medium text-gray-900">{item.count} ({item.percentage}%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${item.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Monthly Trends */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Trends</h3>
          <div className="space-y-3">
            {monthlyTrends.map((item) => (
              <div key={item.month} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 w-12">{item.month}</span>
                <div className="flex-1 mx-4">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${(item.cases / 312) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-16 text-right">
                      {item.cases}
                    </span>
                  </div>
                </div>
                <span className="text-sm text-gray-600 w-24 text-right">
                  ${(item.recovered / 1000).toFixed(0)}K
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Top Collectors */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Users className="h-5 w-5 mr-2" />
          Top Performing Collectors
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Collector</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Cases Handled</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Amount Recovered</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Success Rate</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Performance</th>
              </tr>
            </thead>
            <tbody>
              {topCollectors.map((collector, index) => (
                <tr key={collector.name} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <div className="flex items-center">
                      <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                        <span className="text-sm font-medium text-blue-600">#{index + 1}</span>
                      </div>
                      <span className="font-medium text-gray-900">{collector.name}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-gray-600">{collector.cases}</td>
                  <td className="py-3 px-4 text-gray-600">
                    ${(collector.recovered / 1000).toFixed(0)}K
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant={collector.rate >= 70 ? 'success' : collector.rate >= 60 ? 'warning' : 'default'}>
                      {collector.rate}%
                    </Badge>
                  </td>
                  <td className="py-3 px-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          collector.rate >= 70 ? 'bg-green-500' :
                          collector.rate >= 60 ? 'bg-yellow-500' :
                          'bg-gray-400'
                        }`}
                        style={{ width: `${collector.rate}%` }}
                      />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Additional Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Best Performing Time</h3>
          <p className="text-2xl font-bold text-gray-900">{insights.bestPerformingTime}</p>
          <p className="text-sm text-gray-600 mt-1">Highest contact success rate</p>
        </Card>

        <Card className="p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Avg Contact Attempts</h3>
          <p className="text-2xl font-bold text-gray-900">{insights.avgContactAttempts.toFixed(1)}</p>
          <p className="text-sm text-gray-600 mt-1">Before successful resolution</p>
        </Card>

        <Card className="p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Payment Plan Adoption</h3>
          <p className="text-2xl font-bold text-gray-900">{(insights.paymentPlanAdoption * 100).toFixed(0)}%</p>
          <p className="text-sm text-gray-600 mt-1">Of resolved cases</p>
        </Card>
      </div>
    </div>
  );
};