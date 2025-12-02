#!/bin/bash
# RBOTZILLA System Audit - PIN 841921
# Verify all 130+ features and AI agent nodes

echo "=========================================="
echo "RBOTZILLA SYSTEM AUDIT"
echo "Date: $(date)"
echo "=========================================="
echo ""

# 1. CHECK CORE AI AGENT NODES
echo "=== CORE AI AGENT NODES ==="
agents=(
    "oanda_trading_engine.py:Main Trading Engine"
    "hive/rick_hive_mind.py:RICK Hive Mind Orchestrator"
    "ml_learning/regime_detector.py:ML Regime Detector"
    "ml_learning/signal_analyzer.py:ML Signal Analyzer"
    "systems/momentum_signals.py:Momentum Signal Generator"
    "util/momentum_trailing.py:Smart Trailing Stop System"
    "foundation/rick_charter.py:Charter Compliance Guard"
    "foundation/margin_correlation_gate.py:Margin Gate Agent"
    "brokers/oanda_connector.py:OANDA API Connector"
    "util/rick_narrator.py:RICK Narrator Agent"
    "util/narration_logger.py:Event Logger"
)

for agent in "${agents[@]}"; do
    file="${agent%%:*}"
    name="${agent##*:}"
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        echo "✓ $name"
        echo "  File: $file ($size bytes)"
    else
        echo "✗ $name - FILE MISSING!"
        echo "  Expected: $file"
    fi
done

echo ""
echo "=== CHECKING IF ENGINE IS RUNNING ==="
if pgrep -af "oanda_trading_engine.py" >/dev/null 2>&1; then
    pid=$(pgrep -f "oanda_trading_engine.py")
    echo "✓ Engine RUNNING (PID: $pid)"
    ps -p $pid -o pid,ppid,cmd,%cpu,%mem,etime
else
    echo "✗ Engine NOT RUNNING"
fi

echo ""
echo "=== CHECKING RECENT ACTIVITY ==="
if [ -f "logs/narration.jsonl" ]; then
    echo "Last 5 narration events:"
    tail -5 logs/narration.jsonl | while read line; do
        echo "  $line"
    done
else
    echo "✗ No narration log found"
fi

echo ""
echo "=== CHECKING HIVE MIND FILES ==="
hive_files=(
    "hive/rick_hive_mind.py"
    "hive/swarm_coordinator.py"
    "hive/consensus_engine.py"
)
for f in "${hive_files[@]}"; do
    if [ -f "$f" ]; then
        echo "✓ $f"
    else
        echo "✗ $f MISSING"
    fi
done

echo ""
echo "=== CHECKING ML MODELS ==="
ml_files=(
    "ml_learning/regime_detector.py"
    "ml_learning/signal_analyzer.py"
    "ml_learning/pattern_recognition.py"
)
for f in "${ml_files[@]}"; do
    if [ -f "$f" ]; then
        echo "✓ $f"
    else
        echo "✗ $f MISSING"
    fi
done

echo ""
echo "=========================================="
echo "AUDIT COMPLETE"
echo "=========================================="
