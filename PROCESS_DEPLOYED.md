# ✅ Sample Workflow Deployed!

## 🎯 Now You Can See Processes in Operate

I just deployed a **Loan Collection Workflow** to Camunda!

---

## 📊 View Your Process

1. **Open Camunda Operate**: http://localhost:8080
2. Click **"Processes"** in the left sidebar (not Decisions)
3. You should now see: **"Loan Collection Process"**

---

## 🔄 What This Workflow Does

**Process**: Loan Collection Process

**Steps**:
1. **Start** - New overdue case
2. **Check Compliance** - Calls compliance DMN decision
3. **Calculate Priority** - Calls priority DMN decision  
4. **Determine Strategy** - Service task (needs worker)
5. **Send Notification** - Service task (needs worker)
6. **End** - Case processed

---

## 🚀 Start a Process Instance

To see the workflow in action:

```bash
zbctl create instance loan-collection-process \
  --variables '{"currentHour": 14, "overdueDays": 95, "overdueAmount": 150000}' \
  --address localhost:26500 \
  --insecure
```

Or use Operate UI:
1. Click on "Loan Collection Process"
2. Click "Start instance" button
3. Enter variables
4. Watch it execute!

---

## 📚 What You'll See in Operate

### Processes Tab
- **Loan Collection Process** - Your deployed workflow
- Click it to see the BPMN diagram
- Start instances and watch them flow

### Decisions Tab
- **Compliance Check**
- **Priority Scoring**
- **Contact Strategy**

---

## 🎨 Create More Workflows

Use your visual BPMN editor:
1. Go to http://localhost:5173/workflows/designer
2. Click **"BPMN Workflows"** tab
3. Drag & drop elements
4. Click **"🚀 Deploy to Camunda"**
5. See it appear in Operate!

---

**Now refresh Operate and click "Processes" - you'll see your workflow!** 🎉
