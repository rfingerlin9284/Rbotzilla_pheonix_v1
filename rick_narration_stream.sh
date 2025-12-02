#!/usr/bin/env bash
# RICK Live Narration Stream - Continuous Real-Time Activity Monitor
# Auto-refreshing, color-coded, plain English trading feed

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'
BOLD='\033[1m'
BG_GREEN='\033[42m'
BG_RED='\033[41m'
BG_YELLOW='\033[43m'

# OANDA credentials
source /home/ing/RICK/RICK_LIVE_CLEAN/.env 2>/dev/null

# Track last log position
LAST_LINE=0

show_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BOLD}${WHITE}🤖 RICK LIVE NARRATION STREAM${NC}                                           ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  ${GRAY}Real-time plain English activity feed | Auto-refreshes every 5s${NC}         ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

show_status_bar() {
    local now=$(date '+%H:%M:%S')
    
    # Check engine status
    local engine_status="${RED}STOPPED${NC}"
    if pgrep -f "run_autonomous_full.py" > /dev/null; then
        engine_status="${GREEN}RUNNING${NC}"
    fi
    
    # Get account balance
    local balance="..."
    local positions="0"
    local unrealized="..."
    
    ACCT=$(curl -s -H "Authorization: Bearer ${OANDA_PRACTICE_TOKEN}" \
        "https://api-fxpractice.oanda.com/v3/accounts/${OANDA_PRACTICE_ACCOUNT_ID}/summary" 2>/dev/null)
    
    if [ -n "$ACCT" ]; then
        balance=$(echo "$ACCT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"\${float(d['account']['balance']):,.2f}\")" 2>/dev/null || echo "...")
        positions=$(echo "$ACCT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['account']['openTradeCount'])" 2>/dev/null || echo "0")
        unrealized=$(echo "$ACCT" | python3 -c "import sys,json; d=json.load(sys.stdin); pl=float(d['account']['unrealizedPL']); print(f'+\${pl:,.2f}' if pl>=0 else f'\${pl:,.2f}')" 2>/dev/null || echo "...")
    fi
    
    echo -e "${GRAY}┌─────────────────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${GRAY}│${NC} ⏰ ${WHITE}${now}${NC} │ Engine: ${engine_status} │ Balance: ${WHITE}${balance}${NC} │ P/L: ${unrealized} │ Positions: ${WHITE}${positions}${NC} ${GRAY}│${NC}"
    echo -e "${GRAY}└─────────────────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
}

show_positions() {
    echo -e "${BOLD}${WHITE}📊 ACTIVE POSITIONS${NC}"
    echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
    
    POSITIONS=$(curl -s -H "Authorization: Bearer ${OANDA_PRACTICE_TOKEN}" \
        "https://api-fxpractice.oanda.com/v3/accounts/${OANDA_PRACTICE_ACCOUNT_ID}/openPositions" 2>/dev/null)
    
    if [ -n "$POSITIONS" ]; then
        echo "$POSITIONS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    positions = data.get('positions', [])
    if not positions:
        print('  \033[0;90mNo open positions - watching for opportunities...\033[0m')
    else:
        for pos in positions:
            inst = pos['instrument'].replace('_', '/')
            long_units = int(pos['long']['units'])
            short_units = int(pos['short']['units'])
            unrealized = float(pos.get('unrealizedPL', 0))
            margin = float(pos.get('marginUsed', 0))
            
            if long_units > 0:
                direction = '📈 LONG'
                units = long_units
                avg_price = pos['long'].get('averagePrice', 'N/A')
                dir_color = '\033[0;32m'  # Green
            else:
                direction = '📉 SHORT'
                units = abs(short_units)
                avg_price = pos['short'].get('averagePrice', 'N/A')
                dir_color = '\033[0;31m'  # Red
            
            # P/L color
            if unrealized >= 0:
                pl_str = f'\033[0;32m+\${unrealized:.2f}\033[0m'
            else:
                pl_str = f'\033[0;31m\${unrealized:.2f}\033[0m'
            
            print(f'  {dir_color}{direction}\033[0m {inst} | {units:,} units @ {avg_price} | P/L: {pl_str} | Margin: \${margin:.2f}')
except Exception as e:
    print(f'  Error: {e}')
"
    fi
    echo ""
}

show_live_feed() {
    echo -e "${BOLD}${WHITE}💬 LIVE ACTIVITY FEED${NC} ${GRAY}(Most recent first)${NC}"
    echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
    
    # Parse and translate log entries to plain English
    tail -30 /home/ing/RICK/RICK_LIVE_CLEAN/logs/live.log 2>/dev/null | python3 -c "
import sys
import re

lines = sys.stdin.readlines()
seen = set()
count = 0

for line in reversed(lines):
    if count >= 10:
        break
    
    line = line.strip()
    if not line:
        continue
    
    # Extract timestamp
    time_match = re.search(r'(\d{2}:\d{2}:\d{2})', line)
    time_str = time_match.group(1) if time_match else '??:??:??'
    
    msg = ''
    icon = ''
    color = '\033[0m'
    
    # === SIGNAL DETECTION ===
    if 'PRE-TRADE GATE:' in line:
        match = re.search(r'PRE-TRADE GATE: (\w+_\w+) (BUY|SELL) (\d+)', line)
        if match:
            pair, direction, units = match.groups()
            pair = pair.replace('_', '/')
            icon = '🔍'
            msg = f'Spotted {direction} signal for {pair} ({int(units):,} units) - checking risk...'
            color = '\033[0;36m'  # Cyan
    
    # === MARGIN CHECK ===
    elif 'Margin gate PASSED' in line:
        match = re.search(r'(\d+\.?\d*)% utilization', line)
        if match:
            util = match.group(1)
            icon = '✅'
            msg = f'Margin OK - only {util}% of capital at risk'
            color = '\033[0;32m'  # Green
    
    # === CORRELATION BLOCKED ===
    elif 'Correlation gate BLOCKED' in line:
        match = re.search(r'(\w+)_bucket.*was (-?\d+).*now (-?\d+)', line)
        if match:
            currency, was, now = match.groups()
            currency = currency.upper()
            icon = '🛡️'
            msg = f'PROTECTED: Too much {currency} exposure already - trade blocked for safety'
            color = '\033[0;33m'  # Yellow
    
    # === CORRELATION PASSED ===
    elif 'Correlation gate PASSED' in line:
        match = re.search(r'(\w+_\w+) (BUY|SELL)', line)
        if match:
            pair, direction = match.groups()
            pair = pair.replace('_', '/')
            icon = '✅'
            msg = f'Diversification OK - {pair} {direction} wont over-concentrate portfolio'
            color = '\033[0;32m'  # Green
    
    # === ORDER PLACED ===
    elif 'OANDA OCO placed' in line:
        match = re.search(r'(\w+_\w+).*Entry: ([\d.]+).*SL: ([\d.]+).*TP: ([\d.]+).*Order ID: (\d+)', line)
        if match:
            pair, entry, sl, tp, order_id = match.groups()
            pair = pair.replace('_', '/')
            icon = '🎯'
            msg = f'TRADE OPENED: {pair} @ {entry} | Stop Loss: {sl} | Take Profit: {tp}'
            color = '\033[1;32m'  # Bold Green
    
    # === ALL CHECKS PASSED ===
    elif 'PRE-TRADE GATE PASSED' in line:
        icon = '🚀'
        msg = f'All safety checks passed - executing trade...'
        color = '\033[0;32m'  # Green
    
    # === HIVE MIND ===
    elif 'Hive Mind' in line.lower() or 'consensus' in line.lower():
        icon = '🐝'
        msg = f'Hive Mind analyzing market consensus...'
        color = '\033[0;35m'  # Magenta
    
    # === ML/REGIME ===
    elif 'regime' in line.lower():
        icon = '🧠'
        msg = f'ML detecting current market regime...'
        color = '\033[0;35m'  # Magenta
    
    if msg and msg not in seen:
        seen.add(msg)
        print(f'  \033[0;90m[{time_str}]\033[0m {icon} {color}{msg}\033[0m')
        count += 1

if count == 0:
    print('  \033[0;90mWaiting for trading activity...\033[0m')
"
    echo ""
}

show_explanation() {
    echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${GRAY}📖 What RICK is doing:${NC}"
    echo -e "${GRAY}   • Scanning forex pairs every ~5 minutes for profitable opportunities${NC}"
    echo -e "${GRAY}   • Running each signal through margin, correlation & charter safety gates${NC}"
    echo -e "${GRAY}   • Blocking trades that would over-expose the portfolio to one currency${NC}"
    echo -e "${GRAY}   • When all checks pass, placing real trades with stop-loss protection${NC}"
    echo -e ""
    echo -e "${GRAY}Press Ctrl+C to exit${NC}"
}

# Main loop
while true; do
    show_header
    show_status_bar
    show_positions
    show_live_feed
    show_explanation
    sleep 5
done
