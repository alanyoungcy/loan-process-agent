#!/bin/bash
# Quick Status Check for Camunda 8.7 System

echo "🔍 Camunda 8.7 System Status Check"
echo "===================================="
echo ""

# Check Zeebe
echo "1. Zeebe (Workflow Engine):"
if curl -s http://localhost:9600/ready > /dev/null 2>&1; then
    echo "   ✅ READY - http://localhost:26500 (gRPC)"
else
    echo "   ⚠️  NOT READY - Check: docker logs loan-agent-zeebe"
fi

# Check Operate
echo ""
echo "2. Operate (Process Monitoring UI) - ESSENTIAL:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ | grep -q "302\|200"; then
    echo "   ✅ READY - http://localhost:8080"
    echo "   → This is your main UI to see workflows!"
else
    echo "   ⚠️  NOT READY - Check: docker logs loan-agent-operate"
fi

# Check Tasklist
echo ""
echo "3. Tasklist (Human Tasks UI):"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8082/ | grep -q "302\|200"; then
    echo "   ✅ READY - http://localhost:8082"
    echo "   → For manual tasks (if needed)"
else
    echo "   ⚠️  NOT READY - Check: docker logs loan-agent-tasklist"
fi

# Check Elasticsearch
echo ""
echo "4. Elasticsearch (Data Storage):"
if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
    echo "   ✅ READY - http://localhost:9200"
else
    echo "   ⚠️  NOT READY - Check: docker logs loan-agent-elasticsearch"
fi

# Check DMN Service
echo ""
echo "5. DMN Service (Rules Engine):"
if curl -s http://localhost:8081/api/rules/health > /dev/null 2>&1; then
    echo "   ✅ READY - http://localhost:8081"
else
    echo "   ⚠️  NOT READY - Check: docker logs loan-agent-camunda-dmn"
fi

echo ""
echo "===================================="
echo ""
echo "📊 Main Access Points:"
echo "   • Operate (Monitor Workflows): http://localhost:8080"
echo "   • Tasklist (Human Tasks):      http://localhost:8082"
echo ""
echo "🎯 What Each Does:"
echo "   • Zeebe:   Runs your workflows (engine)"
echo "   • Operate: See & manage workflows (essential UI)"
echo "   • Tasklist: Handle user tasks (if you have them)"
echo "   • DMN:     Execute decision rules"
echo ""
echo "📚 Documentation:"
echo "   • CAMUNDA_8_STATUS.md - Complete guide"
echo "   • CAMUNDA_8_README.md - Getting started"
echo ""
