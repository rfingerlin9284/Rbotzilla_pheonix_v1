#!/bin/bash
# Dashboard Stop Script
# Cleanly shuts down all dashboard components

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${RED}${BOLD}  🛑 RICK Trading System - Dashboard Shutdown${NC}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Step 1: Stop the dashboard supervisor
echo -e "${BLUE}[1/3]${NC} Stopping dashboard supervisor..."
if [ -f .dashboard_supervisor.pid ]; then
    SUPERVISOR_PID=$(cat .dashboard_supervisor.pid)
    if ps -p $SUPERVISOR_PID > /dev/null; then
        kill $SUPERVISOR_PID
        echo -e "${GREEN}✓${NC} Dashboard supervisor stopped (PID: $SUPERVISOR_PID)"
    else
        echo -e "${YELLOW}⚠️${NC} Dashboard supervisor not running"
    fi
    rm .dashboard_supervisor.pid
else
    echo -e "${YELLOW}⚠️${NC} Dashboard supervisor PID file not found"
    # Try to find and kill any running dashboard supervisor
    SUPERVISOR_PID=$(ps aux | grep "dashboard_supervisor.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$SUPERVISOR_PID" ]; then
        kill $SUPERVISOR_PID
        echo -e "${GREEN}✓${NC} Dashboard supervisor stopped (PID: $SUPERVISOR_PID)"
    fi
fi

# Step 2: Stop the OANDA paper trading engine
echo -e "${BLUE}[2/3]${NC} Stopping OANDA paper trading engine..."
if [ -f .oanda_paper.pid ]; then
    OANDA_PID=$(cat .oanda_paper.pid)
    if ps -p $OANDA_PID > /dev/null; then
        kill $OANDA_PID
        echo -e "${GREEN}✓${NC} OANDA paper trading engine stopped (PID: $OANDA_PID)"
    else
        echo -e "${YELLOW}⚠️${NC} OANDA paper trading engine not running"
    fi
    rm .oanda_paper.pid
else
    echo -e "${YELLOW}⚠️${NC} OANDA paper trading engine PID file not found"
    # Try to find and kill any running OANDA trading engine
    OANDA_PID=$(ps aux | grep "oanda_trading_engine.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$OANDA_PID" ]; then
        kill $OANDA_PID
        echo -e "${GREEN}✓${NC} OANDA trading engine stopped (PID: $OANDA_PID)"
    fi
fi

# Step 3: Kill any remaining Python processes related to the dashboard
echo -e "${BLUE}[3/3]${NC} Cleaning up remaining processes..."
pkill -f "app.py" || true
pkill -f "dashboard/app.py" || true
echo -e "${GREEN}✓${NC} Cleanup complete"

echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}  ✅ All Dashboard Components Stopped${NC}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""