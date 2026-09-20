# 🔍 Decisions Are Deployed But Not Visible in UI

## Current Status

✅ **Decisions ARE deployed** - I can see them in Elasticsearch:
- Contact Strategy (key: 2251799813685251)
- Compliance Check (key: 2251799813685254)
- Priority Scoring (key: 2251799813685257)

✅ **Process IS visible** - You can see "Loan Collection Process"

❌ **Decisions tab shows nothing** - UI issue

---

## Why This Happens

Camunda Operate 8.7.0 requires **decision instances** (actual executions) to show decisions in the UI. The decisions are deployed, but you need to execute them first!

---

## ✅ Solution: Execute the Process

When you run the **Loan Collection Process**, it will call the DMN decisions, and then they'll appear in the Decisions tab!

### Steps:

1. **In Operate** (http://localhost:8080)
2. Click on **"Loan Collection Process"**
3. Click **"Start instance"** button (top right)
4. Enter variables:
   ```json
   {
     "currentHour": 14,
     "overdueDays": 95,
     "overdueAmount": 150000,
     "caseId": "TEST-001"
   }
   ```
5. Click **"Start"**

### What Will Happen:
- Process starts
- Calls **Compliance Check** decision
- Calls **Priority Scoring** decision
- After execution, go to **Decisions** tab
- You'll now see decision instances!

---

## Alternative: Test Decisions Directly

You can also execute decisions via API:

```bash
# Execute Compliance Check
curl -X POST http://localhost:8081/api/rules/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "decisionId": "complianceCheck",
    "variables": {"currentHour": 14}
  }'

# Execute Priority Scoring
curl -X POST http://localhost:8081/api/rules/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "decisionId": "priorityScoring",
    "variables": {
      "overdueDays": 95,
      "overdueAmount": 150000
    }
  }'
```

---

## 🎯 Quick Action

**Start a process instance now** and the decisions will appear in Operate after execution!

1. Go to: http://localhost:8080
2. Click "Loan Collection Process"
3. Click "Start instance"
4. Fill variables and start
5. Check "Decisions" tab after - they'll be there!

---

**Note**: In Camunda 8, the "Decisions" tab shows **decision instances** (executions), not just definitions. Once you execute workflows that call decisions, they appear!
