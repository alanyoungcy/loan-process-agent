import api from './api';

export interface WorkflowDefinition {
  key: string;
  name: string;
  description: string;
  version: number;
  enabled: boolean;
  num_tasks: number;
}

export interface WorkflowInstance {
  id: string;
  workflow_key: string;
  status: string;
  business_key: string;
  current_task: string | null;
  created_at: string;
}

export interface WorkflowDiagram {
  workflow_key: string;
  name: string;
  version: number;
  nodes: any[];
  edges: any[];
}

export interface WorkflowStats {
  workflow_key: string;
  name: string;
  total_instances: number;
  active_instances: number;
  completed_instances: number;
  failed_instances: number;
  completed_today: number;
  avg_duration_days: number;
  success_rate: number;
}

export const workflowService = {
  async listDefinitions(): Promise<{ workflows: WorkflowDefinition[] }> {
    const response = await api.get('/api/v1/workflows/definitions');
    return response.data;
  },

  async getDefinition(workflowKey: string): Promise<WorkflowDefinition> {
    const response = await api.get(`/api/v1/workflows/definitions/${workflowKey}`);
    return response.data;
  },

  async startWorkflow(request: { workflow_key: string; business_key: string; variables?: Record<string, any> }): Promise<WorkflowInstance> {
    const response = await api.post('/api/v1/workflows/start', request);
    return response.data;
  },

  async getInstance(instanceId: string): Promise<WorkflowInstance> {
    const response = await api.get(`/api/v1/workflows/instances/${instanceId}`);
    return response.data;
  },

  async getActiveInstances(workflowKey: string): Promise<WorkflowInstance[]> {
    const response = await api.get(`/api/v1/workflows/instances/active/${workflowKey}`);
    return response.data;
  },

  async completeTask(instanceId: string, taskId: string, variables: Record<string, any> = {}): Promise<any> {
    const response = await api.post(`/api/v1/workflows/instances/${instanceId}/tasks/${taskId}/complete`, { variables });
    return response.data;
  },

  async getWorkflowDiagram(workflowKey: string): Promise<WorkflowDiagram> {
    const response = await api.get(`/api/v1/workflows/diagram/${workflowKey}`);
    return response.data;
  },

  async getWorkflowStats(workflowKey?: string): Promise<WorkflowStats[]> {
    const url = workflowKey
      ? `/api/v1/workflows/stats/${workflowKey}`
      : '/api/v1/workflows/stats';
    const response = await api.get(url);
    return response.data;
  },

  // BPMN/DMN Designer methods
  async createWorkflow(name: string, type: 'bpmn' | 'dmn'): Promise<any> {
    const response = await api.post('/api/v1/workflows/create', { name, type });
    return response.data;
  },

  async saveWorkflow(id: string, xml: string): Promise<any> {
    const response = await api.put(`/api/v1/workflows/${id}`, { xml });
    return response.data;
  },

  async getWorkflow(id: string): Promise<any> {
    const response = await api.get(`/api/v1/workflows/${id}`);
    return response.data;
  },

  async deleteWorkflow(id: string): Promise<any> {
    const response = await api.delete(`/api/v1/workflows/${id}`);
    return response.data;
  },

  async deployToCamunda(id: string, xml: string): Promise<any> {
    const response = await api.post(`/api/v1/workflows/${id}/deploy-camunda`, { xml });
    return response.data;
  },

  async deployToDmn(id: string, xml: string): Promise<any> {
    const response = await api.post(`/api/v1/workflows/${id}/deploy-dmn`, { xml });
    return response.data;
  },

  async validateBpmn(xml: string): Promise<{ valid: boolean; errors?: string[] }> {
    const response = await api.post('/api/v1/workflows/validate-bpmn', { xml });
    return response.data;
  },

  async validateDmn(xml: string): Promise<{ valid: boolean; errors?: string[] }> {
    const response = await api.post('/api/v1/workflows/validate-dmn', { xml });
    return response.data;
  },

  async testDecisionTable(xml: string, inputVariables: Record<string, any>): Promise<any> {
    const response = await api.post('/api/v1/workflows/test-decision-table', { xml, inputVariables });
    return response.data;
  },
};
