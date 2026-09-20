# Task #23: Integrate DMN Editor Contextually into BPMN

## Goal
When user clicks a Business Rule Task in the BPMN editor, open the DMN editor in a modal/sidebar to edit the decision table inline.

## Why This is Important
- DMN decisions are part of BPMN workflows
- Business Rule Tasks call specific DMN decisions
- Editing them contextually makes sense
- No need for separate DMN tab

## Implementation Approach

### 1. Detect Business Rule Task Click
In `VisualBpmnEditor.tsx`:
```typescript
modeler.on('element.click', (event) => {
  const element = event.element;
  if (element.type === 'bpmn:BusinessRuleTask') {
    // Get the decision ID from the task properties
    const decisionId = element.businessObject.decisionRef;
    openDmnEditor(decisionId);
  }
});
```

### 2. Create DMN Modal Component
```typescript
<DmnEditorModal
  isOpen={dmnModalOpen}
  decisionId={selectedDecisionId}
  onClose={() => setDmnModalOpen(false)}
  onSave={(updatedDmn) => saveDmnChanges(updatedDmn)}
/>
```

### 3. Load Decision Table
- Fetch DMN XML for the specific decision
- Load into DMN modeler in modal
- Allow inline editing

### 4. Save Back
- Save updated DMN
- Deploy to Camunda
- Update workflow if needed

## Complexity
This is a **medium-large** task requiring:
- Event listening in bpmn-js
- Modal/sidebar UI component
- DMN editor integration
- Save/deploy flow

## Priority
**Optional** - Nice to have but not essential.

Current workaround:
- Users can edit DMN files separately
- Deploy them alongside BPMN
- Works fine, just not as integrated

## Recommendation
**Defer to future sprint** - System is fully functional without this.
Focus on using what we have now.
