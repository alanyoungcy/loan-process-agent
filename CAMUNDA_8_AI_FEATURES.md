# Camunda 8 AI Connectors Configuration

## OpenAI Connector

The OpenAI connector enables AI-powered decision-making in your workflows.

### Environment Variables

Add to your `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o

# Anthropic Claude Configuration (optional)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

### Usage in BPMN

1. **Service Task with OpenAI Connector**

```xml
<bpmn:serviceTask id="AIDecision" name="AI-Powered Decision">
  <bpmn:extensionElements>
    <zeebe:taskDefinition type="io.camunda:openai:1" />
    <zeebe:taskHeaders>
      <zeebe:header key="apiKey" value="${openai_api_key}" />
      <zeebe:header key="model" value="gpt-4o" />
      <zeebe:header key="temperature" value="0.7" />
    </zeebe:taskHeaders>
    <zeebe:ioMapping>
      <zeebe:input source="=caseData" target="messages" />
      <zeebe:output source="=result" target="aiDecision" />
    </zeebe:ioMapping>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

2. **DMN Decision with AI Enhancement**

Use AI to suggest decision table values:
- Analyze historical case outcomes
- Recommend optimal collection strategies
- Predict payment probability

## AI-Powered Features

### 1. Intelligent Process Optimization

Camunda Optimize 8.7 includes AI features:

- **Process Mining**: Discover bottlenecks automatically
- **Predictive Analytics**: Forecast case completion times
- **Smart Recommendations**: Suggest process improvements

Access at: `http://localhost:8083`

### 2. Natural Language to BPMN

Use the Camunda AI Assistant to:

```
"Create a loan collection workflow that:
1. Checks compliance rules
2. Calculates priority score
3. Assigns to appropriate collector
4. Sends automated reminders"
```

The AI will generate the BPMN diagram automatically.

### 3. AI Task Routing

```xml
<bpmn:serviceTask id="IntelligentAssignment" name="AI-Based Assignment">
  <bpmn:extensionElements>
    <zeebe:taskDefinition type="io.camunda:ai-assignment:1" />
    <zeebe:ioMapping>
      <zeebe:input source="=caseData" target="input" />
      <zeebe:input source="=collectorSkills" target="skills" />
      <zeebe:output source="=assignedCollector" target="collector" />
    </zeebe:ioMapping>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

### 4. Sentiment Analysis Connector

Analyze customer communication sentiment:

```xml
<bpmn:serviceTask id="SentimentAnalysis" name="Analyze Customer Sentiment">
  <bpmn:extensionElements>
    <zeebe:taskDefinition type="io.camunda:openai:sentiment:1" />
    <zeebe:ioMapping>
      <zeebe:input source="=customerTranscript" target="text" />
      <zeebe:output source="=sentiment" target="customerSentiment" />
      <zeebe:output source="=score" target="sentimentScore" />
    </zeebe:ioMapping>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

## Custom AI Connectors

### Creating Collection Strategy Connector

Create `/camunda-connectors/collection-strategy-connector.json`:

```json
{
  "name": "Collection Strategy Advisor",
  "id": "io.capco:collection-strategy:1",
  "version": 1,
  "description": "AI-powered collection strategy recommendations",
  "category": {
    "id": "connectors",
    "name": "Connectors"
  },
  "inputs": [
    {
      "id": "caseData",
      "label": "Case Data",
      "type": "Object",
      "binding": {
        "type": "zeebe:input",
        "name": "caseData"
      }
    }
  ],
  "outputs": [
    {
      "id": "strategy",
      "label": "Recommended Strategy",
      "type": "String",
      "binding": {
        "type": "zeebe:output",
        "source": "=strategy"
      }
    },
    {
      "id": "confidence",
      "label": "Confidence Score",
      "type": "Number",
      "binding": {
        "type": "zeebe:output",
        "source": "=confidence"
      }
    }
  ]
}
```

## AI-Enhanced Decision Tables

### Example: Smart Priority Scoring

Use AI to enhance DMN decisions:

```xml
<decision id="SmartPriorityScoring" name="AI-Enhanced Priority Scoring">
  <decisionTable hitPolicy="FIRST">
    <input id="historicalData" label="Historical Success Rate">
      <inputExpression typeRef="number">
        <text>historicalSuccessRate</text>
      </inputExpression>
    </input>
    <input id="aiPrediction" label="AI Predicted Outcome">
      <inputExpression typeRef="number">
        <text>aiPaymentProbability</text>
      </inputExpression>
    </input>
    <output id="priority" label="Priority" typeRef="integer" />
    
    <rule>
      <inputEntry>
        <text>&gt;= 0.7</text>
      </inputEntry>
      <inputEntry>
        <text>&gt;= 0.8</text>
      </inputEntry>
      <outputEntry>
        <text>10</text>
      </outputEntry>
    </rule>
  </decisionTable>
</decision>
```

## Monitoring AI Performance

Access Camunda Optimize to:

1. **Track AI Accuracy**
   - Compare AI predictions vs actual outcomes
   - Monitor confidence scores
   - Identify drift in model performance

2. **A/B Testing**
   - Test AI-driven strategies vs traditional rules
   - Measure impact on collection rates
   - Automatically select winning approach

3. **Continuous Learning**
   - Feed outcomes back to AI models
   - Retrain based on new data
   - Improve predictions over time

## Best Practices

1. **Use AI for Complex Decisions**: Let AI handle nuanced cases
2. **Keep Humans in the Loop**: Use AI for recommendations, not final decisions
3. **Monitor Performance**: Track AI accuracy and adjust thresholds
4. **Fallback to Rules**: Always have rule-based fallbacks
5. **Explain Decisions**: Log AI reasoning for compliance

## Example: Complete AI-Enhanced Workflow

See `/camunda-deployments/ai-enhanced-collection.bpmn` for a complete example integrating:
- AI-powered case assessment
- Intelligent priority scoring
- Automated strategy selection
- Sentiment-based communication
- Predictive outcome forecasting

## Troubleshooting

### Connector Not Available
```bash
# Check connectors service
docker logs loan-agent-connectors

# Verify API key is set
docker exec loan-agent-connectors env | grep OPENAI
```

### AI Predictions Failing
- Check API key validity
- Monitor rate limits
- Review input data format
- Check connector logs
