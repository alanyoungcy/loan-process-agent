/**
 * Real DMN Modeler Component using dmn-js
 */

import React, { useEffect, useRef, useState } from 'react';
import DmnModeler from 'dmn-js/lib/Modeler';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

interface RealDmnModelerProps {
  xml?: string;
  onSave?: (xml: string) => void;
  onDeployDmn?: (xml: string) => void;
  readOnly?: boolean;
  height?: string;
}

const RealDmnModelerComponent: React.FC<RealDmnModelerProps> = ({
  xml,
  onSave,
  onDeployDmn,
  readOnly = false,
  height = '600px',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const modelerRef = useRef<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    const initModeler = async () => {
      try {
        console.log('Initializing DMN modeler...');
        setLoading(true);
        setError(null);

        const modeler = new DmnModeler({
          container: containerRef.current!,
          drd: {
            propertiesPanel: {},
          },
        });

        modelerRef.current = modeler;

        console.log('DMN modeler created');

        // Load XML or create new
        const dmnXml = xml || createEmptyDmnXml();
        await modeler.importXML(dmnXml);

        console.log('DMN XML imported successfully');

        // Listen for changes
        modeler.on('commandStack.changed', () => {
          setHasChanges(true);
        });

        setLoading(false);
      } catch (err) {
        console.error('Error loading DMN modeler:', err);
        setError(err instanceof Error ? err.message : 'Failed to load DMN modeler');
        setLoading(false);
      }
    };

    initModeler();

    return () => {
      if (modelerRef.current) {
        modelerRef.current.destroy();
      }
    };
  }, [xml]);

  const handleSave = async () => {
    if (!modelerRef.current) return;

    try {
      const { xml: savedXml } = await modelerRef.current.saveXML({ format: true });
      if (onSave) {
        onSave(savedXml);
      }
      setHasChanges(false);
      alert('✅ Decision table saved successfully!');
    } catch (err) {
      console.error('Error saving DMN:', err);
      alert('❌ Failed to save decision table');
    }
  };

  const handleDeploy = async () => {
    if (!modelerRef.current) return;

    try {
      const { xml: exportedXml } = await modelerRef.current.saveXML({ format: true });
      if (onDeployDmn) {
        onDeployDmn(exportedXml);
      }
      alert('✅ Deployed to Camunda DMN!');
    } catch (err) {
      console.error('Error deploying DMN:', err);
      alert('❌ Failed to deploy');
    }
  };

  const handleDownload = async () => {
    if (!modelerRef.current) return;

    try {
      const { xml: downloadXml } = await modelerRef.current.saveXML({ format: true });
      const blob = new Blob([downloadXml], { type: 'application/xml' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'decision-table.dmn';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading DMN:', err);
      alert('❌ Failed to download');
    }
  };

  if (loading) {
    return (
      <Card>
        <div className="flex items-center justify-center" style={{ height }}>
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading DMN Modeler...</p>
          </div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <div className="flex flex-col items-center justify-center text-center p-8" style={{ height }}>
          <p className="text-red-600 font-semibold mb-2">Failed to load DMN Modeler</p>
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          <p className="text-xs text-gray-500">
            Make sure dmn-js is installed: npm install dmn-js
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="dmn-modeler-real">
      {/* Toolbar */}
      <div className="flex justify-between items-center p-4 bg-gray-50 border-b border-gray-200">
        <div className="flex gap-2">
          <Button
            onClick={handleSave}
            disabled={readOnly || !hasChanges}
            variant="primary"
          >
            💾 Save Decision Table
          </Button>
          {onDeployDmn && (
            <Button
              onClick={handleDeploy}
              disabled={readOnly}
              variant="success"
            >
              🚀 Deploy to DMN Engine
            </Button>
          )}
          <Button onClick={handleDownload} variant="secondary">
            ⬇️ Download DMN
          </Button>
        </div>
        <div className="text-sm text-gray-600">
          {hasChanges && <span className="text-orange-600">● Unsaved changes</span>}
        </div>
      </div>

      {/* DMN Modeler Canvas */}
      <div
        ref={containerRef}
        style={{
          height,
          border: '1px solid #e5e7eb',
          backgroundColor: '#ffffff'
        }}
      />

      {/* Help Text */}
      <div className="p-4 bg-blue-50 border-t border-blue-200">
        <p className="text-sm text-blue-900">
          💡 <strong>Tip:</strong> Double-click on elements to edit them. Right-click for more options.
          Use the palette on the left to add inputs, outputs, and rules.
        </p>
      </div>
    </div>
  );
};

// Helper function to create empty DMN XML
function createEmptyDmnXml(): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/"
             xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/"
             xmlns:dc="http://www.omg.org/spec/DD/20100524/DC/"
             id="Definitions_1"
             name="DRD"
             namespace="http://camunda.org/schema/1.0/dmn">
  <decision id="Decision_1" name="Decision 1">
    <decisionTable id="DecisionTable_1">
      <input id="Input_1" label="Input">
        <inputExpression id="InputExpression_1" typeRef="string">
          <text></text>
        </inputExpression>
      </input>
      <output id="Output_1" label="Output" name="" typeRef="string" />
    </decisionTable>
  </decision>
</definitions>`;
}

export default RealDmnModelerComponent;
