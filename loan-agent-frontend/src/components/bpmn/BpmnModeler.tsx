/**
 * Simplified BPMN Modeler Component
 * Note: This is a placeholder. For full BPMN editing, use Camunda directly.
 */

import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

interface BpmnModelerProps {
  xml?: string;
  onSave?: (xml: string) => void;
  onDeploy?: (xml: string) => void;
  readOnly?: boolean;
  height?: string;
}

const BpmnModelerComponent: React.FC<BpmnModelerProps> = ({
  xml,
  onSave,
  onDeploy,
  readOnly = false,
  height = '600px',
}) => {
  const [isDirty, setIsDirty] = useState(false);

  const handleSave = () => {
    if (onSave && xml) {
      onSave(xml);
      setIsDirty(false);
      alert('Workflow saved successfully!');
    }
  };

  const handleDeploy = () => {
    if (onDeploy && xml) {
      onDeploy(xml);
      alert('Workflow deployed to Camunda!');
    }
  };

  const openOperate = () => {
    window.open('http://localhost:8080', '_blank');
  };

  return (
    <div className="bpmn-modeler-container">
      {/* Toolbar */}
      <div className="flex justify-between items-center p-4 bg-gray-50 border-b">
        <div className="flex gap-2">
          <Button onClick={handleSave} disabled={readOnly} variant="primary">
            Save Workflow
          </Button>
          {onDeploy && (
            <Button onClick={handleDeploy} disabled={readOnly} variant="success">
              Deploy to Camunda
            </Button>
          )}
        </div>
        <div className="flex gap-2">
          <Button onClick={openOperate} variant="secondary">
            Open Camunda Operate
          </Button>
        </div>
      </div>

      {/* Info Card */}
      <div className="p-6">
        <Card className="bg-blue-50 border-blue-200">
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                🎨 BPMN Workflow Designer
              </h3>
              <p className="text-blue-800 mb-4">
                Design BPMN workflows using Camunda Modeler desktop app.
                Download from camunda.com/download. Deploy and monitor workflows in Camunda Operate.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-4 rounded border border-blue-200">
                <h4 className="font-semibold text-gray-900 mb-2">Features Available:</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>✓ Visual BPMN 2.0 editor (desktop app)</li>
                  <li>✓ Service tasks (Zeebe workers)</li>
                  <li>✓ User tasks (human steps)</li>
                  <li>✓ Gateways and events</li>
                  <li>✓ Properties configuration</li>
                  <li>✓ Deploy to Zeebe engine</li>
                </ul>
              </div>

              <div className="bg-white p-4 rounded border border-blue-200">
                <h4 className="font-semibold text-gray-900 mb-2">How to Use:</h4>
                <ol className="text-sm text-gray-700 space-y-1 list-decimal list-inside">
                  <li>Download Camunda Modeler 8</li>
                  <li>Design your workflow visually</li>
                  <li>Configure Zeebe task types</li>
                  <li>Deploy to Zeebe via Operate</li>
                  <li>Monitor execution in Operate</li>
                </ol>
              </div>
            </div>

            <div className="flex gap-2">
              <Button onClick={openOperate} variant="primary" className="flex-1">
                Open Camunda Operate →
              </Button>
            </div>
          </div>
        </Card>

        {/* Quick Access Links */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={openOperate}>
            <div className="p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Camunda Operate</h4>
              <p className="text-sm text-gray-600">Monitor & manage workflows</p>
              <p className="text-xs text-blue-600 mt-2">http://localhost:8080</p>
            </div>
          </Card>

          <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => window.open('http://localhost:8082', '_blank')}>
            <div className="p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Camunda Tasklist</h4>
              <p className="text-sm text-gray-600">Manage human tasks</p>
              <p className="text-xs text-blue-600 mt-2">http://localhost:8082</p>
            </div>
          </Card>

          <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => window.open('https://camunda.com/download', '_blank')}>
            <div className="p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Download Modeler</h4>
              <p className="text-sm text-gray-600">Desktop BPMN editor</p>
              <p className="text-xs text-gray-500 mt-2">Get Camunda Modeler 8</p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default BpmnModelerComponent;
