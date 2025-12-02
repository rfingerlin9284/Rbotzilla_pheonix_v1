#!/usr/bin/env bash
# RICK Live Status Monitor - Plain English Real-Time Activity Feed
# Color-coded, human-readable trading activity

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# OANDA credentials from .env
source /home/ing/RICK/RICK_LIVE_CLEAN/.env 2>/dev/null

clear
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${BOLD}${WHITE}🤖 RICK LIVE TRADING STATUS${NC}  ${GRAY}$(date '+%Y-%m-%d %H:%M:%S')${NC}              ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if trading engine is running
PROC_COUNT=$(pgrep -f "run_autonomous_full.py" | wc -l)
if [ "$PROC_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ TRADING ENGINE: RUNNING${NC} (PID: $(pgrep -f run_autonomous_full.py | head -1))"
else
    echo -e "${RED}❌ TRADING ENGINE: STOPPED${NC}"
fi

# Check IBKR status
IBKR_COUNT=$(pgrep -f "ibkr_trading_engine" | wc -l)
if [ "$IBKR_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ IBKR ENGINE: RUNNING${NC}"
else
    echo -e "${YELLOW}⚠️  IBKR ENGINE: NOT RUNNING${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${WHITE}📊 CURRENT POSITIONS (OANDA Practice)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Fetch OANDA positions
POSITIONS=$(curl -s -H "Authorization: Bearer ${OANDA_PRACTICE_TOKEN}" \
    "https://api-fxpractice.oanda.com/v3/accounts/${OANDA_PRACTICE_ACCOUNT_ID}/openPositions" 2>/dev/null)

if [ -n "$POSITIONS" ]; then
    echo "$POSITIONS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    positions = data.get('positions', [])
    if not positions:
        print('  ${GRAY}No open positions${NC}')
    else:
        for pos in positions:
            inst = pos['instrument'].replace('_', '/')
            long_units = int(pos['long']['units'])
            short_units = int(pos['short']['units'])
            unrealized = float(pos.get('unrealizedPL', 0))
            
            if long_units > 0:
                direction = 'LONG'
                units = long_units
                avg_price = pos['long'].get('averagePrice', 'N/A')
            else:
                direction = 'SHORT'
                units = abs(short_units)
                avg_price = pos['short'].get('averagePrice', 'N/A')
            
            # Color based on P/L
            if unrealized >= 0:
                pl_color = '\033[0;32m'  # Green
                pl_sign = '+'
            else:
                pl_color = '\033[0;31m'  # Red
                pl_sign = ''
            
            print(f'  {inst}: {direction} {units:,} units @ {avg_price}')
            print(f'    └─ P/L: {pl_color}{pl_sign}\${unrealized:.2f}\033[0m')
except Exception as e:
    print(f'  Error reading positions: {e}')
"
else
    echo -e "  ${RED}Unable to fetch positions${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${WHITE}📋 PENDING ORDERS${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Fetch OANDA orders
ORDERS=$(curl -s -H "Authorization: Bearer ${OANDA_PRACTICE_TOKEN}" \
    "https://api-fxpractice.oanda.com/v3/accounts/${OANDA_PRACTICE_ACCOUNT_ID}/orders" 2>/dev/null)

if [ -n "$ORDERS" ]; then
    echo "$ORDERS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    orders = data.get('orders', [])
    if not orders:
        print('  \033[0;90mNo pending orders\033[0m')
    else:
        for order in orders:
            order_type = order.get('type', 'UNKNOWN')
            order_id = order.get('id', 'N/A')
            
            if order_type in ['STOP_LOSS', 'TAKE_PROFIT']:
                trade_id = order.get('tradeID', 'N/A')
                price = order.get('price', 'N/A')
                if order_type == 'STOP_LOSS':
                    print(f'  🛑 Stop Loss #{order_id} for Trade #{trade_id} @ {price}')
                else:
                    print(f'  🎯 Take Profit #{order_id} for Trade #{trade_id} @ {price}')
            elif order_type == 'LIMIT':
                inst = order.get('instrument', 'N/A').replace('_', '/')
                units = order.get('units', 'N/A')
                price = order.get('price', 'N/A')
                print(f'  📊 Limit Order #{order_id}: {inst} {units} units @ {price}')
            elif order_type == 'MARKET':
                inst = order.get('instrument', 'N/A').replace('_', '/')
                units = order.get('units', 'N/A')
                print(f'  ⚡ Market Order #{order_id}: {inst} {units} units')
except Exception as e:
    print(f'  Error reading orders: {e}')
"
else
    echo -e "  ${RED}Unable to fetch orders${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${WHITE}💬 RECENT ACTIVITY (Plain English)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Parse recent log entries and translate to plain English
tail -50 /home/ing/RICK/RICK_LIVE_CLEAN/logs/live.log 2>/dev/null | python3 -c "
import sys
import re
from datetime import datetime

lines = sys.stdin.readlines()
seen = set()
count = 0

for line in reversed(lines):
    if count >= 8:
        break
    
    line = line.strip()
    if not line:
        continue
    
    # Extract timestamp
    time_match = re.search(r'(\d{2}:\d{2}:\d{2})', line)
    time_str = time_match.group(1) if time_match else ''
    
    msg = ''
    color = '\033[0m'
    
    # Pre-trade gate check
    if 'PRE-TRADE GATE:' in line:
        match = re.search(r'PRE-TRADE GATE: (\w+_\w+) (BUY|SELL) (\d+)', line)
        if match:
            pair, direction, units = match.groups()
            pair = pair.replace('_', '/')
            msg = f'🔍 Analyzing {direction} opportunity for {pair} ({int(units):,} units)'
            color = '\033[0;36m'  # Cyan
    
    # Margin gate passed
    elif 'Margin gate PASSED' in line:
        match = re.search(r'(\d+\.?\d*)% utilization', line)
        if match:
            util = match.group(1)
            msg = f'✅ Margin check OK ({util}% used)'
            color = '\033[0;32m'  # Green
    
    # Correlation gate blocked
    elif 'Correlation gate BLOCKED' in line:
        match = re.search(r'(\w+_bucket).*was (-?\d+).*now (-?\d+)', line)
        if match:
            bucket, was, now = match.groups()
            currency = bucket.replace('_bucket', '').upper()
            msg = f'🚫 BLOCKED: Too much {currency} exposure ({int(was):,} → {int(now):,} units)'
            color = '\033[0;33m'  # Yellow
    
    # Correlation gate passed
    elif 'Correlation gate PASSED' in line:
        match = re.search(r'(\w+_\w+) (BUY|SELL)', line)
        if match:
            pair, direction = match.groups()
            pair = pair.replace('_', '/')
            msg = f'✅ Correlation OK for {pair} {direction}'
            color = '\033[0;32m'  # Green
    
    # Order placed
    elif 'OANDA OCO placed' in line:
        match = re.search(r'(\w+_\w+).*Entry: ([\d.]+).*SL: ([\d.]+).*TP: ([\d.]+).*Order ID: (\d+)', line)
        if match:
            pair, entry, sl, tp, order_id = match.groups()
            pair = pair.replace('_', '/')
            msg = f'🎯 ORDER PLACED #{order_id}: {pair} @ {entry} (SL: {sl}, TP: {tp})'
            color = '\033[0;32m'  # Green
    
    # Pre-trade gate passed
    elif 'PRE-TRADE GATE PASSED' in line:
        msg = f'✅ All pre-trade checks passed - ready to execute'
        color = '\033[0;32m'  # Green
    
    if msg and msg not in seen:
        seen.add(msg)
        print(f'  {color}[{time_str}] {msg}\033[0m')
        count += 1
"

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${WHITE}💰 ACCOUNT SUMMARY${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Fetch account summary
ACCOUNT=$(curl -s -H "Authorization: Bearer ${OANDA_PRACTICE_TOKEN}" \
    "https://api-fxpractice.oanda.com/v3/accounts/${OANDA_PRACTICE_ACCOUNT_ID}/summary" 2>/dev/null)

if [ -n "$ACCOUNT" ]; then
    echo "$ACCOUNT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    acct = data.get('account', {})
    balance = float(acct.get('balance', 0))
    nav = float(acct.get('NAV', balance))
    unrealized = float(acct.get('unrealizedPL', 0))
    margin_used = float(acct.get('marginUsed', 0))
    margin_avail = float(acct.get('marginAvailable', 0))
    open_trades = int(acct.get('openTradeCount', 0))
    
    print(f'  Balance:        \${balance:,.2f}')
    print(f'  NAV:            \${nav:,.2f}')
    if unrealized >= 0:
        print(f'  Unrealized P/L: \033[0;32m+\${unrealized:,.2f}\033[0m')
    else:
        print(f'  Unrealized P/L: \033[0;31m\${unrealized:,.2f}\033[0m')
    print(f'  Margin Used:    \${margin_used:,.2f}')
    print(f'  Margin Avail:   \${margin_avail:,.2f}')
    print(f'  Open Trades:    {open_trades}')
except Exception as e:
    print(f'  Error: {e}')
"
fi

echo ""
echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GRAY}Press Ctrl+C to exit | Refresh: ./rick_live_status.sh${NC}"
