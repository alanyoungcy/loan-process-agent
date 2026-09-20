/**
 * Simplified DMN Modeler Component
 * Note: This is a placeholder. For full DMN editing, use Camunda Modeler desktop app.
 */

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

interface DmnModelerProps {
  xml?: string;
  onSave?: (xml: string) => void;
  onDeployDmn?: (xml: string) => void;
  readOnly?: boolean;
  height?: string;
}

const DmnModelerComponent: React.FC<DmnModelerProps> = ({
  xml,
  onSave,
  onDeployDmn,
  readOnly = false,
  height = '600px',
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isDirty, setIsDirty] = useState(false);

  const handleSave = () => {
    if (onSave && xml) {
      onSave(xml);
      setIsDirty(false);
      alert('Decision table saved successfully!');
    }
  };

  const handleDeploy = () => {
    if (onDeployDmn && xml) {
      onDeployDmn(xml);
      alert('Decision table deployed to Camunda DMN!');
    }
  };

  const openOperate = () => {
    window.open('http://localhost:8080', '_blank');
  };

  return (
    <div className="dmn-modeler-container">
      {/* Toolbar */}
      <div className="flex justify-between items-center p-4 bg-gray-50 border-b">
        <div className="flex gap-2">
          <Button onClick={handleSave} disabled={readOnly} variant="primary">
            Save Decision Table
          </Button>
          {onDeployDmn && (
            <Button onClick={handleDeploy} disabled={readOnly} variant="success">
              Deploy to DMN Engine
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
        <Card className="bg-purple-50 border-purple-200">
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-purple-900 mb-2">
                📊 DMN Decision Table Editor
              </h3>
              <p className="text-purple-800 mb-4">
                Design DMN decision tables to define business rules visually using Camunda Modeler desktop app.
                Download from camunda.com/download. Deploy and execute rules in Camunda DMN engine.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-4 rounded border border-purple-200">
                <h4 className="font-semibold text-gray-900 mb-2">Features Available:</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>✓ Visual decision table editor</li>
                  <li>✓ Input/output columns</li>
                  <li>✓ Rule rows with conditions</li>
                  <li>✓ DMN 1.3 standard</li>
                  <li>✓ Deploy to Camunda DMN engine</li>
                  <li>✓ Test with sample data</li>
                </ul>
              </div>

              <div className="bg-white p-4 rounded border border-purple-200">
                <h4 className="font-semibold text-gray-900 mb-2">Example Rules:</h4>
                <div className="text-sm text-gray-700 space-y-2">
                  <div className="bg-gray-50 p-2 rounded font-mono text-xs">
                    IF overdue_days &lt; 30<br />
                    THEN strategy = "SMS"
                  </div>
                  <div className="bg-gray-50 p-2 rounded font-mono text-xs">
                    IF overdue_days &gt; 90<br />
                    THEN strategy = "Legal"
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white p-4 rounded border border-purple-200">
              <h4 className="font-semibold text-gray-900 mb-3">Active Decision Tables:</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm font-medium">Compliance Check</span>
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">5 Rules</span>
                </div>
                <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm font-medium">Priority Scoring</span>
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">4 Rules</span>
                </div>
                <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm font-medium">Contact Strategy</span>
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">3 Rules</span>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              <Button onClick={openOperate} variant="primary" className="flex-1">
                Open Camunda Operate →
              </Button>
            </div>
          </div>
        </Card>

        {/* Natural Language to DMN */}
        <Card className="mt-6 bg-blue-50 border-blue-200">
          <div className="p-4">
            <h4 className="font-semibold text-blue-900 mb-2">
              💡 Natural Language Rule Generation
            </h4>
            <p className="text-sm text-blue-800 mb-3">
              You can describe rules in plain English and AI converts them to DMN:
            </p>
            <div className="bg-white p-3 rounded border border-blue-200 mb-3">
              <p className="text-sm font-mono text-gray-700">
                "If overdue days is greater than 90 and amount exceeds 100,000, set priority to 10"
              </p>
            </div>
            <p className="text-xs text-blue-700">
              → AI automatically converts to DMN decision table format
            </p>
          </div>
        </Card>

        {/* Quick Actions */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={openOperate}>
            <div className="p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Camunda Operate</h4>
              <p className="text-sm text-gray-600">Monitor workflows & decisions</p>
              <p className="text-xs text-blue-600 mt-2">http://localhost:8080</p>
            </div>
          </Card>

          <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => window.open('http://localhost:8081/api/rules/health', '_blank')}>
            <div className="p-4">
              <h4 className="font-semibold text-gray-900 mb-2">DMN Service</h4>
              <p className="text-sm text-gray-600">Rules engine API</p>
              <p className="text-xs text-blue-600 mt-2">http://localhost:8081</p>
            </div>
          </Card>

          <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => window.open('https://camunda.com/download', '_blank')}>
            <div className="p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Download Modeler</h4>
              <p className="text-sm text-gray-600">Desktop DMN editor</p>
              <p className="text-xs text-gray-500 mt-2">Get Camunda Modeler 8</p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DmnModelerComponent;
