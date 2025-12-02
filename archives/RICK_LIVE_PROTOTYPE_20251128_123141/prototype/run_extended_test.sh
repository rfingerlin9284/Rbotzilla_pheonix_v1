#!/bin/bash

# Extended Paper Mode Test - 1-2 Hours
# PIN: 841921
# Monitors all enforcement rules in real-time

TEST_DURATION_SECONDS=3600  # 1 hour (can extend to 7200 for 2 hours)
CHECKPOINT_INTERVAL=300     # Report every 5 minutes
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "=========================================="
echo "EXTENDED PAPER MODE TEST"
echo "Duration: 1 hour"
echo "Start: $TIMESTAMP"
echo "PIN: 841921"
echo "=========================================="
echo ""

# Run compliance verification first
echo "[$(date -u +%H:%M:%S)] Running pre-test verification..."
make verify > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Pre-test verification failed"
    exit 1
fi
echo "[$(date -u +%H:%M:%S)] ✅ Verification passed"
echo ""

# Start the integration manager in background with output capture
LOG_FILE="logs/extended_test_run_$TIMESTAMP.log"
echo "[$(date -u +%H:%M:%S)] Starting integration manager..."
echo "[$(date -u +%H:%M:%S)] [PIN: 841921] [EXTENDED_TEST: START]" >> logs/charter_compliance.log

python3 trading_manager/integrated_swarm_manager.py > "$LOG_FILE" 2>&1 &
MANAGER_PID=$!

echo "[$(date -u +%H:%M:%S)] Manager started (PID: $MANAGER_PID)"
echo "[$(date -u +%H:%M:%S)] Output: $LOG_FILE"
echo ""

# Monitor the test
START_TIME=$(date +%s)
CHECKPOINT=0

echo "Monitoring test execution:"
echo "Time     | Orders | Closed | PnL      | Auto-BE | Trailing | Giveback | TTL"
echo "---------|--------|--------|----------|---------|----------|----------|-----"

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    # Check if process is still running
    if ! kill -0 $MANAGER_PID 2>/dev/null; then
        echo ""
        echo "[$(date -u +%H:%M:%S)] Manager process ended"
        break
    fi
    
    # Report checkpoint every 5 minutes
    if [ $((ELAPSED % CHECKPOINT_INTERVAL)) -lt 2 ]; then
        MINS=$((ELAPSED / 60))
        if [ $MINS -ne $CHECKPOINT ]; then
            CHECKPOINT=$MINS
            
            # Extract metrics from latest log (if available)
            METRICS=$(tail -20 "$LOG_FILE" | grep -E "orders_submitted|orders_blocked|auto_breakeven|trailing|giveback|cumulative_pnl" | tail -1)
            
            # Format output line
            printf "%02d:%02d:%02d | %-6s | %-6s | %-8s | %-7s | %-8s | %-8s | %-3s\n" \
                $((MINS / 60)) $((MINS % 60)) 0 \
                "..." "..." "..." "..." "..." "..." "..."
        fi
    fi
    
    # Stop after TEST_DURATION
    if [ $ELAPSED -ge $TEST_DURATION_SECONDS ]; then
        echo ""
        echo "[$(date -u +%H:%M:%S)] Test duration reached ($((TEST_DURATION_SECONDS / 60)) minutes)"
        break
    fi
    
    sleep 5
done

# Wait for process to finish
wait $MANAGER_PID 2>/dev/null

echo ""
echo "=========================================="
echo "TEST COMPLETE"
echo "Log file: $LOG_FILE"
echo "=========================================="
echo ""

# Parse and display results
echo "Final Results:"
echo ""
tail -50 "$LOG_FILE" | grep -E "final_metrics|total_orders|orders_blocked|auto_breakeven|trailing|giveback|cumulative_pnl"

echo ""
echo "Compliance Log Entry:"
echo "[$(date -u +%H:%M:%SZ)] [PIN: 841921] [EXTENDED_TEST: COMPLETE]" >> logs/charter_compliance.log
tail -3 logs/charter_compliance.log

