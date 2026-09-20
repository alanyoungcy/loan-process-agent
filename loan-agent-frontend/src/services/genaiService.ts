import api from './api';
import type {
  SummarizeRequest,
  SummarizeResponse,
  GenerateScriptRequest,
  GenerateScriptResponse,
  AnalyzeIntentRequest,
  AnalyzeIntentResponse,
  ScoreWillingnessRequest,
  ScoreWillingnessResponse,
} from '@/types';

export const genaiService = {
  async summarizeCase(request: SummarizeRequest): Promise<SummarizeResponse> {
    const { data } = await api.post<SummarizeResponse>(
      '/api/v1/genai/summarize',
      request
    );
    return data;
  },

  async generateScript(request: GenerateScriptRequest): Promise<GenerateScriptResponse> {
    const { data } = await api.post<GenerateScriptResponse>(
      '/api/v1/genai/generate-script',
      request
    );
    return data;
  },

  async analyzeIntent(request: AnalyzeIntentRequest): Promise<AnalyzeIntentResponse> {
    const { data } = await api.post<AnalyzeIntentResponse>(
      '/api/v1/genai/analyze-intent',
      request
    );
    return data;
  },

  async scoreWillingness(request: ScoreWillingnessRequest): Promise<ScoreWillingnessResponse> {
    const { data } = await api.post<ScoreWillingnessResponse>(
      '/api/v1/genai/score-willingness',
      request
    );
    return data;
  },

  async complianceCheck(text: string): Promise<{
    compliant: boolean;
    forbidden_phrases: string[];
    suggestions: string[];
  }> {
    const { data } = await api.post('/api/v1/genai/compliance-check', { text });
    return data;
  },
};
