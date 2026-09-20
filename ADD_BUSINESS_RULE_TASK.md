# How to Add Business Rule Task in BPMN Editor

## Current Issue:
The BPMN editor's context menu doesn't show "Business Rule Task" option.

## Solution - Use the Palette:

### Method 1: From Left Palette (Recommended)
1. Look at the **left side** of the BPMN editor
2. Find the **palette** with all BPMN elements
3. Look for the **Business Rule Task** icon (table/grid icon)
4. **Drag it** onto the canvas

### Method 2: Change Existing Task Type
1. Add a regular "Service task" from the menu
2. Click on the task to select it
3. Click the **wrench icon** (🔧) that appears
4. Select **"Business rule task"** from the dropdown
5. This converts it to a Business Rule Task

### Method 3: Use Append Menu
1. Select an existing element
2. Click the **context pad** (circular menu around the element)
3. Click **"Append Task"**
4. From the dropdown, look for Business Rule Task

---

## Once You Have a Business Rule Task:

### To Configure the DMN Decision:

1. **Click on the Business Rule Task** (it will have a table icon)
2. Look for the **properties panel on the right**
3. Find these fields:
   - **Implementation**: Should say "DMN" or have DMN option
   - **Called Decision**: or "Decision Ref" field
   - Type the decision ID:
     - `complianceCheck`
     - `priorityScoring`
     - `contactStrategy`

4. **Result Variable**: Where to store the result
   - Example: `complianceResult`

---

## If Properties Panel Doesn't Appear:

The standard bpmn-js Modeler might not show all properties for Camunda 8.

### Alternative: Edit XML Directly

1. Get the XML from editor
2. Find the Business Rule Task element:
```xml
<bpmn:businessRuleTask id="Task_1" name="Check Compliance">
  <bpmn:extensionElements>
    <zeebe:calledDecision decisionId="complianceCheck" resultVariable="complianceResult" />
  </bpmn:extensionElements>
  <bpmn:incoming>Flow_1</bpmn:incoming>
  <bpmn:outgoing>Flow_2</bpmn:outgoing>
</bpmn:businessRuleTask>
```

3. Add the `zeebe:calledDecision` element with:
   - `decisionId`: The DMN decision ID
   - `resultVariable`: Variable name for the result

---

## Recommended: Use Camunda Desktop Modeler

For full Camunda 8 support with proper DMN integration:

1. Download **Camunda Modeler 8** from https://camunda.com/download/modeler/
2. Open your BPMN file
3. Add Business Rule Task
4. Properties panel will show all Camunda 8 specific fields
5. Save and upload to your system

---

**For now, try Method 2: Add Service Task → Change to Business Rule Task using wrench icon!**
