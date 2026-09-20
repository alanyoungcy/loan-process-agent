# AI Features Integration Guide

## Quick Start

This guide shows you how to integrate the four AI features into your loan collection system.

---

## 1. Installation & Setup

### Install Dependencies (if needed)

```bash
cd loan-agent-frontend
npm install axios recharts lucide-react
```

### Import Components

```typescript
// In your React components
import { ChatbotWidget } from '@/components/ai/ChatbotWidget';
import { MultiAgentDebate } from '@/components/ai/MultiAgentDebate';
import { TrustGateBadge, TrustGateStatus } from '@/components/ai/TrustGateBadge';
import { ABTestDashboard } from '@/components/ai/ABTestDashboard';
import { AICommandCenter } from '@/components/dashboard/AICommandCenter';
import aiServices from '@/services/aiServices';
```

---

## 2. Feature Integration Examples

### A. Case Detail Page - Full Integration

```typescript
// pages/cases/CaseDetailPage.tsx

import React, { useState } from 'react';
import { ChatbotWidget } from '@/components/ai/ChatbotWidget';
import { MultiAgentDebate } from '@/components/ai/MultiAgentDebate';
import { TrustGateStatus } from '@/components/ai/TrustGateBadge';

export const CaseDetailPage = ({ caseId }) => {
  const [showChatbot, setShowChatbot] = useState(false);
  const [showDebate, setShowDebate] = useState(false);
  const [caseData, setCaseData] = useState(null);

  // Load case data
  useEffect(() => {
    fetchCaseData(caseId).then(setCaseData);
  }, [caseId]);

  return (
    <div className="space-y-6">
      {/* Case Header */}
      <div className="flex justify-between items-center">
        <h1>Case {caseId}</h1>
        <div className="flex gap-2">
          <Button onClick={() => setShowChatbot(true)}>
            💬 Start Customer Chat
          </Button>
          <Button onClick={() => setShowDebate(true)}>
            🧠 Get AI Strategy
          </Button>
        </div>
      </div>

      {/* Case Info */}
      <Card>
        <h2>Case Information</h2>
        <div>Amount: ${caseData?.overdue_amount}</div>
        <div>Days Overdue: {caseData?.overdue_days}</div>
      </Card>

      {/* AI Strategy Debate */}
      {showDebate && (
        <MultiAgentDebate
          caseId={caseId}
          caseData={{
            overdue_amount: caseData?.overdue_amount,
            overdue_days: caseData?.overdue_days,
            status: caseData?.status,
            priority: caseData?.priority,
          }}
          onAccept={(consensus) => {
            // Apply the recommended strategy
            console.log('Accepted strategy:', consensus);
            applyStrategy(caseId, consensus);
            setShowDebate(false);
          }}
          onReject={() => setShowDebate(false)}
        />
      )}

      {/* Chatbot Widget */}
      {showChatbot && (
        <ChatbotWidget
          caseId={caseId}
          onClose={() => setShowChatbot(false)}
        />
      )}
    </div>
  );
};
```

### B. Generate Collection Script with Trust Gate

```typescript
// Example: Generate and validate a collection email

import { genaiService, trustGateService } from '@/services/aiServices';

const generateAndValidateScript = async (caseData) => {
  // Step 1: Generate script
  const scriptResult = await genaiService.generateScript(
    caseData,
    'email',
    {
      customer_segment: 'standard',
      previous_interactions: []
    }
  );

  console.log('Generated Script:', scriptResult.script);
  console.log('Compliance Status:', scriptResult.compliance_status);

  // Step 2: Trust Gate evaluation (automatic in backend, but can check)
  const trustEvaluation = await trustGateService.evaluateAction(
    scriptResult,
    {
      case_id: caseData.case_id,
      overdue_amount: caseData.overdue_amount,
      overdue_days: caseData.overdue_days,
    }
  );

  // Step 3: Display with Trust Gate badge
  return (
    <div>
      <h3>Generated Email Script</h3>
      <div className="p-4 bg-gray-50 rounded">
        {scriptResult.script}
      </div>
      
      <TrustGateStatus
        evaluation={trustEvaluation}
        actionType="Email Script"
        showPipeline={true}
      />

      {trustEvaluation.decision === 'auto_execute' && (
        <Button onClick={() => sendEmail(scriptResult.script)}>
          Send Email
        </Button>
      )}
      
      {trustEvaluation.requires_review && (
        <Button onClick={() => requestHumanReview(scriptResult, trustEvaluation)}>
          Submit for Review
        </Button>
      )}
    </div>
  );
};
```

### C. A/B Testing Integration

```typescript
// Example: Assign variant and track outcome

import { abTestingService } from '@/services/aiServices';

const handleCaseAssignment = async (caseId) => {
  // Check if there's an active experiment
  const experiments = await abTestingService.listExperiments('active');
  
  if (experiments.length > 0) {
    const experiment = experiments[0]; // e.g., "Email Timing Test"
    
    // Assign variant
    const variant = await abTestingService.assignVariant(
      experiment.name,
      caseId
    );
    
    console.log(`Case ${caseId} assigned to ${variant} variant`);
    
    // Use appropriate strategy based on variant
    if (variant === 'treatment') {
      // Send morning email (9 AM)
      await scheduleEmail(caseId, '09:00');
    } else {
      // Send evening email (7 PM)
      await scheduleEmail(caseId, '19:00');
    }
    
    // Later, track outcome
    const paymentReceived = await checkPaymentStatus(caseId);
    
    await abTestingService.trackOutcome(
      experiment.name,
      caseId,
      { payment_amount: paymentReceived.amount },
      paymentReceived.success
    );
  }
};
```

### D. Chatbot Embedded in Customer Portal

```typescript
// CustomerPortal.tsx - Customer-facing page

export const CustomerPortal = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <header>
        <h1>Payment Center</h1>
      </header>

      <main className="container mx-auto p-6">
        <Card>
          <h2>Your Account</h2>
          {/* Account details */}
        </Card>

        {/* Embedded Chatbot */}
        <div className="mt-6">
          <ChatbotWidget
            embedded={true}
            caseId={userCaseId}
          />
        </div>
      </main>
    </div>
  );
};
```

### E. AI Command Center Dashboard

```typescript
// Dashboard.tsx - Main monitoring dashboard

import { AICommandCenter } from '@/components/dashboard/AICommandCenter';

export const Dashboard = () => {
  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <StatsOverview />

      {/* AI Command Center */}
      <AICommandCenter />

      {/* Other dashboard sections */}
      <CasesOverview />
      <PerformanceMetrics />
    </div>
  );
};
```

---

## 3. Complete Workflow Example

### End-to-End Collection Process with All AI Features

```typescript
// CompleteCollectionWorkflow.tsx

const CollectionWorkflow = ({ caseId }) => {
  const [step, setStep] = useState(1);
  const [debateResult, setDebateResult] = useState(null);
  const [scriptResult, setScriptResult] = useState(null);
  const [trustEvaluation, setTrustEvaluation] = useState(null);

  // Step 1: Run Multi-Agent Debate
  const runStrategyDebate = async () => {
    const result = await multiAgentService.runDebate(caseId);
    setDebateResult(result);
    setStep(2);
  };

  // Step 2: Generate Script Based on Strategy
  const generateScript = async () => {
    const script = await genaiService.generateScript(
      caseData,
      'email',
      { strategy: debateResult.consensus.strategy }
    );
    setScriptResult(script);
    
    // Automatic Trust Gate evaluation
    const evaluation = await trustGateService.evaluateAction(
      script,
      { case_id: caseId }
    );
    setTrustEvaluation(evaluation);
    setStep(3);
  };

  // Step 3: Execute or Review
  const executeAction = async () => {
    if (trustEvaluation.decision === 'auto_execute') {
      // A/B test assignment
      const variant = await abTestingService.assignVariant(
        'email-script-test',
        caseId
      );
      
      // Send email
      await sendEmail(caseId, scriptResult.script);
      
      setStep(4);
    } else {
      // Queue for human review
      await queueForReview(caseId, scriptResult, trustEvaluation);
    }
  };

  return (
    <div className="space-y-6">
      {/* Progress Indicator */}
      <div className="flex items-center justify-between">
        <StepIndicator active={step >= 1}>1. Strategy Debate</StepIndicator>
        <StepIndicator active={step >= 2}>2. Generate Script</StepIndicator>
        <StepIndicator active={step >= 3}>3. Trust Gate</StepIndicator>
        <StepIndicator active={step >= 4}>4. Execute</StepIndicator>
      </div>

      {/* Step 1: Multi-Agent Debate */}
      {step === 1 && (
        <MultiAgentDebate
          caseId={caseId}
          onAccept={(consensus) => {
            setDebateResult({ consensus });
            generateScript();
          }}
        />
      )}

      {/* Step 2: Script Generation */}
      {step === 2 && (
        <div>
          <h3>Generating Script...</h3>
          {/* Loading indicator */}
        </div>
      )}

      {/* Step 3: Trust Gate Evaluation */}
      {step === 3 && trustEvaluation && (
        <div>
          <h3>Generated Email Script</h3>
          <div className="bg-white p-4 rounded border mb-4">
            {scriptResult.script}
          </div>

          <TrustGateStatus
            evaluation={trustEvaluation}
            actionType="Email"
            showPipeline={true}
          />

          <div className="mt-4">
            {trustEvaluation.decision === 'auto_execute' ? (
              <Button onClick={executeAction} className="bg-green-600">
                ✅ Send Email
              </Button>
            ) : (
              <Button onClick={executeAction} className="bg-yellow-600">
                📋 Submit for Review
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Step 4: Success */}
      {step === 4 && (
        <div className="text-center p-8 bg-green-50 rounded">
          <h3 className="text-2xl font-bold text-green-600 mb-2">
            ✓ Action Completed
          </h3>
          <p>Email sent successfully and outcome tracking initiated.</p>
        </div>
      )}
    </div>
  );
};
```

---

## 4. Backend API Endpoints

Ensure these endpoints are implemented in your FastAPI backend:

### Chatbot Endpoints
```
POST   /api/v1/chatbot/session          - Create new chat session
POST   /api/v1/chatbot/message          - Send message
GET    /api/v1/chatbot/session/{id}/summary
POST   /api/v1/chatbot/session/{id}/takeover
```

### Multi-Agent Endpoints
```
POST   /api/v1/multi-agent/debate       - Run debate
GET    /api/v1/multi-agent/debates/{case_id}
POST   /api/v1/multi-agent/debates/{id}/accept
```

### Trust Gate Endpoints
```
POST   /api/v1/trust-gate/evaluate      - Evaluate action
GET    /api/v1/trust-gate/history/{case_id}
POST   /api/v1/trust-gate/{id}/override
```

### A/B Testing Endpoints
```
POST   /api/v1/experiments               - Create experiment
GET    /api/v1/experiments               - List experiments
GET    /api/v1/experiments/{name}        - Get experiment
GET    /api/v1/experiments/{name}/results
POST   /api/v1/experiments/{name}/stop
POST   /api/v1/experiments/{name}/promote
POST   /api/v1/experiments/{name}/assign
POST   /api/v1/experiments/{name}/outcome
```

### AI Metrics Endpoints
```
GET    /api/v1/ai/metrics                - Overview metrics
GET    /api/v1/ai/active-sessions        - Active sessions
GET    /api/v1/ai/performance-trends     - Trends data
```

---

## 5. Backend API Implementation Example

```python
# loan-agent-backend/app/api/v1/ai.py

from fastapi import APIRouter, Depends
from app.services.chatbot.collection_chatbot import get_chatbot
from app.services.multi_agent.debate import get_multi_agent_debate
from app.services.trust_gate import get_trust_gate
from app.services.ab_testing.experiment import ABTestService

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/metrics")
async def get_ai_metrics():
    """Get AI system overview metrics"""
    # Aggregate metrics from all AI services
    return {
        "chatbot": {
            "sessions_24h": 247,
            "resolution_rate": 0.89,
            "avg_duration_minutes": 2.3
        },
        "multi_agent": {
            "debates_24h": 43,
            "avg_confidence": 0.87,
            "acceptance_rate": 0.92
        },
        "trust_gate": {
            "approval_rate": 0.98,
            "reviews_pending": 12,
            "blocked_count": 0
        },
        "ab_testing": {
            "active_experiments": 2,
            "experiments_concluding": 1,
            "overall_success_rate": 0.89
        },
        "ai_actions": {
            "executed_24h": 156,
            "reviewed_24h": 23,
            "accuracy": 0.94
        },
        "alerts": {
            "pending": 3,
            "critical": 0
        }
    }

@router.get("/active-sessions")
async def get_active_sessions():
    """Get currently active AI sessions"""
    # Query active chatbot sessions, debates, etc.
    return [
        {
            "id": "CHT-12345",
            "type": "chatbot",
            "case_id": "CS-2024-5678",
            "status": "Intent: payment | Sentiment: positive | Duration: 2m 15s",
            "metadata": {},
            "trust_gate": {
                "decision": "auto_execute",
                "risk_level": "low"
            }
        }
    ]
```

---

## 6. Testing

### Test Chatbot
```bash
# Start backend
cd loan-agent-backend
python -m uvicorn app.main:app --reload

# Test chatbot endpoint
curl -X POST http://localhost:8000/api/v1/chatbot/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to make a payment",
    "case_id": "CS-2024-1234"
  }'
```

### Test Multi-Agent Debate
```bash
curl -X POST http://localhost:8000/api/v1/multi-agent/debate \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "CS-2024-1234",
    "context": {
      "overdue_amount": 25000,
      "overdue_days": 45
    },
    "debate_rounds": 2
  }'
```

---

## 7. Deployment Checklist

- [ ] Environment variables configured (OpenAI/Anthropic API keys)
- [ ] Database migrations run
- [ ] Redis cache configured
- [ ] All AI service endpoints deployed
- [ ] Frontend environment variables set
- [ ] WebSocket support enabled (for real-time chat)
- [ ] Monitoring and logging configured
- [ ] Rate limiting configured for API endpoints
- [ ] Backup strategy for experiment data

---

## 8. Monitoring & Debugging

### View Logs
```bash
# Backend logs
tail -f logs/ai-services.log

# Check Trust Gate decisions
grep "Trust Gate" logs/ai-services.log | tail -20
```

### Monitor Performance
- Check AI Command Center dashboard
- Review Trust Gate approval rates
- Monitor A/B test progress
- Track chatbot resolution rates

---

## 9. Best Practices

1. **Always use Trust Gate** for AI-generated content before sending to customers
2. **Run debates for high-value cases** (>$50k or complex situations)
3. **A/B test new strategies** before rolling out broadly
4. **Monitor chatbot takeover rate** - high rate indicates issues
5. **Review blocked actions** regularly to improve Trust Gate thresholds
6. **Archive completed experiments** to keep dashboard clean
7. **Set up alerts** for critical Trust Gate blocks

---

## 10. Troubleshooting

### Chatbot not responding
- Check LLM API keys in `.env`
- Verify backend is running
- Check browser console for errors
- Test API endpoint directly with curl

### Trust Gate always blocking
- Review risk factor thresholds in `trust_gate.py`
- Check if compliance rules are too strict
- Verify case data is complete

### A/B test not assigning variants
- Ensure experiment status is "active"
- Check if sample size target reached
- Verify case_id format is correct

---

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review API documentation at `/docs`
3. Check Trust Gate decision reasoning
4. Review AI metrics dashboard for patterns

---

**Ready to use!** Start with the AI Command Center dashboard to monitor everything in one place.
