/**
 * Simplified DMN Modeler - Uses placeholder until dmn-js can be properly configured
 */

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { AlertCircle } from 'lucide-react';

interface SimpleDmnModelerProps {
  height?: string;
}

const SimpleDmnModelerComponent: React.FC<SimpleDmnModelerProps> = ({
  height = '600px',
}) => {
  const navigate = useNavigate();
  const [dmnXml, setDmnXml] = useState(getExampleDmn());

  const handleSave = () => {
    // Create a blob from the XML content
    const blob = new Blob([dmnXml], { type: 'application/xml' });
    const url = window.URL.createObjectURL(blob);

    // Create a temporary link and trigger download
    const a = document.createElement('a');
    a.href = url;
    a.download = 'collection-strategy.dmn';
    document.body.appendChild(a);
    a.click();

    // Cleanup
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    alert('✅ DMN file saved!');
  };

  const handleLoadExample = () => {
    setDmnXml(getExampleDmn());
    alert('✅ Example DMN loaded!');
  };

  return (
    <div className="dmn-modeler-simple">
      {/* Info Banner */}
      <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-4">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-amber-400 mt-0.5 mr-3" />
          <div>
            <h3 className="text-sm font-medium text-amber-800">
              DMN Visual Editor Configuration Required
            </h3>
            <p className="text-sm text-amber-700 mt-1">
              The visual DMN editor needs additional configuration to load properly.
              For now, you can use the JSON editor below or external tools.
            </p>
          </div>
        </div>
      </div>

      {/* Temporary Text Editor */}
      <Card>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">DMN XML Editor (Temporary)</h3>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm" onClick={handleLoadExample}>
                Load Example
              </Button>
              <Button variant="primary" size="sm" onClick={handleSave}>
                Save DMN
              </Button>
            </div>
          </div>

          <textarea
            className="w-full h-96 p-4 border border-gray-300 rounded-lg font-mono text-sm"
            placeholder="Paste your DMN XML here or load an example..."
            value={dmnXml}
            onChange={(e) => setDmnXml(e.target.value)}
          />

          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              💡 <strong>Tip:</strong> You can edit DMN XML directly here and save it
            </div>
            <Button
              variant="secondary"
              onClick={() => window.open('https://demo.bpmn.io/dmn', '_blank')}
            >
              Open External DMN Editor →
            </Button>
          </div>
        </div>
      </Card>

      {/* Help Section */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-blue-50">
          <div className="p-4">
            <h4 className="font-semibold text-blue-900 mb-2">📊 What is DMN?</h4>
            <p className="text-sm text-blue-800">
              Decision Model and Notation - a standard for defining business decisions using decision tables.
            </p>
          </div>
        </Card>

        <Card className="bg-green-50">
          <div className="p-4">
            <h4 className="font-semibold text-green-900 mb-2">✅ Current Rules</h4>
            <p className="text-sm text-green-800">
              View and manage active rules in the <span
                className="underline cursor-pointer"
                onClick={() => navigate('/rules')}
              >Rules Engine</span> page.
            </p>
          </div>
        </Card>

        <Card className="bg-purple-50">
          <div className="p-4">
            <h4 className="font-semibold text-purple-900 mb-2">🔧 Alternative Tools</h4>
            <p className="text-sm text-purple-800">
              Use <a href="https://demo.bpmn.io/dmn" target="_blank" rel="noopener noreferrer" className="underline">
                demo.bpmn.io/dmn
              </a> for visual editing.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};

function getExampleDmn(): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/"
             xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/"
             xmlns:dc="http://www.omg.org/spec/DD/20100524/DC/"
             id="collection_strategy_rules"
             name="Collection Strategy Rules"
             namespace="http://capco.com/dmn/collection">
  <decision id="strategy_decision" name="Determine Collection Strategy">
    <decisionTable id="strategy_table">
      <!-- Input: Overdue Days -->
      <input id="input_overdue_days" label="Overdue Days">
        <inputExpression id="input_expr_1" typeRef="number">
          <text>overdue_days</text>
        </inputExpression>
      </input>

      <!-- Input: Overdue Amount -->
      <input id="input_overdue_amount" label="Overdue Amount">
        <inputExpression id="input_expr_2" typeRef="number">
          <text>overdue_amount</text>
        </inputExpression>
      </input>

      <!-- Output: Strategy -->
      <output id="output_strategy" label="Strategy" name="strategy" typeRef="string" />

      <!-- Rules -->
      <rule id="rule_1">
        <inputEntry id="rule1_input1">
          <text>&lt; 30</text>
        </inputEntry>
        <inputEntry id="rule1_input2">
          <text>-</text>
        </inputEntry>
        <outputEntry id="rule1_output">
          <text>"SMS"</text>
        </outputEntry>
      </rule>

      <rule id="rule_2">
        <inputEntry id="rule2_input1">
          <text>[30..90]</text>
        </inputEntry>
        <inputEntry id="rule2_input2">
          <text>&lt; 10000</text>
        </inputEntry>
        <outputEntry id="rule2_output">
          <text>"Call"</text>
        </outputEntry>
      </rule>

      <rule id="rule_3">
        <inputEntry id="rule3_input1">
          <text>[30..90]</text>
        </inputEntry>
        <inputEntry id="rule3_input2">
          <text>&gt;= 10000</text>
        </inputEntry>
        <outputEntry id="rule3_output">
          <text>"Email"</text>
        </outputEntry>
      </rule>

      <rule id="rule_4">
        <inputEntry id="rule4_input1">
          <text>&gt; 90</text>
        </inputEntry>
        <inputEntry id="rule4_input2">
          <text>-</text>
        </inputEntry>
        <outputEntry id="rule4_output">
          <text>"Legal"</text>
        </outputEntry>
      </rule>
    </decisionTable>
  </decision>
</definitions>`;
}

export default SimpleDmnModelerComponent;
