#!/bin/bash
# ============================================================================
# RICK Persistent Monitoring Terminal
# Self-healing autonomous system monitor for VSCode terminal
# PIN: 841921
# ============================================================================

MONITOR_FLAG="/tmp/rick_monitor_active"
PID_FILE="/tmp/rick_monitor.pid"
PROJECT_ROOT="/home/ing/RICK/RICK_PHOENIX"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

check_feature_status() {
    local feature_name="$1"
    local check_command="$2"
    if eval "$check_command" &>/dev/null; then
        echo -e "${GREEN}✅${NC} $feature_name"
        return 0
    else
        echo -e "${RED}❌${NC} $feature_name"
        return 1
    fi
}

check_file_exists() {
    local file="$1"
    [ -f "$PROJECT_ROOT/$file" ]
}

display_feature_status() {
    clear
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║              🤖 RICK AUTONOMOUS TRADING SYSTEM - FEATURE STATUS              ║"
    echo "║                    HIVE MIND → RBOTZILLA INTEGRATION                         ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo -e "${CYAN}System Timestamp:${NC} $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo -e "${CYAN}PIN Authentication:${NC} 841921"
    echo ""

    local active_count=0
    local total_count=0
    echo "════════════════════════════════════════════════"
    echo "FEATURE SUMMARY"
    echo "════════════════════════════════════════════════"
    check_feature_status "OANDA Connector" "check_file_exists 'connectors/oanda_connector.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Narration System" "check_file_exists 'logs/narration.jsonl'" && ((active_count++)); ((total_count++))
    printf "\n${GREEN}Active Features:${NC} %d / %d\n" $active_count $total_count
}

show_live_narration() {
    echo "════════════════════════════════════════════════"
    echo "📡 LIVE TRADING NARRATION (last 10 events)"
    echo "════════════════════════════════════════════════"
    if [ -f "$PROJECT_ROOT/narration.jsonl" ]; then
        tail -10 "$PROJECT_ROOT/narration.jsonl" | while read -r line; do
            local timestamp=$(echo "$line" | jq -r '.timestamp | split("T")[1] | split("+")[0] | split(".")[0]' 2>/dev/null || echo "N/A")
            local event_type=$(echo "$line" | jq -r '.event_type' 2>/dev/null || echo "UNKNOWN")
            local symbol=$(echo "$line" | jq -r '.symbol // "N/A"' 2>/dev/null)
            case "$event_type" in
                *TRADE_OPENED*|*ORDER_PLACED*) echo -e "${GREEN}[$timestamp] 🟢 $event_type: $symbol${NC}" ;; 
                *SIGNAL*) echo -e "${YELLOW}[$timestamp] 📊 $event_type: $symbol${NC}" ;; 
                *ERROR*|*REJECTED*) echo -e "${RED}[$timestamp] ❌ $event_type: $symbol${NC}" ;; 
                *) echo -e "${NC}[$timestamp] 📋 $event_type: $symbol${NC}" ;; 
            esac
        done
    else
        echo "No narration log found. Start trading to see events."
    fi
    echo ""
}

run_persistent_monitor() {
    echo "Starting RICK Persistent Monitor..."
    echo "Monitor flag: $MONITOR_FLAG"
    echo "PID: $$"
    echo $$ > "$PID_FILE"
    while [ -f "$MONITOR_FLAG" ]; do
        display_feature_status
        show_live_narration
        echo "Auto-refresh in 30 seconds..."
        sleep 30
    done
    echo "Monitor flag removed. Stopping persistent monitor."
    rm -f "$PID_FILE"
}

start_monitor() {
    if [ -f "$MONITOR_FLAG" ]; then
        echo "Monitor is already running"
        exit 1
    fi
    touch "$MONITOR_FLAG"
    run_persistent_monitor
}

stop_monitor() {
    if [ ! -f "$MONITOR_FLAG" ]; then
        echo "Monitor is not running"
        exit 1
    fi
    echo "Stopping persistent monitor..."
    rm -f "$MONITOR_FLAG"
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid" 2>/dev/null
            echo "Monitor stopped (PID: $pid)"
        fi
        rm -f "$PID_FILE"
    fi
}

check_status() {
    if [ -f "$MONITOR_FLAG" ]; then
        echo "Monitor is RUNNING"
    else
        echo "Monitor is NOT running"
    fi
}

case "${1:-}" in
    start) start_monitor ;; stop) stop_monitor ;; status) check_status ;; *) echo "Usage: $0 {start|stop|status}" ;;
esac
