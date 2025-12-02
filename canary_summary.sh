#!/bin/bash
# CANARY Session Summary
# Summarize narration events from current session
# PIN: 841921

NARRATION_LOG="/home/ing/RICK/RICK_LIVE_CLEAN/pre_upgrade/headless/logs/narration.jsonl"

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🐤 CANARY SESSION SUMMARY                                 ║"
echo "║                    Charter-Compliant Event Analysis                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if narration log exists
if [ ! -f "$NARRATION_LOG" ]; then
    echo "❌ Narration log not found: $NARRATION_LOG"
    exit 1
fi

# Count events by type
echo "📊 Event Counts:"
echo "───────────────────────────────────────────────────────────────────────────────"
cat "$NARRATION_LOG" | jq -r '.event_type' | sort | uniq -c | while read -r count event; do
    case "$event" in
        "CANARY_INIT") icon="🐤" ;;
        "CANARY_SESSION_START") icon="🚀" ;;
        "SIGNAL_GENERATED") icon="📊" ;;
        "SIGNAL_REJECTED") icon="❌" ;;
        "TRADE_OPENED") icon="🟢" ;;
        "TRADE_CLOSED") icon="🔴" ;;
        "TTL_ENFORCEMENT") icon="⏰" ;;
        "CANARY_SESSION_END") icon="🏁" ;;
        *) icon="📝" ;;
    esac
    printf "  %s %-25s %3d\n" "$icon" "$event" "$count"
done
echo ""

# Session info
echo "📋 Session Information:"
echo "───────────────────────────────────────────────────────────────────────────────"
session_start=$(cat "$NARRATION_LOG" | jq -r 'select(.event_type == "CANARY_SESSION_START") | .details.start_time' | head -1)
session_end_planned=$(cat "$NARRATION_LOG" | jq -r 'select(.event_type == "CANARY_SESSION_START") | .details.end_time' | head -1)
starting_capital=$(cat "$NARRATION_LOG" | jq -r 'select(.event_type == "CANARY_SESSION_START") | .details.starting_capital' | head -1)

if [ -n "$session_start" ]; then
    echo "  Start Time:       $session_start"
    echo "  Planned End:      $session_end_planned"
    echo "  Starting Capital: \$$starting_capital"
fi
echo ""

# Charter rules
echo "⚖️  Charter Rules (from session start):"
echo "───────────────────────────────────────────────────────────────────────────────"
cat "$NARRATION_LOG" | jq -r 'select(.event_type == "CANARY_SESSION_START") | .details.charter_rules | to_entries[] | "  \(.key): \(.value)"' | head -4
echo ""

# Trade statistics
echo "📈 Trade Statistics:"
echo "───────────────────────────────────────────────────────────────────────────────"
trades_opened=$(cat "$NARRATION_LOG" | jq -s '[.[] | select(.event_type == "TRADE_OPENED")] | length')
trades_closed=$(cat "$NARRATION_LOG" | jq -s '[.[] | select(.event_type == "TRADE_CLOSED")] | length')
trades_open=$((trades_opened - trades_closed))

echo "  Trades Opened:    $trades_opened"
echo "  Trades Closed:    $trades_closed"
echo "  Currently Open:   $trades_open"
echo ""

# Win/Loss breakdown
if [ "$trades_closed" -gt 0 ]; then
    echo "💰 P&L Breakdown:"
    echo "───────────────────────────────────────────────────────────────────────────────"
    
    wins=$(cat "$NARRATION_LOG" | jq -s '[.[] | select(.event_type == "TRADE_CLOSED" and .details.outcome == "win")] | length')
    losses=$(cat "$NARRATION_LOG" | jq -s '[.[] | select(.event_type == "TRADE_CLOSED" and .details.outcome == "loss")] | length')
    
    if [ "$trades_closed" -gt 0 ]; then
        win_rate=$(echo "scale=1; $wins * 100 / $trades_closed" | bc)
    else
        win_rate="0.0"
    fi
    
    echo "  Wins:             $wins"
    echo "  Losses:           $losses"
    echo "  Win Rate:         ${win_rate}%"
    echo ""
    
    # Show last few closed trades
    echo "  Recent Trades:"
    cat "$NARRATION_LOG" | jq -r 'select(.event_type == "TRADE_CLOSED") | "    [\(.timestamp | split("T")[1] | split("+")[0])] \(.symbol) - \(.details.outcome | ascii_upcase) - P&L: $\(.details.pnl)"' | tail -5
    echo ""
fi

# Signals
signals_generated=$(cat "$NARRATION_LOG" | jq -s '[.[] | select(.event_type == "SIGNAL_GENERATED")] | length')
signals_rejected=$(cat "$NARRATION_LOG" | jq -s '[.[] | select(.event_type == "SIGNAL_REJECTED")] | length')

if [ "$signals_generated" -gt 0 ] || [ "$signals_rejected" -gt 0 ]; then
    echo "📊 Signal Analysis:"
    echo "───────────────────────────────────────────────────────────────────────────────"
    echo "  Signals Generated: $signals_generated"
    echo "  Signals Rejected:  $signals_rejected"
    
    if [ "$signals_generated" -gt 0 ]; then
        execution_rate=$(echo "scale=1; $signals_generated * 100 / ($signals_generated + $signals_rejected)" | bc 2>/dev/null || echo "100.0")
        echo "  Execution Rate:    ${execution_rate}%"
    fi
    echo ""
fi

# Session end info (if available)
session_end=$(cat "$NARRATION_LOG" | jq -r 'select(.event_type == "CANARY_SESSION_END")' 2>/dev/null)
if [ -n "$session_end" ]; then
    echo "🏁 Final Session Results:"
    echo "───────────────────────────────────────────────────────────────────────────────"
    echo "$session_end" | jq -r '.details | "  Total P&L:         $\(.total_pnl)\n  Return:            \(.return_pct)%\n  Ending Capital:    $\(.ending_capital)\n  Promotion Eligible: \(.promotion_eligible)"'
    echo ""
fi

echo "───────────────────────────────────────────────────────────────────────────────"
echo "📝 Full narration log: $NARRATION_LOG"
echo "🔄 Monitor live: ./monitor_narration.sh"
echo ""
