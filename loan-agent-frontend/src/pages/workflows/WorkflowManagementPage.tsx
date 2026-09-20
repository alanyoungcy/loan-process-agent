/**
 * Workflow Designer Page
 * Visual BPMN editor only - DMN opens contextually when clicking Business Rule Tasks
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { VisualBpmnEditor } from '../../components/bpmn/VisualBpmnEditor';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { workflowService } from '../../services/workflowService';

export const WorkflowManagementPage: React.FC = () => {
  console.log('🚀 WorkflowManagementPage loaded');

  const navigate = useNavigate();
  const [bpmnXml, setBpmnXml] = useState<string | undefined>(undefined);

  const handleBpmnSave = async (xml: string) => {
    try {
      setBpmnXml(xml);
      console.log('BPMN saved locally');
    } catch (error) {
      console.error('Error saving BPMN:', error);
    }
  };

  const handleBpmnDeploy = async (xml: string) => {
    try {
      // Deploy to Camunda via backend
      await workflowService.deployCamunda('new-workflow', xml);
      console.log('BPMN deployed to Camunda');
      alert('✅ Deployed successfully! Check Camunda Operate.');
    } catch (error) {
      console.error('Error deploying BPMN:', error);
      alert('Failed to deploy. Check console for details.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workflow Designer</h1>
          <p className="text-gray-600 mt-1">
            Visual BPMN editor • Click Business Rule Tasks to edit DMN decisions
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => window.open('http://localhost:8080', '_blank')}
            variant="primary"
          >
            Open Camunda Operate
          </Button>
          <Button onClick={() => navigate('/workflows')} variant="secondary">
            ← Back to Workflows
          </Button>
        </div>
      </div>

      {/* BPMN Editor */}
      <Card>
        <div className="p-6">
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded">
            <h3 className="font-semibold text-blue-900 mb-2">Visual BPMN Editor</h3>
            <p className="text-sm text-blue-800">
              Design workflows by dragging and dropping elements. Click on Business Rule Tasks to edit their DMN decisions.
              Deploy directly to Camunda Operate when ready.
            </p>
          </div>
          <VisualBpmnEditor
            xml={bpmnXml}
            onSave={handleBpmnSave}
            onDeploy={handleBpmnDeploy}
            height="700px"
          />
        </div>
      </Card>

      {/* Help Section */}
      <Card>
        <div className="p-6">
          <h3 className="font-semibold text-gray-900 mb-3">📚 Quick Guide</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="font-medium text-blue-900 mb-2">BPMN Workflow Design:</h4>
              <ul className="space-y-1 text-gray-700">
                <li>• Drag elements from the left palette</li>
                <li>• Connect elements to create flow</li>
                <li>• Click elements to configure properties</li>
                <li>• Save locally or deploy to Camunda</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-purple-900 mb-2">DMN Decision Tables:</h4>
              <ul className="space-y-1 text-gray-700">
                <li>• Add Business Rule Task to your workflow</li>
                <li>• Click the task to configure its decision</li>
                <li>• DMN decisions are embedded in workflows</li>
                <li>• All deployed to Camunda together</li>
              </ul>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default WorkflowManagementPage;
