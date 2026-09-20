import React, { useEffect, useRef, useState } from 'react';
import DmnModeler from 'dmn-js/lib/Modeler';
import 'dmn-js-decision-table/assets/css/dmn-js-decision-table-controls.css';
import 'dmn-js-decision-table/assets/css/dmn-js-decision-table.css';
import 'dmn-js-drd/assets/css/dmn-js-drd.css';
import 'dmn-js-shared/assets/css/dmn-js-shared.css';
import { Button } from '../ui/Button';

interface VisualDmnEditorProps {
  xml?: string;
  onSave?: (xml: string) => void;
  onDeploy?: (xml: string) => void;
  height?: string;
}

const defaultDmnXml = `<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/"
             xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/"
             xmlns:dc="http://www.omg.org/spec/DMN/20180521/DC/"
             xmlns:camunda="http://camunda.org/schema/1.0/dmn"
             id="sample-decision"
             name="Sample Decision"
             namespace="http://camunda.org/schema/1.0/dmn">
  <decision id="Decision_1" name="Sample Decision">
    <decisionTable id="DecisionTable_1" hitPolicy="FIRST">
      <input id="input1" label="Input 1">
        <inputExpression id="inputExpression1" typeRef="string">
          <text>input1</text>
        </inputExpression>
      </input>
      <output id="output1" label="Output 1" name="output1" typeRef="string" />
      <rule id="rule1">
        <inputEntry id="inputEntry1">
          <text>"value1"</text>
        </inputEntry>
        <outputEntry id="outputEntry1">
          <text>"result1"</text>
        </outputEntry>
      </rule>
    </decisionTable>
  </decision>
</definitions>`;

export const VisualDmnEditor: React.FC<VisualDmnEditorProps> = ({
  xml,
  onSave,
  onDeploy,
  height = '600px',
}) => {
  console.log('🎨 VisualDmnEditor component rendering');

  const containerRef = useRef<HTMLDivElement>(null);
  const modelerRef = useRef<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<string>('decisionTable');

  const switchToDecisionTable = () => {
    if (modelerRef.current) {
      const views = modelerRef.current.getViews();
      const decisionView = views.find((v: any) => v.type === 'decisionTable');
      if (decisionView) {
        modelerRef.current.open(decisionView);
        setActiveView('decisionTable');
      }
    }
  };

  const switchToDrd = () => {
    if (modelerRef.current) {
      const views = modelerRef.current.getViews();
      const drdView = views.find((v: any) => v.type === 'drd');
      if (drdView) {
        modelerRef.current.open(drdView);
        setActiveView('drd');
      }
    }
  };

  console.log('📦 DMN Editor state:', { loading, error, hasContainer: !!containerRef.current });

  useEffect(() => {
    if (!containerRef.current) return;

    const initModeler = async () => {
      try {
        console.log('🔧 Initializing DMN modeler...');
        setLoading(true);
        setError(null);

        const modeler = new DmnModeler({
          container: containerRef.current!,
          drd: {
            propertiesPanel: {},
          },
        });

        modelerRef.current = modeler;
        console.log('✅ DMN modeler created');

        // Import diagram
        const diagramXml = xml || defaultDmnXml;
        console.log('📄 Importing DMN XML...');
        await modeler.importXML(diagramXml);
        console.log('✅ DMN XML imported successfully');

        // DMN.js doesn't have a single 'canvas' - it has multiple views
        // Get the active view (usually decision table or DRD)
        const activeEditor = modeler.getActiveViewer();
        if (activeEditor && activeEditor.get) {
          try {
            const canvas = activeEditor.get('canvas');
            if (canvas && canvas.zoom) {
              canvas.zoom('fit-viewport');
              console.log('✅ Canvas zoomed to fit');
            }
          } catch (err) {
            console.log('Note: Canvas zoom not available for this DMN view');
          }
        }

        setLoading(false);
      } catch (err: any) {
        console.error('❌ Error initializing DMN modeler:', err);
        console.error('Error details:', err.message, err.stack);
        setError(err.message || 'Failed to load DMN editor');
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
      alert('✅ DMN decision table saved!');
    } catch (err) {
      console.error('Error saving DMN:', err);
      alert('❌ Failed to save decision table');
    }
  };

  const handleDeploy = async () => {
    if (!modelerRef.current) return;

    try {
      const { xml: deployXml } = await modelerRef.current.saveXML({ format: true });
      if (onDeploy) {
        onDeploy(deployXml);
      }
      alert('✅ Deployed to Camunda!');
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
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading DMN:', err);
      alert('❌ Failed to download');
    }
  };

  return (
    <div className="flex flex-col border border-gray-300 rounded">
      {/* Toolbar */}
      <div className="flex justify-between items-center p-3 bg-gray-50 border-b">
        <div className="flex gap-2">
          <Button onClick={handleSave} variant="primary" size="sm">
            💾 Save
          </Button>
          {onDeploy && (
            <Button onClick={handleDeploy} variant="success" size="sm">
              🚀 Deploy to Camunda
            </Button>
          )}
          <Button onClick={handleDownload} variant="secondary" size="sm">
            ⬇️ Download
          </Button>
        </div>
        <div className="text-sm text-gray-600">
          Visual DMN Editor • Edit decision table rows and columns
        </div>
      </div>

      {/* Canvas */}
      <div ref={containerRef} style={{ height }}>
        {loading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading DMN editor...</p>
            </div>
          </div>
        )}
        {error && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-red-600">
              <p className="text-lg font-semibold mb-2">❌ Error loading editor</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        )}
      </div>

      {/* View Switcher - Shows when DMN is loaded */}
      {!loading && !error && activeView && (
        <div className="p-2 bg-purple-50 border-t flex items-center justify-between">
          <div className="text-xs text-purple-800">
            💡 Current view: <strong>{activeView === 'drd' ? 'Decision Requirements Diagram' : 'Decision Table'}</strong>
          </div>
          <div className="flex gap-2">
            {activeView === 'drd' && (
              <button
                onClick={() => switchToDecisionTable()}
                className="px-3 py-1 text-xs bg-purple-600 text-white rounded hover:bg-purple-700"
              >
                ← Back to Decision Table
              </button>
            )}
            {activeView === 'decisionTable' && (
              <button
                onClick={() => switchToDrd()}
                className="px-3 py-1 text-xs bg-purple-600 text-white rounded hover:bg-purple-700"
              >
                View DRD →
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
