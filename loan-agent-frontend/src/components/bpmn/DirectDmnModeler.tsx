/**
 * DMN Modeler using direct script approach
 * Based on https://bpmn.io/toolkit/dmn-js/
 */

import React, { useEffect, useRef, useState } from 'react';
import { Button } from '../ui/Button';

interface DirectDmnModelerProps {
  height?: string;
}

const DirectDmnModelerComponent: React.FC<DirectDmnModelerProps> = ({
  height = '700px',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const modelerRef = useRef<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load dmn-js from CDN
    const loadDmnJS = () => {
      return new Promise((resolve, reject) => {
        // Check if already loaded
        if (window.DmnJS) {
          resolve(window.DmnJS);
          return;
        }

        const script = document.createElement('script');
        script.src = 'https://unpkg.com/dmn-js@16.0.0/dist/dmn-modeler.development.js';
        script.onload = () => resolve(window.DmnJS);
        script.onerror = reject;
        document.head.appendChild(script);

        // Load CSS
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/dmn-js@16.0.0/dist/assets/dmn-js-drd.css';
        document.head.appendChild(link);

        const link2 = document.createElement('link');
        link2.rel = 'stylesheet';
        link2.href = 'https://unpkg.com/dmn-js@16.0.0/dist/assets/dmn-js-decision-table.css';
        document.head.appendChild(link2);

        const link3 = document.createElement('link');
        link3.rel = 'stylesheet';
        link3.href = 'https://unpkg.com/dmn-js@16.0.0/dist/assets/dmn-js-literal-expression.css';
        document.head.appendChild(link3);

        const link4 = document.createElement('link');
        link4.rel = 'stylesheet';
        link4.href = 'https://unpkg.com/dmn-js@16.0.0/dist/assets/diagram-js.css';
        document.head.appendChild(link4);

        const link5 = document.createElement('link');
        link5.rel = 'stylesheet';
        link5.href = 'https://unpkg.com/dmn-js@16.0.0/dist/assets/dmn-font/css/dmn-embedded.css';
        document.head.appendChild(link5);
      });
    };

    const initModeler = async () => {
      if (!containerRef.current) return;

      try {
        console.log('Loading dmn-js from CDN...');
        setLoading(true);

        const DmnJS = await loadDmnJS();
        console.log('dmn-js loaded successfully');

        const modeler = new DmnJS({
          container: containerRef.current,
          drd: {
            propertiesPanel: {},
          },
        });

        modelerRef.current = modeler;

        // Create empty DMN
        const emptyDmn = `<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/"
             xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/"
             xmlns:dc="http://www.omg.org/spec/DD/20100524/DC/"
             id="collection_rules"
             name="Collection Rules"
             namespace="http://capco.com/dmn">
  <decision id="strategy_decision" name="Collection Strategy">
    <decisionTable id="strategy_table">
      <input id="input_1" label="Overdue Days">
        <inputExpression id="expr_1" typeRef="number">
          <text>overdue_days</text>
        </inputExpression>
      </input>
      <input id="input_2" label="Amount">
        <inputExpression id="expr_2" typeRef="number">
          <text>amount</text>
        </inputExpression>
      </input>
      <output id="output_1" label="Strategy" name="strategy" typeRef="string" />
      <rule id="rule_1">
        <inputEntry><text>&lt; 30</text></inputEntry>
        <inputEntry><text>-</text></inputEntry>
        <outputEntry><text>"SMS"</text></outputEntry>
      </rule>
      <rule id="rule_2">
        <inputEntry><text>[30..90]</text></inputEntry>
        <inputEntry><text>&lt; 10000</text></inputEntry>
        <outputEntry><text>"Call"</text></outputEntry>
      </rule>
      <rule id="rule_3">
        <inputEntry><text>&gt; 90</text></inputEntry>
        <inputEntry><text>-</text></inputEntry>
        <outputEntry><text>"Legal"</text></outputEntry>
      </rule>
    </decisionTable>
  </decision>
</definitions>`;

        await modeler.importXML(emptyDmn);
        console.log('DMN imported successfully');

        setLoading(false);
      } catch (err) {
        console.error('Error initializing DMN modeler:', err);
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
  }, []);

  const handleSave = async () => {
    if (!modelerRef.current) return;

    try {
      const { xml } = await modelerRef.current.saveXML({ format: true });
      console.log('Saved DMN:', xml);

      // Download file
      const blob = new Blob([xml], { type: 'application/xml' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'collection-strategy.dmn';
      a.click();
      window.URL.revokeObjectURL(url);

      alert('✅ DMN saved and downloaded!');
    } catch (err) {
      alert('❌ Failed to save: ' + err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center bg-white rounded-lg border border-gray-200 p-8" style={{ height }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading DMN Modeler from CDN...</p>
          <p className="text-sm text-gray-500 mt-2">This may take a few seconds</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center bg-red-50 rounded-lg border border-red-200 p-8" style={{ height }}>
        <div className="text-center">
          <p className="text-red-600 font-semibold mb-2">Failed to load DMN Modeler</p>
          <p className="text-sm text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dmn-direct-modeler">
      {/* Toolbar */}
      <div className="flex justify-between items-center p-4 bg-gray-50 border-b border-gray-200 mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          ✨ Visual DMN Decision Table Editor
        </h3>
        <Button onClick={handleSave} variant="primary">
          💾 Save & Download DMN
        </Button>
      </div>

      {/* Modeler Container */}
      <div
        ref={containerRef}
        style={{
          height,
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          backgroundColor: '#ffffff',
        }}
      />

      {/* Help */}
      <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-900">
          💡 <strong>Tip:</strong> Click on cells to edit rules. Right-click to add/remove rows and columns.
          Double-click inputs/outputs to rename them.
        </p>
      </div>
    </div>
  );
};

// Extend Window interface for TypeScript
declare global {
  interface Window {
    DmnJS: any;
  }
}

export default DirectDmnModelerComponent;
