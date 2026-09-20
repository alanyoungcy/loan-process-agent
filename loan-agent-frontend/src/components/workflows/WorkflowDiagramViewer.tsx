import React, { useEffect, useRef, useState } from 'react';
import { Card, CardTitle, CardContent, LoadingSpinner } from '@/components/ui';

interface WorkflowDiagramViewerProps {
  workflowKey: string;
  bpmnXml?: string;
}

export const WorkflowDiagramViewer: React.FC<WorkflowDiagramViewerProps> = ({
  workflowKey,
  bpmnXml
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const loadBpmnViewer = async () => {
      try {
        // Dynamically import bpmn-js to avoid SSR issues
        const BpmnJS = (await import('bpmn-js/lib/Viewer')).default;

        const viewer = new BpmnJS({
          container: containerRef.current!,
          width: '100%',
          height: '600px'
        });

        // Use provided XML or fetch from backend
        let xml = bpmnXml;

        if (!xml) {
          // Fetch BPMN XML from backend
          const response = await fetch(`http://localhost:8000/api/v1/workflows/definitions/${workflowKey}/diagram`);
          if (!response.ok) {
            throw new Error('Failed to load workflow diagram');
          }
          const data = await response.json();
          xml = data.bpmn_xml || generateSampleBpmn(workflowKey);
        }

        await viewer.importXML(xml);

        // Zoom to fit
        const canvas = viewer.get('canvas');
        canvas.zoom('fit-viewport');

        setLoading(false);
      } catch (err) {
        console.error('Error loading BPMN viewer:', err);
        setError(err instanceof Error ? err.message : 'Failed to load diagram');
        setLoading(false);
      }
    };

    loadBpmnViewer();
  }, [workflowKey, bpmnXml]);

  if (loading) {
    return (
      <Card>
        <CardContent>
          <div className="flex items-center justify-center h-96">
            <LoadingSpinner size="lg" />
            <span className="ml-3 text-capco-gray-600">Loading workflow diagram...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-96 text-center">
            <p className="text-capco-red mb-2">Failed to load diagram</p>
            <p className="text-sm text-capco-gray-600">{error}</p>
            <p className="text-sm text-capco-gray-500 mt-4">
              Showing text-based workflow description instead
            </p>
            <div className="mt-6 text-left max-w-2xl">
              <WorkflowTextDescription workflowKey={workflowKey} />
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardTitle>Workflow Diagram - {workflowKey}</CardTitle>
      <CardContent>
        <div
          ref={containerRef}
          className="border border-capco-gray-200 rounded-capco bg-white"
          style={{ minHeight: '600px' }}
        />
        <div className="mt-4 text-sm text-capco-gray-600">
          <p>💡 Tip: Scroll to zoom, drag to pan</p>
        </div>
      </CardContent>
    </Card>
  );
};

// Fallback text description if diagram fails to load
const WorkflowTextDescription: React.FC<{ workflowKey: string }> = ({ workflowKey }) => {
  const descriptions: Record<string, any> = {
    standard_collection: {
      name: 'Standard Collection Process',
      steps: [
        'Initial Contact - Send reminder SMS/Email',
        'Follow-up Call - Contact customer within 3 days',
        'Payment Negotiation - Offer payment plan if needed',
        'Escalation Check - Evaluate for further action',
        'Legal Review - Assess if legal action needed',
        'Resolution - Close case or escalate'
      ]
    },
    payment_plan: {
      name: 'Payment Plan Management',
      steps: [
        'Plan Setup - Define payment schedule',
        'Agreement - Customer signs payment plan',
        'Monitoring - Track payment compliance',
        'Reminder - Send payment due reminders',
        'Breach Handling - Address missed payments',
        'Completion - Close successful plan'
      ]
    }
  };

  const workflow = descriptions[workflowKey] || { name: workflowKey, steps: [] };

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-lg">{workflow.name}</h3>
      <ol className="space-y-2">
        {workflow.steps.map((step: string, index: number) => (
          <li key={index} className="flex items-start">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-capco-blue text-white text-sm mr-3 flex-shrink-0">
              {index + 1}
            </span>
            <span>{step}</span>
          </li>
        ))}
      </ol>
    </div>
  );
};

// Generate sample BPMN XML for demo purposes
function generateSampleBpmn(workflowKey: string): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                   xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                   xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                   xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                   id="Definitions_1"
                   targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="${workflowKey}" name="${workflowKey}" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Start">
      <bpmn:outgoing>Flow_1</bpmn:outgoing>
    </bpmn:startEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Task_1" />
    <bpmn:userTask id="Task_1" name="Initial Contact">
      <bpmn:incoming>Flow_1</bpmn:incoming>
      <bpmn:outgoing>Flow_2</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:sequenceFlow id="Flow_2" sourceRef="Task_1" targetRef="Task_2" />
    <bpmn:userTask id="Task_2" name="Follow Up">
      <bpmn:incoming>Flow_2</bpmn:incoming>
      <bpmn:outgoing>Flow_3</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:sequenceFlow id="Flow_3" sourceRef="Task_2" targetRef="Task_3" />
    <bpmn:userTask id="Task_3" name="Negotiate">
      <bpmn:incoming>Flow_3</bpmn:incoming>
      <bpmn:outgoing>Flow_4</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:sequenceFlow id="Flow_4" sourceRef="Task_3" targetRef="EndEvent_1" />
    <bpmn:endEvent id="EndEvent_1" name="End">
      <bpmn:incoming>Flow_4</bpmn:incoming>
    </bpmn:endEvent>
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="${workflowKey}">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent_1" bpmnElement="StartEvent_1">
        <dc:Bounds x="152" y="102" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_1_di" bpmnElement="Task_1">
        <dc:Bounds x="250" y="80" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_2_di" bpmnElement="Task_2">
        <dc:Bounds x="410" y="80" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_3_di" bpmnElement="Task_3">
        <dc:Bounds x="570" y="80" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndEvent_1_di" bpmnElement="EndEvent_1">
        <dc:Bounds x="732" y="102" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <di:waypoint x="188" y="120" />
        <di:waypoint x="250" y="120" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_2_di" bpmnElement="Flow_2">
        <di:waypoint x="350" y="120" />
        <di:waypoint x="410" y="120" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_3_di" bpmnElement="Flow_3">
        <di:waypoint x="510" y="120" />
        <di:waypoint x="570" y="120" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_4_di" bpmnElement="Flow_4">
        <di:waypoint x="670" y="120" />
        <di:waypoint x="732" y="120" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`;
}
