# How to Connect Business Rule Task to DMN Decision

## In BPMN Editor:

### Step 1: Add Business Rule Task
1. Open BPMN workflow in designer
2. Drag "Business Rule Task" from palette onto canvas
3. Click on the task to select it

### Step 2: Configure the Task
In the properties panel on the right:

1. **Task Type**: Should be "Business Rule Task" (automatically set)

2. **Implementation**: Select "DMN"

3. **Decision Ref**: Enter the DMN decision ID
   - For Compliance Check: `complianceCheck`
   - For Priority Scoring: `priorityScoring`
   - For Contact Strategy: `contactStrategy`

4. **Result Variable**: Name to store the result
   - Example: `complianceResult`
   - This variable will be available in later tasks

### Step 3: Map Inputs (Optional)
Configure input variables that the DMN needs:
- Click "Input/Output" tab
- Add input mappings from process variables

### Step 4: Deploy
Click "🚀 Deploy to Camunda"

---

## Example Configuration:

### Compliance Check Task:
```
Name: Check Compliance
Type: Business Rule Task
Implementation: DMN
Decision Ref: complianceCheck
Result Variable: complianceResult
```

### Using the Result:
In subsequent tasks or gateways:
```
Condition: = complianceResult.canContact = true
```

---

## All Available DMN Decisions:

1. **complianceCheck**
   - Inputs: currentHour, dailyContactCount, currentDay, riskLevel
   - Outputs: canContact, violation, recommendation, tag

2. **priorityScoring**
   - Inputs: overdueDays, overdueAmount
   - Outputs: priority, urgencyLevel

3. **contactStrategy**
   - Inputs: overdueDays
   - Outputs: channel, timing

---

## Visual Guide:

```
[Start Event]
      ↓
[Business Rule Task] ← Decision Ref: "complianceCheck"
   (Compliance Check)    Result Variable: "complianceResult"
      ↓
[Exclusive Gateway] ← Condition: = complianceResult.canContact = true
  /         \
Yes         No
```

---

**Try it now in your BPMN designer!** 🚀
