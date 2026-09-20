// API Client for Backend Communication

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiError {
  detail: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;

    // Load token from localStorage if available
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'An error occurred');
    }

    return response.json();
  }

  // Auth endpoints
  async login(username: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async getCurrentUser() {
    return this.request('/api/v1/auth/me');
  }

  async logout() {
    this.clearToken();
  }

  // Case endpoints
  async getCases(params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.status) query.append('status', params.status);

    return this.request(`/api/v1/cases?${query.toString()}`);
  }

  async getCase(caseId: string) {
    return this.request(`/api/v1/cases/${caseId}`);
  }

  async createCase(data: any) {
    return this.request('/api/v1/cases', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCase(caseId: string, data: any) {
    return this.request(`/api/v1/cases/${caseId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async getCaseStats() {
    return this.request('/api/v1/cases/stats/summary');
  }

  // GenAI endpoints
  async summarizeCase(caseId: string) {
    return this.request('/api/v1/genai/summarize', {
      method: 'POST',
      body: JSON.stringify({ case_id: caseId }),
    });
  }

  async generateScript(caseId: string, scenario: string, tone: string = 'professional') {
    return this.request('/api/v1/genai/generate-script', {
      method: 'POST',
      body: JSON.stringify({ case_id: caseId, scenario, tone }),
    });
  }

  async analyzeIntent(transcript: string) {
    return this.request('/api/v1/genai/analyze-intent', {
      method: 'POST',
      body: JSON.stringify({ transcript }),
    });
  }

  async scoreWillingness(caseId: string) {
    return this.request(`/api/v1/genai/score-willingness?case_id=${caseId}`, {
      method: 'POST',
    });
  }

  async checkCompliance(script: string) {
    return this.request(`/api/v1/genai/compliance-check?script=${encodeURIComponent(script)}`, {
      method: 'POST',
    });
  }

  // Rules endpoints
  async getRules(params?: { rule_type?: string; is_active?: boolean }) {
    const query = new URLSearchParams();
    if (params?.rule_type) query.append('rule_type', params.rule_type);
    if (params?.is_active !== undefined) query.append('is_active', params.is_active.toString());

    return this.request(`/api/v1/rules?${query.toString()}`);
  }

  async createRule(data: any) {
    return this.request('/api/v1/rules', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateRule(ruleId: string, data: any) {
    return this.request(`/api/v1/rules/${ruleId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Analytics endpoints
  async getPerformanceMetrics() {
    return this.request('/api/v1/analytics/performance');
  }

  async getComplianceMetrics() {
    return this.request('/api/v1/analytics/compliance-metrics');
  }

  async getABTestResults() {
    return this.request('/api/v1/analytics/ab-test-results');
  }

  async getDashboardStats() {
    return this.request('/api/v1/analytics/dashboard-stats');
  }
}

export const apiClient = new ApiClient(API_URL);
