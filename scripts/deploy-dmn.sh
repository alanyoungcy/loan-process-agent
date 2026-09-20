#!/bin/bash
# Deploy DMN files to Camunda 8 Zeebe
# Uses zbctl (Zeebe CLI) or backend API

echo "🚀 Deploying DMN files to Camunda 8..."
echo ""

DMN_DIR="/Volumes/Orico/code/capco/loan-agent/camunda-deployments"

# Check if files exist
if [ ! -d "$DMN_DIR" ]; then
    echo "❌ DMN directory not found: $DMN_DIR"
    exit 1
fi

DMN_FILES=$(ls $DMN_DIR/*.dmn 2>/dev/null)
if [ -z "$DMN_FILES" ]; then
    echo "❌ No DMN files found in $DMN_DIR"
    exit 1
fi

echo "📋 Found DMN files:"
for file in $DMN_FILES; do
    echo "   • $(basename $file)"
done
echo ""

# Deploy via backend API
echo "⏳ Deploying via backend API..."
echo ""

for file in $DMN_FILES; do
    filename=$(basename $file)
    echo -n "   Deploying $filename... "

    # Read file content
    xml_content=$(cat "$file")

    # Deploy via backend API
    response=$(curl -s -X POST "http://localhost:8000/api/v1/workflows/dmn-deploy" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"$filename\", \"xml\": $(jq -Rs . <<< "$xml_content")}" \
        2>&1)

    if [ $? -eq 0 ]; then
        echo "✅"
    else
        echo "⚠️ (backend may need endpoint)"
    fi
done

echo ""
echo "📊 Alternative: Deploy manually via Operate UI"
echo ""
echo "1. Open Camunda Operate: http://localhost:8080"
echo "2. Login (if needed): demo/demo"
echo "3. Click 'Processes' or 'Decisions'"
echo "4. Look for 'Deploy' or 'Upload' button"
echo "5. Upload files from: $DMN_DIR"
echo ""
echo "🎯 Or use the visual DMN editor:"
echo "   → http://localhost:5173/workflows/designer"
echo "   → DMN tab → Open existing DMN → Deploy"
echo ""
