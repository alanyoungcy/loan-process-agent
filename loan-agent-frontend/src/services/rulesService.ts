import api from './api';

export interface RuleInfo {
  name: string;
  description: string;
  priority: string;
  enabled: boolean;
  tags: string[];
}

export interface RulesStatistics {
  total_rules: number;
  enabled_rules: number;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
}

export interface EvaluateResponse {
  case_id: string;
  rules_executed: string[];
  actions_taken: string[];
  modifications: Record<string, any>;
  recommendations: string[];
  can_contact: boolean;
  applied: boolean;
}

export const rulesService = {
  async listRules(category?: string): Promise<RuleInfo[]> {
    const response = await api.get('/api/v1/rules/list', {
      params: category ? { category } : {}
    });
    return response.data;
  },

  async getStatistics(): Promise<RulesStatistics> {
    const response = await api.get('/api/v1/rules/statistics');
    return response.data;
  },

  async getCategories(): Promise<{ categories: string[] }> {
    const response = await api.get('/api/v1/rules/categories');
    return response.data;
  },

  async evaluateCase(data: {
    case_id: string;
    additional_facts?: Record<string, any>;
    auto_apply?: boolean;
  }): Promise<EvaluateResponse> {
    const response = await api.post('/api/v1/rules/evaluate', data);
    return response.data;
  },

  async enableRule(ruleName: string): Promise<{ message: string }> {
    const response = await api.post(`/api/v1/rules/enable/${ruleName}`);
    return response.data;
  },

  async disableRule(ruleName: string): Promise<{ message: string }> {
    const response = await api.post(`/api/v1/rules/disable/${ruleName}`);
    return response.data;
  },
};
