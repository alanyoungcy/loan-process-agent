#!/bin/bash

# Loan Agent - Restart Script
# This script restarts all services for the Loan Agent system

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🔄 Restarting Loan Agent System${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Stop the system
cd "$PROJECT_ROOT/scripts"
./stop.sh

echo ""
echo -e "${BLUE}⏳ Waiting 3 seconds before restart...${NC}"
sleep 3
echo ""

# Start the system
./start.sh
