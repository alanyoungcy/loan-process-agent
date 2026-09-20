import api from './api';
import type { Case, PaginatedResponse } from '@/types';

export const caseService = {
  async getCases(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    assigned_to?: string;
    priority_min?: number;
    priority_max?: number;
  }): Promise<Case[]> {
    const { data } = await api.get<Case[]>('/api/v1/cases', { params });
    return data;
  },

  async getCase(id: string): Promise<Case> {
    const { data } = await api.get<Case>(`/api/v1/cases/${id}`);
    return data;
  },

  async createCase(caseData: Partial<Case>): Promise<Case> {
    const { data } = await api.post<Case>('/api/v1/cases', caseData);
    return data;
  },

  async updateCase(id: string, caseData: Partial<Case>): Promise<Case> {
    const { data } = await api.put<Case>(`/api/v1/cases/${id}`, caseData);
    return data;
  },

  async deleteCase(id: string): Promise<void> {
    await api.delete(`/api/v1/cases/${id}`);
  },

  async assignCase(caseId: string, userId: string): Promise<Case> {
    const { data } = await api.patch<Case>(`/api/v1/cases/${caseId}/assign`, {
      user_id: userId,
    });
    return data;
  },

  async updateStatus(caseId: string, status: string): Promise<Case> {
    const { data } = await api.patch<Case>(`/api/v1/cases/${caseId}/status`, {
      status,
    });
    return data;
  },

  async addNote(caseId: string, note: string): Promise<Case> {
    const { data } = await api.post<Case>(`/api/v1/cases/${caseId}/notes`, {
      note,
    });
    return data;
  },
};
