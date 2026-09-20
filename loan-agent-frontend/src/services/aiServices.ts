import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Chatbot Service
export const chatbotService = {
  async createSession(caseId?: string) {
    const response = await apiClient.post('/chatbot/session', { case_id: caseId });
    return response.data;
  },

  async sendMessage(sessionId: string, message: string, caseId?: string) {
    const response = await apiClient.post('/chatbot/message', {
      session_id: sessionId,
      message,
      case_id: caseId,
    });
    return response.data;
  },

  async getConversationSummary(sessionId: string) {
    const response = await apiClient.get(`/chatbot/session/${sessionId}/summary`);
    return response.data;
  },

  async endSession(sessionId: string) {
    const response = await apiClient.post(`/chatbot/session/${sessionId}/end`);
    return response.data;
  },

  async takeoverSession(sessionId: string, agentId: string) {
    const response = await apiClient.post(`/chatbot/session/${sessionId}/takeover`, {
      agent_id: agentId,
    });
    return response.data;
  },
};

// Multi-Agent Debate Service
export const multiAgentService = {
  async runDebate(caseId: string, context?: any, debateRounds: number = 2) {
    const response = await apiClient.post('/multi-agent/debate', {
      case_id: caseId,
      context,
      debate_rounds: debateRounds,
    });
    return response.data;
  },

  async getDebateHistory(caseId: string) {
    const response = await apiClient.get(`/multi-agent/debates/${caseId}`);
    return response.data;
  },

  async acceptConsensus(caseId: string, debateId: string) {
    const response = await apiClient.post(`/multi-agent/debates/${debateId}/accept`, {
      case_id: caseId,
    });
    return response.data;
  },
};

// Trust Gate Service
export const trustGateService = {
  async evaluateAction(genaiOutput: any, context?: any) {
    const response = await apiClient.post('/trust-gate/evaluate', {
      genai_output: genaiOutput,
      context,
    });
    return response.data;
  },

  async getEvaluationHistory(caseId: string) {
    const response = await apiClient.get(`/trust-gate/history/${caseId}`);
    return response.data;
  },

  async overrideDecision(evaluationId: string, reason: string) {
    const response = await apiClient.post(`/trust-gate/${evaluationId}/override`, {
      reason,
    });
    return response.data;
  },
};

// A/B Testing Service
export const abTestingService = {
  async createExperiment(data: {
    name: string;
    description: string;
    hypothesis: string;
    control_description: string;
    treatment_description: string;
    target_metric: string;
    target_sample_size: number;
    start_date: string;
    end_date?: string;
  }) {
    const response = await apiClient.post('/experiments', data);
    return response.data;
  },

  async listExperiments(status?: 'active' | 'completed' | 'all') {
    const response = await apiClient.get('/experiments', {
      params: { status },
    });
    return response.data;
  },

  async getExperiment(name: string) {
    const response = await apiClient.get(`/experiments/${name}`);
    return response.data;
  },

  async getExperimentResults(name: string) {
    const response = await apiClient.get(`/experiments/${name}/results`);
    return response.data;
  },

  async stopExperiment(name: string, reason?: string) {
    const response = await apiClient.post(`/experiments/${name}/stop`, { reason });
    return response.data;
  },

  async promoteWinner(name: string) {
    const response = await apiClient.post(`/experiments/${name}/promote`);
    return response.data;
  },

  async assignVariant(experimentName: string, caseId: string) {
    const response = await apiClient.post(`/experiments/${experimentName}/assign`, {
      case_id: caseId,
    });
    return response.data;
  },

  async trackOutcome(experimentName: string, caseId: string, outcomeData: any, success: boolean) {
    const response = await apiClient.post(`/experiments/${experimentName}/outcome`, {
      case_id: caseId,
      outcome_data: outcomeData,
      success,
    });
    return response.data;
  },
};

// AI Metrics Service
export const aiMetricsService = {
  async getOverviewMetrics() {
    const response = await apiClient.get('/ai/metrics');
    return response.data;
  },

  async getActiveSessions() {
    const response = await apiClient.get('/ai/active-sessions');
    return response.data;
  },

  async getPerformanceTrends(days: number = 7) {
    const response = await apiClient.get('/ai/performance-trends', {
      params: { days },
    });
    return response.data;
  },

  async getAccuracyMetrics() {
    const response = await apiClient.get('/ai/accuracy');
    return response.data;
  },
};

// GenAI Service (existing, extended)
export const genaiService = {
  async generateScript(caseData: any, channel: 'email' | 'sms' | 'call', context?: any) {
    const response = await apiClient.post('/genai/generate-script', {
      case_data: caseData,
      channel,
      context,
    });
    return response.data;
  },

  async analyzeIntent(message: string) {
    const response = await apiClient.post('/genai/analyze-intent', {
      message,
    });
    return response.data;
  },

  async summarizeCase(caseId: string) {
    const response = await apiClient.post('/genai/summarize', {
      case_id: caseId,
    });
    return response.data;
  },

  async checkCompliance(content: string, context: any) {
    const response = await apiClient.post('/genai/check-compliance', {
      content,
      context,
    });
    return response.data;
  },
};

export default {
  chatbot: chatbotService,
  multiAgent: multiAgentService,
  trustGate: trustGateService,
  abTesting: abTestingService,
  aiMetrics: aiMetricsService,
  genai: genaiService,
};
