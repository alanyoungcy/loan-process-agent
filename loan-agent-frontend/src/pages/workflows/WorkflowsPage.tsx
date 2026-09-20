import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import {
  Play,
  Edit,
  Eye,
  Workflow,
  Activity,
  Clock,
  CheckCircle2,
  GitBranch,
} from 'lucide-react';
import { workflowService } from '../../services/workflowService';

interface WorkflowDefinition {
  key: string;
  name: string;
  description: string;
  version: number;
  enabled: boolean;
  num_tasks?: number;
}

export const WorkflowsPage: React.FC = () => {
  const navigate = useNavigate();
  const [workflows, setWorkflows] = useState<WorkflowDefinition[]>([]);
  const [loading, setLoading] = useState(true);
  const [startingWorkflow, setStartingWorkflow] = useState<string | null>(null);

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    try {
      const data = await workflowService.listDefinitions();
      setWorkflows(data.workflows || []);
    } catch (error) {
      console.error('Failed to load workflows:', error);
      // Use workflows matching what's deployed in Camunda
      setWorkflows([
        {
          key: 'standard-collection-process',
          name: 'Standard Collection Process',
          description: 'Standard 30-60-90 day collection workflow',
          version: 1,
          enabled: true,
          num_tasks: 8,
        },
        {
          key: 'legal-escalation-process',
          name: 'Legal Escalation Process',
          description: 'Escalate case to legal action',
          version: 1,
          enabled: true,
          num_tasks: 6,
        },
        {
          key: 'dispute-resolution-process',
          name: 'Dispute Resolution Process',
          description: 'Handle customer disputes in compliance with regulations',
          version: 1,
          enabled: true,
          num_tasks: 7,
        },
        {
          key: 'loan-collection-process',
          name: 'Loan Collection Process',
          description: 'Full loan collection workflow with DMN integration',
          version: 1,
          enabled: true,
          num_tasks: 5,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleStartWorkflow = async (workflowKey: string) => {
    setStartingWorkflow(workflowKey);
    try {
      const result = await workflowService.startWorkflow({
        workflow_key: workflowKey,
        business_key: `CASE-${Date.now()}`,
        variables: {},
      });

      alert(`✅ Workflow started successfully!\nInstance ID: ${result.id}`);
      loadWorkflows(); // Refresh
    } catch (error: any) {
      console.error('Failed to start workflow:', error);
      alert(`❌ Failed to start workflow: ${error.message || 'Unknown error'}`);
    } finally {
      setStartingWorkflow(null);
    }
  };

  const handleOpenDesigner = () => {
    navigate('/workflows/designer');
  };

  const handleViewInstances = async (workflowKey: string) => {
    try {
      const instances = await workflowService.getActiveInstances(workflowKey);

      if (instances.length === 0) {
        alert('No active instances for this workflow');
        return;
      }

      // Create a detailed message
      let message = `Active Workflow Instances: ${instances.length}\n\n`;
      instances.slice(0, 5).forEach((instance: WorkflowInstance, idx: number) => {
        message += `${idx + 1}. Instance ID: ${instance.id}\n`;
        message += `   Status: ${instance.status}\n`;
        message += `   Business Key: ${instance.business_key}\n`;
        message += `   Current Task: ${instance.current_task || 'N/A'}\n`;
        message += `   Created: ${new Date(instance.created_at).toLocaleString()}\n\n`;
      });

      if (instances.length > 5) {
        message += `... and ${instances.length - 5} more`;
      }

      alert(message);
    } catch (error) {
      console.error('Failed to load instances:', error);
      alert('Failed to load workflow instances');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading workflows...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Workflows</h1>
          <p className="text-gray-600 mt-1">Manage and monitor collection workflows</p>
        </div>
        <div className="flex gap-3">
          <Button onClick={() => navigate('/workflows/designer')} variant="primary">
            <Edit className="w-4 h-4 mr-2" />
            Open BPMN/DMN Designer
          </Button>
        </div>
      </div>

      {/* Info Banner */}
      <Card className="bg-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <div className="bg-blue-100 p-2 rounded-lg">
            <Workflow className="w-5 h-5 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-blue-900">Visual Workflow Designer</h3>
            <p className="text-sm text-blue-700 mt-1">
              Click "Open BPMN/DMN Designer" to create new workflows using drag-and-drop visual editor.
              Design BPMN processes and DMN decision tables, then deploy directly to Camunda.
            </p>
          </div>
        </div>
      </Card>

      {/* Workflow Definitions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workflows.map((workflow) => (
          <Card key={workflow.key} className="hover:shadow-lg transition-shadow">
            <div className="space-y-4">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-gray-900">{workflow.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{workflow.description}</p>
                </div>
                <Badge variant={workflow.enabled ? 'success' : 'secondary'}>
                  {workflow.enabled ? 'Active' : 'Inactive'}
                </Badge>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4 py-3 border-t border-b border-gray-200">
                <div>
                  <div className="flex items-center gap-2 text-gray-600 mb-1">
                    <GitBranch className="w-4 h-4" />
                    <span className="text-xs">Version</span>
                  </div>
                  <p className="text-xl font-semibold text-gray-900">v{workflow.version}</p>
                </div>
                <div>
                  <div className="flex items-center gap-2 text-gray-600 mb-1">
                    <Activity className="w-4 h-4" />
                    <span className="text-xs">Tasks</span>
                  </div>
                  <p className="text-xl font-semibold text-gray-900">{workflow.num_tasks || 'N/A'}</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <Button
                  onClick={() => handleStartWorkflow(workflow.key)}
                  disabled={!workflow.enabled || startingWorkflow === workflow.key}
                  className="flex-1"
                  variant="primary"
                  size="sm"
                >
                  {startingWorkflow === workflow.key ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Starting...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-1" />
                      Start
                    </>
                  )}
                </Button>
                <Button
                  onClick={() => handleViewInstances(workflow.key)}
                  variant="secondary"
                  size="sm"
                >
                  <Eye className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {workflows.length === 0 && (
        <Card className="text-center py-12">
          <Workflow className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Workflows Yet</h3>
          <p className="text-gray-600 mb-6">
            Create your first workflow using the visual BPMN/DMN designer
          </p>
          <Button onClick={handleOpenDesigner} variant="primary">
            <Edit className="w-4 h-4 mr-2" />
            Open Designer
          </Button>
        </Card>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-3 rounded-lg">
              <Workflow className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-blue-700">Total Workflows</p>
              <p className="text-2xl font-bold text-blue-900">{workflows.length}</p>
            </div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <div className="flex items-center gap-3">
            <div className="bg-green-600 p-3 rounded-lg">
              <CheckCircle2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-green-700">Active</p>
              <p className="text-2xl font-bold text-green-900">
                {workflows.filter(w => w.enabled).length}
              </p>
            </div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <div className="flex items-center gap-3">
            <div className="bg-purple-600 p-3 rounded-lg">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-purple-700">Running</p>
              <p className="text-2xl font-bold text-purple-900">0</p>
            </div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <div className="flex items-center gap-3">
            <div className="bg-orange-600 p-3 rounded-lg">
              <Clock className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-orange-700">Avg Duration</p>
              <p className="text-2xl font-bold text-orange-900">18d</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
