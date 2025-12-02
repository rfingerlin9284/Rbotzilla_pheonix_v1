#!/bin/bash
# Color-coded Paper Trading Monitor
# Easy-to-read real-time display of ghost trading activity

# Color definitions
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'

# Foreground colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'

# Background colors
BG_RED='\033[41m'
BG_GREEN='\033[42m'
BG_YELLOW='\033[43m'
BG_BLUE='\033[44m'
BG_CYAN='\033[46m'

# Bright colors
BRIGHT_GREEN='\033[1;32m'
BRIGHT_RED='\033[1;31m'
BRIGHT_YELLOW='\033[1;33m'
BRIGHT_CYAN='\033[1;36m'
BRIGHT_MAGENTA='\033[1;35m'

LOG_FILE="/home/ing/RICK/RICK_LIVE_CLEAN/logs/paper_trading.log"

# Function to print section divider
print_divider() {
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════${RESET}"
}

# Function to print header
print_header() {
    clear
    echo -e "${BG_BLUE}${WHITE}${BOLD}                                                                                ${RESET}"
    echo -e "${BG_BLUE}${WHITE}${BOLD}                    🤖 RICK PAPER TRADING MONITOR 🤖                            ${RESET}"
    echo -e "${BG_BLUE}${WHITE}${BOLD}                                                                                ${RESET}"
    print_divider
    echo ""
}

# Function to extract and display session info
display_session_info() {
    echo -e "${BRIGHT_CYAN}${BOLD}📊 SESSION INFORMATION${RESET}"
    print_divider
    
    # Extract capital
    CAPITAL=$(grep -oP 'capital: \$\K[\d.]+' "$LOG_FILE" | tail -1)
    if [ ! -z "$CAPITAL" ]; then
        echo -e "${GREEN}💰 Capital:${RESET}        ${BRIGHT_GREEN}${BOLD}\$$CAPITAL${RESET}"
    fi
    
    # Extract win rate
    WIN_RATE=$(grep -oP 'Win Rate: \K[\d.]+' "$LOG_FILE" | tail -1)
    if [ ! -z "$WIN_RATE" ]; then
        if (( $(echo "$WIN_RATE >= 70" | bc -l) )); then
            echo -e "${GREEN}📈 Win Rate:${RESET}       ${BRIGHT_GREEN}${BOLD}${WIN_RATE}%${RESET} ✅"
        else
            echo -e "${YELLOW}📈 Win Rate:${RESET}       ${YELLOW}${BOLD}${WIN_RATE}%${RESET}"
        fi
    fi
    
    # Check if session is running
    if ps aux | grep -v grep | grep -q "ghost_trading_engine"; then
        echo -e "${GREEN}🟢 Status:${RESET}         ${BRIGHT_GREEN}${BOLD}TRADING LIVE${RESET}"
    else
        echo -e "${RED}⚫ Status:${RESET}         ${BRIGHT_RED}${BOLD}NOT RUNNING${RESET}"
    fi
    
    echo ""
}

# Function to display broker connections
display_connections() {
    echo -e "${BRIGHT_MAGENTA}${BOLD}🔗 BROKER CONNECTIONS${RESET}"
    print_divider
    
    if grep -q "OANDA v20 API - PRACTICE MODE - CONNECTED" "$LOG_FILE"; then
        echo -e "${GREEN}✅ OANDA:${RESET}          ${BRIGHT_GREEN}Practice API Connected${RESET}"
    else
        echo -e "${RED}❌ OANDA:${RESET}          ${BRIGHT_RED}Not Connected${RESET}"
    fi
    
    if grep -q "Coinbase Advanced API - SANDBOX MODE - CONNECTED" "$LOG_FILE"; then
        echo -e "${GREEN}✅ Coinbase:${RESET}       ${BRIGHT_GREEN}Sandbox API Connected${RESET}"
    else
        echo -e "${RED}❌ Coinbase:${RESET}       ${BRIGHT_RED}Not Connected${RESET}"
    fi
    
    echo ""
}

# Function to display recent trades
display_recent_trades() {
    echo -e "${BRIGHT_YELLOW}${BOLD}💱 RECENT TRADES${RESET}"
    print_divider
    
    # Get last 5 ghost trades
    grep "GHOST TRADE:" "$LOG_FILE" | tail -5 | while read -r line; do
        if echo "$line" | grep -q "BUY"; then
            ARROW="📈"
            COLOR="${GREEN}"
        else
            ARROW="📉"
            COLOR="${RED}"
        fi
        
        PAIR=$(echo "$line" | grep -oP '\b[A-Z]{3}_[A-Z]{3}\b' | head -1)
        DIRECTION=$(echo "$line" | grep -oP '\b(BUY|SELL)\b')
        PRICE=$(echo "$line" | grep -oP '@ \K[\d.]+')
        TIME=$(echo "$line" | awk '{print $1, $2}')
        
        echo -e "${DIM}${TIME}${RESET} ${ARROW} ${COLOR}${BOLD}${DIRECTION}${RESET} ${CYAN}${PAIR}${RESET} @ ${WHITE}${PRICE}${RESET}"
    done
    
    echo ""
}

# Function to display trade results
display_trade_results() {
    echo -e "${BRIGHT_CYAN}${BOLD}🎯 TRADE RESULTS${RESET}"
    print_divider
    
    # Get last 5 trade results
    grep "Ghost Trade Result:" "$LOG_FILE" | tail -5 | while read -r line; do
        if echo "$line" | grep -q "WIN"; then
            RESULT_COLOR="${BG_GREEN}${WHITE}${BOLD}"
            EMOJI="✅"
        else
            RESULT_COLOR="${BG_RED}${WHITE}${BOLD}"
            EMOJI="❌"
        fi
        
        RESULT=$(echo "$line" | grep -oP '(WIN|LOSS)')
        PNL=$(echo "$line" | grep -oP 'PnL: \$\K[-\d.]+')
        CAPITAL=$(echo "$line" | grep -oP 'Capital: \$\K[\d.]+')
        WINRATE=$(echo "$line" | grep -oP 'Win Rate: \K[\d.]+')
        TIME=$(echo "$line" | awk '{print $1, $2}')
        
        echo -e "${DIM}${TIME}${RESET} ${EMOJI} ${RESULT_COLOR} ${RESULT} ${RESET} ${YELLOW}P&L:${RESET} ${BOLD}\$${PNL}${RESET} ${GREEN}Capital:${RESET} \$${CAPITAL} ${CYAN}WR:${RESET} ${WINRATE}%"
    done
    
    echo ""
}

# Function to display Rick's commentary
display_rick_commentary() {
    echo -e "${BRIGHT_MAGENTA}${BOLD}💬 RICK'S COMMENTARY${RESET}"
    print_divider
    
    # Get last 3 Rick comments
    grep "Rick:" "$LOG_FILE" | tail -3 | while read -r line; do
        COMMENT=$(echo "$line" | grep -oP 'Rick: \K.*')
        TIME=$(echo "$line" | awk '{print $1, $2}')
        
        echo -e "${DIM}${TIME}${RESET} ${BRIGHT_YELLOW}Rick:${RESET} ${WHITE}${COMMENT}${RESET}"
    done
    
    echo ""
}

# Function to display promotion criteria
display_promotion_criteria() {
    echo -e "${BRIGHT_GREEN}${BOLD}🎯 PROMOTION CRITERIA${RESET}"
    print_divider
    
    if grep -q "Promotion criteria:" "$LOG_FILE"; then
        CRITERIA=$(grep "Promotion criteria:" "$LOG_FILE" | tail -1)
        
        echo -e "${CYAN}Min Trades:${RESET}        10 trades required"
        echo -e "${CYAN}Win Rate:${RESET}          ≥70% required"
        echo -e "${CYAN}Min P&L:${RESET}           \$50+ required"
        echo -e "${CYAN}Max Losses:${RESET}        <3 consecutive"
        echo -e "${CYAN}Avg R:R:${RESET}           ≥2.5:1 required"
    fi
    
    echo ""
}

# Function to display live tail
display_live_updates() {
    echo -e "${BRIGHT_RED}${BOLD}📡 LIVE UPDATES (Last 10 lines)${RESET}"
    print_divider
    
    tail -10 "$LOG_FILE" | while read -r line; do
        # Color code by log level
        if echo "$line" | grep -q "ERROR"; then
            echo -e "${RED}${line}${RESET}"
        elif echo "$line" | grep -q "WARNING"; then
            echo -e "${YELLOW}${line}${RESET}"
        elif echo "$line" | grep -q "INFO.*GHOST TRADE"; then
            echo -e "${BRIGHT_GREEN}${line}${RESET}"
        elif echo "$line" | grep -q "INFO.*WIN"; then
            echo -e "${BRIGHT_GREEN}${line}${RESET}"
        elif echo "$line" | grep -q "INFO.*LOSS"; then
            echo -e "${BRIGHT_RED}${line}${RESET}"
        elif echo "$line" | grep -q "Rick:"; then
            echo -e "${BRIGHT_MAGENTA}${line}${RESET}"
        else
            echo -e "${DIM}${line}${RESET}"
        fi
    done
    
    echo ""
    print_divider
    echo -e "${DIM}Press Ctrl+C to exit • Refreshing every 3 seconds${RESET}"
}

# Main monitoring loop
while true; do
    print_header
    display_session_info
    display_connections
    display_promotion_criteria
    display_recent_trades
    display_trade_results
    display_rick_commentary
    display_live_updates
    
    sleep 3
done
