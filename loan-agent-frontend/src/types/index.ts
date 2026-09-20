// User types
export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'supervisor' | 'collector';
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Case types
export interface Case {
  id: string;
  case_id: string;
  customer_id: string;
  loan_id: string;
  loan_product: string;
  principal_amount: number;
  overdue_amount: number;
  overdue_days: number;
  overdue_date?: string;
  status: CaseStatus;
  priority: number;
  contact_count: number;
  last_contact_date?: string;
  next_action_date?: string;
  assigned_to?: string;
  dispute_flag: boolean;
  legal_flag: boolean;
  tags?: string[];
  notes?: string;
  created_at: string;
  updated_at: string;
}

export type CaseStatus = 
  | 'new'
  | 'in_progress'
  | 'contacted'
  | 'promised_to_pay'
  | 'payment_plan'
  | 'dispute'
  | 'legal'
  | 'closed'
  | 'written_off';

// Customer types
export interface Customer {
  id: string;
  customer_id: string;
  name: string;
  phone: string;
  email: string;
  id_number: string;
  address?: string;
  credit_score?: number;
  risk_category?: string;
  created_at: string;
  updated_at: string;
}

// GenAI types
export interface SummarizeRequest {
  case_id: string;
}

export interface SummarizeResponse {
  summary: string;
  confidence: number;
  processing_time_ms: number;
}

export interface GenerateScriptRequest {
  case_id: string;
  scenario: ScriptScenario;
  tone: ScriptTone;
  custom_instructions?: string;
}

export type ScriptScenario = 
  | 'first_contact'
  | 'follow_up'
  | 'payment_reminder'
  | 'broken_promise'
  | 'dispute_resolution'
  | 'payment_plan_discussion';

export type ScriptTone = 
  | 'professional'
  | 'empathetic'
  | 'firm'
  | 'friendly';

export interface GenerateScriptResponse {
  script: string;
  compliance_status: string;
  forbidden_phrases_found: string[];
  suggestions: string[];
  processing_time_ms: number;
}

export interface AnalyzeIntentRequest {
  transcript: string;
  case_id?: string;
}

export interface AnalyzeIntentResponse {
  intent: CustomerIntent;
  sentiment: Sentiment;
  willingness_to_pay_score: number;
  key_points: string[];
  recommended_actions: string[];
  processing_time_ms: number;
}

export type CustomerIntent = 
  | 'willing_to_pay'
  | 'requesting_time'
  | 'disputing_debt'
  | 'financial_hardship'
  | 'threatening'
  | 'avoiding'
  | 'unclear';

export type Sentiment = 'positive' | 'neutral' | 'negative';

export interface ScoreWillingnessRequest {
  case_id: string;
  conversation_history?: string[];
}

export interface ScoreWillingnessResponse {
  score: number;
  confidence: number;
  factors: {
    factor: string;
    impact: number;
    explanation: string;
  }[];
  recommendation: string;
  processing_time_ms: number;
}

// Audit types
export interface GenAIAudit {
  id: string;
  case_id?: string;
  service_type: string;
  model_used: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  confidence?: number;
  processing_time_ms: number;
  user_id?: string;
  created_at: string;
}

// Analytics types
export interface DashboardStats {
  total_cases: number;
  active_cases: number;
  resolved_today: number;
  total_overdue_amount: number;
  avg_resolution_time: number;
  collection_rate: number;
  cases_by_status: Record<CaseStatus, number>;
  cases_by_priority: Record<number, number>;
}

export interface PerformanceMetrics {
  collector_id: string;
  collector_name: string;
  cases_assigned: number;
  cases_resolved: number;
  amount_collected: number;
  avg_resolution_time: number;
  success_rate: number;
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  status?: number;
}
