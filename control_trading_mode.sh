#!/bin/bash
# Control script for switching between PAPER and LIVE trading modes

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
function show_usage {
    echo -e "${BLUE}RICK Trading System - Mode Control${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  status      - Show current trading mode status"
    echo "  paper       - Switch to PAPER mode (api=true)"
    echo "  live        - Switch to LIVE mode (api=false)"
    echo "  restart     - Restart the trading engine"
    echo "  help        - Show this help message"
    echo ""
}

# Function to check if trading engine is running
function check_engine_status {
    if [ -f .trading_engine.pid ]; then
        PID=$(cat .trading_engine.pid)
        if ps -p $PID > /dev/null; then
            echo -e "${GREEN}Trading engine is running (PID: $PID)${NC}"
            return 0
        else
            echo -e "${YELLOW}Trading engine is not running (stale PID file)${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}Trading engine is not running (no PID file)${NC}"
        return 1
    fi
}

# Function to show current mode
function show_status {
    echo -e "${BLUE}=== RICK Trading System Status ===${NC}"
    echo ""
    
    # Check if mode manager exists
    if [ ! -f util/mode_manager.py ]; then
        echo -e "${RED}Error: Mode manager not found${NC}"
        exit 1
    fi
    
    # Run mode manager to get current status
    python3 -c "from util.mode_manager import get_mode_info; info = get_mode_info(); print(f'Current Mode: {info[\"mode\"]}'); print(f'API Enabled: {info[\"api\"]}'); print(f'Description: {info[\"description\"]}')"
    
    echo ""
    check_engine_status
}

# Function to switch mode
function switch_mode {
    MODE=$1
    
    echo -e "${BLUE}Switching to $MODE mode...${NC}"
    
    # Check if mode manager exists
    if [ ! -f util/mode_manager.py ]; then
        echo -e "${RED}Error: Mode manager not found${NC}"
        exit 1
    fi
    
    # Switch mode
    if [ "$MODE" == "LIVE" ]; then
        # For LIVE mode, we need to provide the PIN
        python3 -c "from util.mode_manager import switch_mode; switch_mode('LIVE', 841921)"
    else
        python3 -c "from util.mode_manager import switch_mode; switch_mode('$MODE')"
    fi
    
    # Check if engine is running and restart if needed
    if check_engine_status; then
        echo -e "${YELLOW}Restarting trading engine to apply new mode...${NC}"
        restart_engine
    fi
    
    echo -e "${GREEN}Mode switched to $MODE${NC}"
}

# Function to start trading engine
function start_engine {
    echo -e "${BLUE}Starting trading engine...${NC}"
    
    # Check if engine is already running
    if check_engine_status; then
        echo -e "${YELLOW}Trading engine is already running${NC}"
        return
    fi
    
    # Start engine in background
    nohup python3 trading_engine.py > logs/trading_engine_stdout.log 2>&1 &
    
    # Wait for PID file to be created
    sleep 2
    
    # Check if engine started successfully
    if check_engine_status; then
        echo -e "${GREEN}Trading engine started successfully${NC}"
    else
        echo -e "${RED}Failed to start trading engine${NC}"
    fi
}

# Function to stop trading engine
function stop_engine {
    echo -e "${BLUE}Stopping trading engine...${NC}"
    
    # Check if engine is running
    if [ -f .trading_engine.pid ]; then
        PID=$(cat .trading_engine.pid)
        if ps -p $PID > /dev/null; then
            echo -e "${YELLOW}Sending SIGTERM to PID $PID...${NC}"
            kill $PID
            
            # Wait for process to terminate
            sleep 2
            
            if ps -p $PID > /dev/null; then
                echo -e "${RED}Process did not terminate, sending SIGKILL...${NC}"
                kill -9 $PID
            fi
            
            echo -e "${GREEN}Trading engine stopped${NC}"
        else
            echo -e "${YELLOW}Trading engine is not running (stale PID file)${NC}"
            rm .trading_engine.pid
        fi
    else
        echo -e "${YELLOW}Trading engine is not running (no PID file)${NC}"
    fi
}

# Function to restart trading engine
function restart_engine {
    stop_engine
    sleep 2
    start_engine
}

# Main script logic
case "$1" in
    status)
        show_status
        ;;
    paper)
        switch_mode "PAPER"
        ;;
    live)
        switch_mode "LIVE"
        ;;
    start)
        start_engine
        ;;
    stop)
        stop_engine
        ;;
    restart)
        restart_engine
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        show_usage
        ;;
esac

exit 0