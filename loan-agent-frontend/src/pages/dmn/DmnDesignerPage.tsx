/**
 * DMN Designer Page
 * Visual DMN decision table editor
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { VisualDmnEditor } from '../../components/bpmn/VisualDmnEditor';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';

// Available DMN decisions to load
const AVAILABLE_DECISIONS = [
  { id: 'new', name: 'New Decision Table', file: null },
  { id: 'compliance-check', name: 'Compliance Check', file: 'compliance-check-fixed.dmn' },
  { id: 'priority-scoring', name: 'Priority Scoring', file: 'priority-scoring-fixed.dmn' },
  { id: 'contact-strategy', name: 'Contact Strategy', file: 'contact-strategy.dmn' },
];

export const DmnDesignerPage: React.FC = () => {
  const navigate = useNavigate();
  const [dmnXml, setDmnXml] = useState<string | undefined>(undefined);
  const [selectedDecision, setSelectedDecision] = useState<string>('new');
  const [currentXml, setCurrentXml] = useState<string | undefined>(undefined);

  const handleLoadDecision = async (decisionId: string) => {
    const decision = AVAILABLE_DECISIONS.find(d => d.id === decisionId);
    if (!decision) return;

    setSelectedDecision(decisionId);

    if (decisionId === 'new') {
      setCurrentXml(undefined);
      return;
    }

    if (decision.file) {
      try {
        console.log(`📥 Loading decision: ${decision.name}`);
        const response = await fetch(`/workflows/${decision.file}`);
        if (response.ok) {
          const xmlContent = await response.text();
          setCurrentXml(xmlContent);
          console.log(`✅ Loaded ${decision.name}`);
        } else {
          console.error(`Failed to load ${decision.file}`);
          alert(`Could not load decision. File might not be accessible.`);
        }
      } catch (err) {
        console.error('Error loading decision:', err);
        alert('Error loading decision from server');
      }
    }
  };

  const handleDmnSave = async (xml: string) => {
    try {
      setDmnXml(xml);
      setCurrentXml(xml);
      console.log('DMN saved locally');
      alert('✅ DMN decision saved locally!');
    } catch (error) {
      console.error('Error saving DMN:', error);
    }
  };

  const handleDmnDeploy = async (xml: string) => {
    try {
      // Deploy to Camunda via zbctl or backend API
      // For now, show instructions
      console.log('DMN deploy requested');
      alert('✅ To deploy this DMN:\n\n1. Save the file (.dmn)\n2. Use: zbctl deploy <file>.dmn --address localhost:26500 --insecure\n\nOr integrate with backend deployment API.');
    } catch (error) {
      console.error('Error deploying DMN:', error);
      alert('Failed to deploy. Check console for details.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">DMN Decision Table Designer</h1>
          <p className="text-gray-600 mt-1">
            Visual DMN editor • Edit decision tables and deploy to Camunda
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => window.open('http://localhost:8080', '_blank')}
            variant="secondary"
          >
            Open Camunda Operate
          </Button>
          <Button onClick={() => navigate('/rules')} variant="secondary">
            ← Back to Rules
          </Button>
        </div>
      </div>

      {/* DMN Editor */}
      <Card>
        <div className="p-6">
          <div className="mb-4 p-4 bg-purple-50 border border-purple-200 rounded">
            <h3 className="font-semibold text-purple-900 mb-2">Visual DMN Editor</h3>
            <p className="text-sm text-purple-800">
              Create and edit decision tables by modifying rows and columns. Define input conditions
              and output values. Deploy to Camunda when ready.
            </p>
          </div>

          {/* Decision Selector */}
          <div className="mb-4 flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Load Decision:</label>
            <select
              value={selectedDecision}
              onChange={(e) => handleLoadDecision(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {AVAILABLE_DECISIONS.map(dec => (
                <option key={dec.id} value={dec.id}>{dec.name}</option>
              ))}
            </select>
          </div>

          <VisualDmnEditor
            xml={currentXml || dmnXml}
            onSave={handleDmnSave}
            onDeploy={handleDmnDeploy}
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
              <h4 className="font-medium text-purple-900 mb-2">Creating Decision Tables:</h4>
              <ul className="space-y-1 text-gray-700">
                <li>• Click cells to edit input conditions</li>
                <li>• Click output cells to set values</li>
                <li>• Right-click to add/remove rows and columns</li>
                <li>• Save locally or deploy to Camunda</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-blue-900 mb-2">Using in Workflows:</h4>
              <ul className="space-y-1 text-gray-700">
                <li>• Add Business Rule Task to BPMN workflow</li>
                <li>• Set Decision ID (e.g., "complianceCheck")</li>
                <li>• Decision is called during workflow execution</li>
                <li>• Results stored in workflow variables</li>
              </ul>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default DmnDesignerPage;
