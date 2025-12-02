#!/bin/bash
# ============================================================================
# RICK Plain English Interface
# Simple command interface for querying system information
# No coding required - Just ask questions in plain English!
# PIN: 841921
# ============================================================================

# Colors for readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

PROJECT_ROOT="/home/ing/RICK/RICK_LIVE_CLEAN"

show_header() {
    clear
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    🤖 RICK PLAIN ENGLISH INTERFACE                           ║"
    echo "║                    Ask Questions - Get Answers                               ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo ""
}

show_help() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}HOW TO USE THIS INTERFACE${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Just type your question or command below. Examples:"
    echo ""
    echo -e "${YELLOW}Questions You Can Ask:${NC}"
    echo "  • status          - Show me the overall system status"
    echo "  • health          - Is the system healthy?"
    echo "  • trading         - Is trading active?"
    echo "  • balance         - What's my account balance?"
    echo "  • trades          - Show me recent trades"
    echo "  • positions       - What positions are open?"
    echo "  • features        - What features are available?"
    echo "  • brokers         - Which brokers am I using?"
    echo "  • activity        - What's happening right now?"
    echo "  • logs            - Show me recent activity logs"
    echo "  • help            - Show this help menu"
    echo "  • menu            - Show all available commands"
    echo "  • quit or exit    - Leave this interface"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

show_menu() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}AVAILABLE COMMANDS${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}System Status:${NC}"
    echo "  status, health, features, brokers"
    echo ""
    echo -e "${YELLOW}Trading Information:${NC}"
    echo "  trading, balance, trades, positions, activity"
    echo ""
    echo -e "${YELLOW}Recent Activity:${NC}"
    echo "  logs, events, signals, errors"
    echo ""
    echo -e "${YELLOW}Configuration:${NC}"
    echo "  config, settings, accounts"
    echo ""
    echo -e "${YELLOW}Help:${NC}"
    echo "  help, menu, quit, exit"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

cmd_status() {
    echo -e "${GREEN}━━━ SYSTEM STATUS ━━━${NC}"
    echo ""
    
    # Check trading engine
    if pgrep -f "rick_trading_engine\|oanda_trading_engine\|canary_trading" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Trading Engine is RUNNING${NC}"
    else
        echo -e "${YELLOW}⚠️  Trading Engine is STOPPED${NC}"
        echo "   (You can start it with: ./start_paper.sh)"
    fi
    
    # Check narration
    if [ -f "$PROJECT_ROOT/narration.jsonl" ]; then
        local size=$(du -h "$PROJECT_ROOT/narration.jsonl" 2>/dev/null | cut -f1)
        echo -e "${GREEN}✅ Narration System is ACTIVE${NC}"
        echo "   Log size: $size"
    else
        echo -e "${YELLOW}⚠️  No narration log found${NC}"
    fi
    
    # Check dashboard
    if pgrep -f "dashboard\.py\|streamlit" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Dashboard is RUNNING${NC}"
    else
        echo -e "${YELLOW}⚠️  Dashboard is STOPPED${NC}"
    fi
    
    # Feature count (fallback)
    echo ""
}

# ... More internal functions and handlers (see file for full details) ...

main_loop() {
    show_header
    show_help
    while true; do
        echo -ne "${BLUE}RICK> ${NC}"
        read -r input
        cmd=$(echo "$input" | tr '[:upper:]' '[:lower:]' | xargs)
        echo ""
        case "$cmd" in
            "quit"|"exit"|"q")
                echo "Goodbye! 👋"
                echo ""
                exit 0
                ;;
            "help"|"h"|"?")
                show_help
                ;;
            "menu"|"commands")
                show_menu
                ;;
            "status"|"what's the status"|"system status")
                cmd_status
                ;;
            "health"|"is the system healthy"|"system health")
                cmd_health
                ;;
            "trading"|"is trading active"|"trading status")
                cmd_trading
                ;;
            "balance"|"balances"|"account balance"|"what's my balance")
                cmd_balance
                ;;
            "trades"|"recent trades"|"show trades"|"trade history")
                cmd_trades
                ;;
            "positions"|"open positions"|"what positions"|"show positions")
                cmd_positions
                ;;
            "features"|"what features"|"show features"|"capabilities")
                cmd_features
                ;;
            "brokers"|"which brokers"|"show brokers"|"broker status")
                cmd_brokers
                ;;
            "activity"|"what's happening"|"recent activity"|"current activity")
                cmd_activity
                ;;
            "logs"|"show logs"|"recent logs")
                cmd_logs
                ;;
            "events"|"show events"|"recent events")
                cmd_events
                ;;
            "signals"|"show signals"|"recent signals"|"trading signals")
                cmd_signals
                ;;
            "errors"|"show errors"|"any errors"|"warnings")
                cmd_errors
                ;;
            "config"|"configuration"|"show config")
                cmd_config
                ;;
            "settings"|"show settings")
                cmd_settings
                ;;
            "accounts"|"show accounts")
                cmd_accounts
                ;;
            "clear"|"cls")
                show_header
                ;;
            "")
                ;;
            *)
                echo -e "${YELLOW}I don't understand that command.${NC}"
                echo "Type 'help' to see available commands, or 'menu' for a full list."
                echo ""
                ;;
        esac
    done
}

# Check for interactive terminal
if [ -t 0 ]; then
    main_loop
else
    echo "This interface requires an interactive terminal."
    echo "Please run it directly from your terminal."
    exit 1
fi
