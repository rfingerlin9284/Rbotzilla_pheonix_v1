#!/bin/bash
# Complete Dashboard Launcher
# Connects all components: Dashboard, OANDA API, and Narration

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}  🤖 RICK Trading System - Complete Dashboard Launcher${NC}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Step 1: Create logs directory if it doesn't exist
echo -e "${BLUE}[1/6]${NC} Creating logs directory..."
mkdir -p logs
echo -e "${GREEN}✓${NC} Logs directory ready"

# Step 2: Generate test narration entries
echo -e "${BLUE}[2/6]${NC} Generating test narration entries..."
python3 test_narration.py
echo -e "${GREEN}✓${NC} Narration entries created"

# Step 3: Start the dashboard supervisor in the background
echo -e "${BLUE}[3/6]${NC} Starting dashboard supervisor..."
python3 dashboard_supervisor.py > logs/dashboard_supervisor.log 2>&1 &
SUPERVISOR_PID=$!
echo $SUPERVISOR_PID > .dashboard_supervisor.pid
echo -e "${GREEN}✓${NC} Dashboard supervisor started (PID: $SUPERVISOR_PID)"

# Step 4: Wait for supervisor to initialize
echo -e "${BLUE}[4/6]${NC} Waiting for supervisor initialization..."
sleep 3
echo -e "${GREEN}✓${NC} Supervisor initialized"

# Step 5: Start the OANDA paper trading engine
echo -e "${BLUE}[5/6]${NC} Starting OANDA paper trading engine..."
./start_paper_NOW.sh > logs/oanda_paper.log 2>&1 &
OANDA_PID=$!
echo $OANDA_PID > .oanda_paper.pid
echo -e "${GREEN}✓${NC} OANDA paper trading engine started (PID: $OANDA_PID)"

# Step 6: Launch the web browser dashboard
echo -e "${BLUE}[6/6]${NC} Launching web dashboard..."
sleep 2

# Try different browsers
if command -v firefox &> /dev/null; then
    firefox http://localhost:8080 &
elif command -v google-chrome &> /dev/null; then
    google-chrome http://localhost:8080 &
elif command -v chromium &> /dev/null; then
    chromium http://localhost:8080 &
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8080 &
else
    echo -e "${YELLOW}⚠️ No browser found. Please open manually:${NC}"
    echo -e "   http://localhost:8080"
fi

echo -e "${GREEN}✓${NC} Dashboard launched!"
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}  🎉 Complete Dashboard System Running${NC}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Dashboard URL:${NC} http://localhost:8080"
echo -e "${YELLOW}Arena Test:${NC} http://localhost:8080/arena-test"
echo -e "${YELLOW}Narration File:${NC} narration.jsonl"
echo ""
echo -e "${BLUE}To stop all components:${NC}"
echo -e "  ./stop_dashboard.sh"
echo ""
echo -e "${RED}NOTE:${NC} If the dashboard doesn't load, try running these commands separately:"
echo -e "  1. python3 dashboard/app.py"
echo -e "  2. In another terminal: ./start_paper_NOW.sh"
echo ""