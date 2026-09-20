import api from './api';

export interface AnalyticsStats {
  totalCases: number;
  totalRecovered: number;
  avgRecoveryTime: number;
  successRate: number;
}

export interface CollectionsByStatus {
  status: string;
  count: number;
  percentage: number;
}

export interface TopCollector {
  name: string;
  cases: number;
  recovered: number;
  rate: number;
}

export interface MonthlyTrend {
  month: string;
  cases: number;
  recovered: number;
}

export interface AnalyticsDashboard {
  stats: AnalyticsStats;
  collectionsByStatus: CollectionsByStatus[];
  topCollectors: TopCollector[];
  monthlyTrends: MonthlyTrend[];
  insights: {
    bestPerformingTime: string;
    avgContactAttempts: number;
    paymentPlanAdoption: number;
  };
}

export const analyticsService = {
  async getDashboard(dateRange: string = '30d'): Promise<AnalyticsDashboard> {
    const response = await api.get('/api/v1/analytics/dashboard', {
      params: { date_range: dateRange }
    });
    return response.data;
  },

  async getPerformanceMetrics(dateRange: string = '30d'): Promise<any> {
    const response = await api.get('/api/v1/analytics/performance', {
      params: { date_range: dateRange }
    });
    return response.data;
  },

  async getComplianceMetrics(): Promise<any> {
    const response = await api.get('/api/v1/analytics/compliance-metrics');
    return response.data;
  },

  async getABTestResults(): Promise<any> {
    const response = await api.get('/api/v1/analytics/ab-test-results');
    return response.data;
  },

  async exportReport(dateRange: string, format: 'csv' | 'pdf' = 'csv'): Promise<Blob> {
    const response = await api.get('/api/v1/analytics/export', {
      params: { date_range: dateRange, format },
      responseType: 'blob'
    });
    return response.data;
  },
};
