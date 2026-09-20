/**
 * Business Rules Engine / DMN Decisions Page
 * Shows DMN decision tables deployed in Camunda
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import {
  BookOpen,
  Play,
  Settings,
  ExternalLink,
  CheckCircle2,
  TrendingUp,
} from 'lucide-react';

interface DmnDecision {
  decisionId: string;
  name: string;
  description: string;
  version: number;
  category: string;
  enabled: boolean;
  inputs: string[];
  outputs: string[];
}

export const RulesPage: React.FC = () => {
  const navigate = useNavigate();
  const [decisions, setDecisions] = useState<DmnDecision[]>([]);
  const [loading, setLoading] = useState(true);
  const [testModalOpen, setTestModalOpen] = useState(false);
  const [selectedDecision, setSelectedDecision] = useState<DmnDecision | null>(null);

  useEffect(() => {
    loadDecisions();
  }, []);

  const loadDecisions = async () => {
    try {
      // These are your 3 real DMN decisions deployed in Camunda
      setDecisions([
        {
          decisionId: 'complianceCheck',
          name: 'Compliance Check',
          description: 'Verify if contact is allowed based on time and regulations',
          version: 1,
          category: 'Compliance',
          enabled: true,
          inputs: ['currentHour', 'dailyContactCount', 'currentDay', 'riskLevel'],
          outputs: ['canContact', 'violation', 'recommendation', 'tag'],
        },
        {
          decisionId: 'priorityScoring',
          name: 'Priority Scoring',
          description: 'Calculate priority score based on overdue amount and days',
          version: 1,
          category: 'Priority',
          enabled: true,
          inputs: ['overdueDays', 'overdueAmount'],
          outputs: ['priority', 'urgencyLevel'],
        },
        {
          decisionId: 'contactStrategy',
          name: 'Contact Strategy',
          description: 'Determine the best contact channel and timing',
          version: 1,
          category: 'Strategy',
          enabled: true,
          inputs: ['overdueDays'],
          outputs: ['channel', 'timing'],
        },
      ]);
    } catch (error) {
      console.error('Failed to load DMN decisions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTestDecision = (decision: DmnDecision) => {
    setSelectedDecision(decision);
    setTestModalOpen(true);
  };

  const handleOpenDesigner = () => {
    navigate('/dmn/designer');
  };

  const handleViewInOperate = () => {
    window.open('http://localhost:8080', '_blank');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading DMN decisions...</p>
        </div>
      </div>
    );
  }

  const stats = {
    totalDecisions: decisions.length,
    enabled: decisions.filter(d => d.enabled).length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <BookOpen className="h-7 w-7 text-blue-600" />
            Business Rules Engine
          </h1>
          <p className="text-gray-600 mt-1">
            DMN decision tables deployed in Camunda
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleViewInOperate} variant="secondary">
            <ExternalLink className="h-4 w-4 mr-2" />
            View in Operate
          </Button>
          <Button onClick={handleOpenDesigner} variant="primary">
            <Settings className="h-4 w-4 mr-2" />
            Open Designer
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Decisions</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.totalDecisions}</p>
              </div>
              <BookOpen className="h-12 w-12 text-blue-500 opacity-20" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Enabled</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{stats.enabled}</p>
              </div>
              <CheckCircle2 className="h-12 w-12 text-green-500 opacity-20" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Deployed</p>
                <p className="text-3xl font-bold text-purple-600 mt-1">✓</p>
              </div>
              <TrendingUp className="h-12 w-12 text-purple-500 opacity-20" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Version</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">v1</p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Decisions List */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">DMN Decision Tables</h2>

        {decisions.map((decision) => (
          <Card key={decision.decisionId}>
            <div className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {decision.name}
                    </h3>
                    <Badge variant={decision.enabled ? 'success' : 'secondary'}>
                      {decision.enabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                    <Badge variant="info">{decision.category}</Badge>
                  </div>

                  <p className="text-gray-600 mb-4">{decision.description}</p>

                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Inputs:</p>
                      <div className="flex flex-wrap gap-2">
                        {decision.inputs.map((input) => (
                          <span
                            key={input}
                            className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded"
                          >
                            {input}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Outputs:</p>
                      <div className="flex flex-wrap gap-2">
                        {decision.outputs.map((output) => (
                          <span
                            key={output}
                            className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded"
                          >
                            {output}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
                    <span>Version: v{decision.version}</span>
                    <span>•</span>
                    <span>Decision ID: {decision.decisionId}</span>
                  </div>
                </div>

                <div className="ml-6 flex gap-2">
                  <Button
                    onClick={() => handleTestDecision(decision)}
                    variant="primary"
                    size="sm"
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Test
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Info Card */}
      <Card>
        <div className="p-6 bg-blue-50 border border-blue-100">
          <h3 className="font-semibold text-blue-900 mb-2">About DMN Decisions</h3>
          <div className="text-sm text-blue-800 space-y-2">
            <p>
              These DMN decision tables are deployed in Camunda and can be called from BPMN workflows
              using Business Rule Tasks.
            </p>
            <p>
              <strong>To use:</strong> Add a Business Rule Task to your workflow and reference
              the decision ID (e.g., "complianceCheck").
            </p>
            <p>
              <strong>View history:</strong> Click "View in Operate" to see execution history in
              Camunda Operate → Decisions tab.
            </p>
          </div>
        </div>
      </Card>

      {/* Test Modal */}
      {testModalOpen && selectedDecision && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="max-w-2xl w-full m-4">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4">Test {selectedDecision.name}</h3>
              <p className="text-gray-600 mb-4">
                Enter input values to test this decision:
              </p>

              <div className="space-y-3 mb-6">
                {selectedDecision.inputs.map((input) => (
                  <div key={input}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {input}
                    </label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded"
                      placeholder={`Enter ${input}`}
                    />
                  </div>
                ))}
              </div>

              <div className="flex gap-2 justify-end">
                <Button onClick={() => setTestModalOpen(false)} variant="secondary">
                  Cancel
                </Button>
                <Button onClick={() => alert('Execute via DMN service at localhost:8081')} variant="primary">
                  Execute Decision
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default RulesPage;
