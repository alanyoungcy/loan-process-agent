// Type definitions for the application

export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Case {
  id: string;
  case_id: string;
  customer_id: string;
  loan_id: string;
  loan_product?: string;
  principal_amount?: number;
  overdue_amount?: number;
  overdue_days?: number;
  overdue_date?: string;
  status: string;
  priority: number;
  assigned_to?: string;
  contact_count: number;
  last_contact_date?: string;
  payment_promise?: any;
  dispute_flag: boolean;
  legal_status?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

export interface ContactHistory {
  id: string;
  contact_id: string;
  case_id: string;
  contact_type: string;
  contact_time: string;
  duration_seconds?: number;
  transcript?: string;
  sentiment?: string;
  intent?: string;
  outcome?: string;
  genai_processed: boolean;
  compliance_checked: boolean;
  compliance_violations?: string[];
  created_at: string;
}

export interface Rule {
  id: string;
  rule_id: string;
  name: string;
  description?: string;
  rule_type: string;
  drl_content?: string;
  is_active: boolean;
  priority: number;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface GenAISummary {
  summary: string;
  confidence: number;
  processing_time_ms: number;
}

export interface GenAIScript {
  script: string;
  confidence: number;
  compliance_checked: boolean;
  compliance_issues?: string[];
}

export interface IntentAnalysis {
  intent: string;
  sentiment: string;
  confidence: number;
  key_phrases: string[];
}

export interface PerformanceMetrics {
  total_cases: number;
  active_cases: number;
  resolved_cases: number;
  avg_resolution_time_days: number;
  contact_success_rate: number;
  compliance_rate: number;
  recovery_rate: number;
}

export interface ComplianceMetrics {
  total_violations: number;
  violations_by_type: Record<string, number>;
  violations_by_severity: Record<string, number>;
  resolution_rate: number;
  avg_resolution_time_hours: number;
}

export interface DashboardStats {
  cases: {
    total: number;
    active: number;
    resolved: number;
  };
  financial: {
    total_overdue_amount: number;
    recovered_amount: number;
    recovery_rate: number;
  };
  genai: {
    total_calls: number;
    avg_confidence: number;
    auto_execution_rate: number;
  };
  compliance: {
    violation_count: number;
    compliance_rate: number;
  };
}

export type CaseStatus =
  | 'new'
  | 'assigned'
  | 'in_progress'
  | 'contacted'
  | 'negotiating'
  | 'promise_pending'
  | 'escalated'
  | 'legal_review'
  | 'legal_action'
  | 'resolved'
  | 'write_off';

export type ContactType = 'call' | 'sms' | 'email' | 'whatsapp';

export type RuleType = 'assignment' | 'compliance' | 'strategy';

export type UserRole = 'admin' | 'supervisor' | 'collector' | 'compliance';
