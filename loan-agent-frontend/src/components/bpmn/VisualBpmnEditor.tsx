import React, { useEffect, useRef, useState } from 'react';
import BpmnModeler from 'bpmn-js/lib/Modeler';
import 'bpmn-js/dist/assets/diagram-js.css';
import 'bpmn-js/dist/assets/bpmn-js.css';
import 'bpmn-js/dist/assets/bpmn-font/css/bpmn-embedded.css';
import { Button } from '../ui/Button';

interface VisualBpmnEditorProps {
  xml?: string;
  onSave?: (xml: string) => void;
  onDeploy?: (xml: string) => void;
  height?: string;
}

// Available workflows to load
const AVAILABLE_WORKFLOWS = [
  { id: 'new', name: 'New Workflow', file: null },
  { id: 'standard-collection', name: 'Standard Collection Process', file: 'standard-collection-process.bpmn' },
  { id: 'legal-escalation', name: 'Legal Escalation Process', file: 'legal-escalation-process.bpmn' },
  { id: 'dispute-resolution', name: 'Dispute Resolution Process', file: 'dispute-resolution-process.bpmn' },
  { id: 'loan-collection', name: 'Loan Collection Process', file: 'loan-collection-process.bpmn' },
];

const defaultBpmnXml = `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                   xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                   xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                   xmlns:zeebe="http://camunda.org/schema/zeebe/1.0"
                   id="Definitions_1"
                   targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Start">
      <bpmn:outgoing>Flow_1</bpmn:outgoing>
    </bpmn:startEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Activity_1" />
    <bpmn:serviceTask id="Activity_1" name="Sample Task">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="sample-task" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_1</bpmn:incoming>
      <bpmn:outgoing>Flow_2</bpmn:outgoing>
    </bpmn:serviceTask>
    <bpmn:sequenceFlow id="Flow_2" sourceRef="Activity_1" targetRef="EndEvent_1" />
    <bpmn:endEvent id="EndEvent_1" name="End">
      <bpmn:incoming>Flow_2</bpmn:incoming>
    </bpmn:endEvent>
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="StartEvent_1_di" bpmnElement="StartEvent_1">
        <dc:Bounds x="180" y="100" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Activity_1_di" bpmnElement="Activity_1">
        <dc:Bounds x="300" y="80" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndEvent_1_di" bpmnElement="EndEvent_1">
        <dc:Bounds x="480" y="100" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <di:waypoint x="216" y="118" />
        <di:waypoint x="300" y="120" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_2_di" bpmnElement="Flow_2">
        <di:waypoint x="400" y="120" />
        <di:waypoint x="480" y="118" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`;

export const VisualBpmnEditor: React.FC<VisualBpmnEditorProps> = ({
  xml,
  onSave,
  onDeploy,
  height = '600px',
}) => {
  console.log('🎨 VisualBpmnEditor component rendering');

  const containerRef = useRef<HTMLDivElement>(null);
  const modelerRef = useRef<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>('new');
  const [currentXml, setCurrentXml] = useState<string | undefined>(xml);

  console.log('📦 BPMN Editor state:', { loading, error, hasContainer: !!containerRef.current });

  useEffect(() => {
    console.log('👀 useEffect triggered, containerRef.current:', !!containerRef.current);
    if (!containerRef.current) {
      console.warn('⚠️ Container ref is null, waiting...');
      return;
    }

    const initModeler = async () => {
      try {
        console.log('🔧 Initializing BPMN modeler...');
        setLoading(true);
        setError(null);

        const modeler = new BpmnModeler({
          container: containerRef.current!,
          keyboard: {
            bindTo: document
          }
        });

        modelerRef.current = modeler;
        console.log('✅ BPMN modeler created');

        // Import diagram
        const diagramXml = currentXml || xml || defaultBpmnXml;
        console.log('📄 Importing BPMN XML...');
        await modeler.importXML(diagramXml);
        console.log('✅ BPMN XML imported successfully');

        const canvas = modeler.get('canvas');
        canvas.zoom('fit-viewport');
        console.log('✅ Canvas zoomed to fit');

        setLoading(false);
      } catch (err: any) {
        console.error('❌ Error initializing BPMN modeler:', err);
        console.error('Error details:', err.message, err.stack);
        setError(err.message || 'Failed to load BPMN editor');
        setLoading(false);
      }
    };

    initModeler();

    return () => {
      if (modelerRef.current) {
        modelerRef.current.destroy();
      }
    };
  }, [xml, currentXml]);

  const handleLoadWorkflow = async (workflowId: string) => {
    const workflow = AVAILABLE_WORKFLOWS.find(w => w.id === workflowId);
    if (!workflow) return;

    setSelectedWorkflow(workflowId);

    if (workflowId === 'new') {
      // Load default empty workflow
      setCurrentXml(defaultBpmnXml);
      return;
    }

    if (workflow.file) {
      try {
        console.log(`📥 Loading workflow: ${workflow.name}`);
        // Fetch the workflow file from public folder
        const response = await fetch(`/workflows/${workflow.file}`);
        if (response.ok) {
          const xmlContent = await response.text();
          setCurrentXml(xmlContent);
          console.log(`✅ Loaded ${workflow.name}`);
        } else {
          console.error(`Failed to load ${workflow.file}`);
          alert(`Could not load workflow. File might not be accessible.`);
        }
      } catch (err) {
        console.error('Error loading workflow:', err);
        alert('Error loading workflow from server');
      }
    }
  };

  const handleSave = async () => {
    if (!modelerRef.current) return;

    try {
      const { xml: savedXml } = await modelerRef.current.saveXML({ format: true });
      if (onSave) {
        onSave(savedXml);
      }
      alert('✅ BPMN diagram saved!');
    } catch (err) {
      console.error('Error saving BPMN:', err);
      alert('❌ Failed to save diagram');
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
      console.error('Error deploying BPMN:', err);
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
      a.download = 'workflow.bpmn';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading BPMN:', err);
      alert('❌ Failed to download');
    }
  };

  return (
    <div className="flex flex-col border border-gray-300 rounded">
      {/* Toolbar */}
      <div className="flex justify-between items-center p-3 bg-gray-50 border-b">
        <div className="flex gap-2 items-center">
          <select
            value={selectedWorkflow}
            onChange={(e) => handleLoadWorkflow(e.target.value)}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {AVAILABLE_WORKFLOWS.map(wf => (
              <option key={wf.id} value={wf.id}>{wf.name}</option>
            ))}
          </select>

          <div className="border-l border-gray-300 h-6 mx-2"></div>

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
          Visual BPMN Editor • Drag & drop elements from palette
        </div>
      </div>

      {/* Canvas */}
      <div ref={containerRef} style={{ height }}>
        {loading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading BPMN editor...</p>
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
    </div>
  );
};
