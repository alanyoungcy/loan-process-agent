import React, { useState } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { X, PlayCircle, CheckCircle2, XCircle } from 'lucide-react';
import { rulesService } from '../../services/rulesService';

interface TestRuleModalProps {
  isOpen: boolean;
  onClose: () => void;
  ruleName?: string;
}

export const TestRuleModal: React.FC<TestRuleModalProps> = ({
  isOpen,
  onClose,
  ruleName,
}) => {
  const [caseId, setCaseId] = useState('');
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<any>(null);

  if (!isOpen) return null;

  const handleTest = async () => {
    if (!caseId.trim()) {
      alert('Please enter a Case ID');
      return;
    }

    setTesting(true);
    setResult(null);

    try {
      const response = await rulesService.evaluateCase({
        case_id: caseId,
        auto_apply: false,
      });
      setResult(response);
    } catch (error: any) {
      setResult({
        error: true,
        message: error.message || 'Failed to test rule',
      });
    } finally {
      setTesting(false);
    }
  };

  const handleClose = () => {
    setCaseId('');
    setResult(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              Test {ruleName ? `Rule: ${ruleName}` : 'Rules'}
            </h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Input Section */}
          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Case ID to Test
              </label>
              <input
                type="text"
                value={caseId}
                onChange={(e) => setCaseId(e.target.value)}
                placeholder="Enter case ID (e.g., CASE-001)"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-sm text-gray-500 mt-1">
                Enter the ID of a case to test the rule against
              </p>
            </div>

            <Button
              onClick={handleTest}
              disabled={testing || !caseId.trim()}
              variant="primary"
              className="w-full"
            >
              {testing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Testing...
                </>
              ) : (
                <>
                  <PlayCircle className="h-4 w-4 mr-2" />
                  Run Test
                </>
              )}
            </Button>
          </div>

          {/* Results Section */}
          {result && (
            <div className="space-y-4">
              <div className="border-t border-gray-200 pt-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Results</h3>

                {result.error ? (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-red-800">
                      <XCircle className="h-5 w-5" />
                      <span className="font-semibold">Test Failed</span>
                    </div>
                    <p className="text-red-700 mt-2">{result.message}</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {/* Summary */}
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex items-center gap-2 text-green-800 mb-2">
                        <CheckCircle2 className="h-5 w-5" />
                        <span className="font-semibold">Test Completed Successfully</span>
                      </div>
                      <div className="grid grid-cols-2 gap-4 mt-3">
                        <div>
                          <p className="text-sm text-green-700">Rules Executed</p>
                          <p className="text-2xl font-bold text-green-900">
                            {result.rules_executed?.length || 0}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-green-700">Can Contact</p>
                          <p className="text-2xl font-bold text-green-900">
                            {result.can_contact ? 'Yes' : 'No'}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Rules Executed */}
                    {result.rules_executed && result.rules_executed.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Rules Executed</h4>
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                          <ul className="space-y-1">
                            {result.rules_executed.map((rule: string, idx: number) => (
                              <li key={idx} className="text-blue-900 text-sm">
                                • {rule}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}

                    {/* Actions Taken */}
                    {result.actions_taken && result.actions_taken.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Actions Taken</h4>
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                          <ul className="space-y-1">
                            {result.actions_taken.map((action: string, idx: number) => (
                              <li key={idx} className="text-purple-900 text-sm">
                                → {action}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}

                    {/* Modifications */}
                    {result.modifications && Object.keys(result.modifications).length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Modifications</h4>
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                          <div className="space-y-2">
                            {Object.entries(result.modifications).map(([key, value]) => (
                              <div key={key} className="flex justify-between text-sm">
                                <span className="text-yellow-900 font-medium">{key}:</span>
                                <span className="text-yellow-800">
                                  {JSON.stringify(value)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Recommendations */}
                    {result.recommendations && result.recommendations.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Recommendations</h4>
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                          <ul className="space-y-1">
                            {result.recommendations.map((rec: string, idx: number) => (
                              <li key={idx} className="text-gray-900 text-sm">
                                💡 {rec}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="mt-6 flex justify-end gap-3 border-t border-gray-200 pt-4">
            <Button onClick={handleClose} variant="secondary">
              Close
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};
