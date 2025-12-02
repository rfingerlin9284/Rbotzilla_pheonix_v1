#!/bin/bash
# CANARY Narration Monitor
# Real-time monitoring of Charter-compliant trading events
# PIN: 841921

NARRATION_LOG="/home/ing/RICK/RICK_LIVE_CLEAN/pre_upgrade/headless/logs/narration.jsonl"

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🐤 CANARY NARRATION MONITOR                               ║"
echo "║                    Charter-Compliant Event Stream                            ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if narration log exists
if [ ! -f "$NARRATION_LOG" ]; then
    echo "❌ Narration log not found: $NARRATION_LOG"
    exit 1
fi

echo "📊 Monitoring: $NARRATION_LOG"
echo "Press Ctrl+C to stop"
echo ""
echo "───────────────────────────────────────────────────────────────────────────────"
echo ""

# Tail with colored output
tail -f "$NARRATION_LOG" | while read -r line; do
    # Parse event type
    event_type=$(echo "$line" | jq -r '.event_type' 2>/dev/null)
    timestamp=$(echo "$line" | jq -r '.timestamp | split("T")[1] | split("+")[0]' 2>/dev/null)
    symbol=$(echo "$line" | jq -r '.symbol // "N/A"' 2>/dev/null)
    
    # Color code by event type
    case "$event_type" in
        "CANARY_INIT")
            echo -e "\033[1;36m[$timestamp] 🐤 CANARY_INIT\033[0m"
            echo "$line" | jq '.details' 2>/dev/null
            ;;
        "CANARY_SESSION_START")
            echo -e "\033[1;32m[$timestamp] 🚀 CANARY_SESSION_START\033[0m"
            echo "$line" | jq '.details.charter_rules' 2>/dev/null
            ;;
        "SIGNAL_GENERATED")
            side=$(echo "$line" | jq -r '.details.side' 2>/dev/null)
            rr=$(echo "$line" | jq -r '.details.risk_reward_ratio' 2>/dev/null)
            echo -e "\033[1;33m[$timestamp] 📊 SIGNAL_GENERATED: $symbol $side (RR: $rr)\033[0m"
            ;;
        "SIGNAL_REJECTED")
            reason=$(echo "$line" | jq -r '.details.reason' 2>/dev/null)
            echo -e "\033[1;31m[$timestamp] ❌ SIGNAL_REJECTED: $reason\033[0m"
            ;;
        "TRADE_OPENED")
            trade_id=$(echo "$line" | jq -r '.details.trade_id' 2>/dev/null)
            notional=$(echo "$line" | jq -r '.details.notional_usd' 2>/dev/null)
            echo -e "\033[1;32m[$timestamp] 🟢 TRADE_OPENED: $symbol ($trade_id) - \$${notional}\033[0m"
            ;;
        "TRADE_CLOSED")
            outcome=$(echo "$line" | jq -r '.details.outcome' 2>/dev/null)
            pnl=$(echo "$line" | jq -r '.details.pnl' 2>/dev/null)
            if [ "$outcome" = "win" ]; then
                echo -e "\033[1;32m[$timestamp] ✅ TRADE_CLOSED: $symbol - WIN (+\$$pnl)\033[0m"
            else
                echo -e "\033[1;31m[$timestamp] ❌ TRADE_CLOSED: $symbol - LOSS (\$$pnl)\033[0m"
            fi
            ;;
        "TTL_ENFORCEMENT")
            duration=$(echo "$line" | jq -r '.details.duration_hours' 2>/dev/null)
            echo -e "\033[1;35m[$timestamp] ⏰ TTL_ENFORCEMENT: $symbol (${duration}h)\033[0m"
            ;;
        "CANARY_SESSION_END")
            win_rate=$(echo "$line" | jq -r '.details.win_rate' 2>/dev/null)
            total_pnl=$(echo "$line" | jq -r '.details.total_pnl' 2>/dev/null)
            promo=$(echo "$line" | jq -r '.details.promotion_eligible' 2>/dev/null)
            echo -e "\033[1;36m[$timestamp] 🏁 CANARY_SESSION_END\033[0m"
            echo -e "   Win Rate: $win_rate% | P&L: \$$total_pnl | Promotion: $promo"
            ;;
        *)
            echo -e "\033[0;37m[$timestamp] $event_type: $symbol\033[0m"
            ;;
    esac
    echo ""
done
