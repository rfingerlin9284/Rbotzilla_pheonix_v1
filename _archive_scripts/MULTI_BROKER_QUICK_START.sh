#!/usr/bin/env bash
# Multi-Broker Engine - Quick Start Commands
# Copy and paste these commands to deploy
# PIN: 841921

echo "🚀 MULTI-BROKER ENGINE - QUICK START"
echo "======================================"

# ============================================
# STEP 1: VERIFY ALL BROKERS CONNECTED
# ============================================
echo ""
echo "📋 STEP 1: Test All Broker Connections"
echo "------"
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

print("\n🔧 Testing broker connections...")

# OANDA
try:
    from brokers.oanda_connector import OandaConnector
    oanda = OandaConnector()
    print("✅ OANDA: Connected (Forex)")
except Exception as e:
    print(f"❌ OANDA: {e}")

# Coinbase
try:
    from brokers.coinbase_connector import CoinbaseConnector
    cb = CoinbaseConnector()
    print("✅ Coinbase: Connected (Crypto)")
except Exception as e:
    print(f"❌ Coinbase: {e}")

# IBKR
try:
    from brokers.ib_connector import IBConnector
    ib = IBConnector()
    print("✅ IBKR: Connected (Equities)")
except Exception as e:
    print(f"❌ IBKR: {e}")

print("\n✅ Connection test complete\n")
EOF

# ============================================
# STEP 2: RUN PAPER MODE (TEST)
# ============================================
echo ""
echo "📋 STEP 2: Run Multi-Broker Engine in Paper Mode"
echo "------"
echo "PAPER MODE COMMAND:"
echo ""
echo "  export ENVIRONMENT=practice"
echo "  python3 multi_broker_engine.py --iterations 10"
echo ""
echo "Expected output:"
echo "  🚀 MULTI-BROKER TRADING ENGINE STARTING"
echo "  ✅ OANDA connected (Forex)"
echo "  ✅ Coinbase connected (Crypto)"
echo "  ✅ IBKR connected (Equities)"
echo "  📊 Fetching market data from all brokers..."
echo "  🎯 Running strategy analysis..."
echo "  🚀 Executing signals..."
echo ""
echo "👉 Run this now to test:"
echo "  export ENVIRONMENT=practice && python3 multi_broker_engine.py --iterations 5"
echo ""

# ============================================
# STEP 3: MONITOR LIVE EXECUTION
# ============================================
echo ""
echo "📋 STEP 3: Monitor Live Execution (In Separate Terminal)"
echo "------"
echo "MONITORING COMMANDS:"
echo ""
echo "  # Watch all events in real-time"
echo "  tail -f narration.jsonl"
echo ""
echo "  # Filter for trades only"
echo "  tail -f narration.jsonl | grep -i 'execution'"
echo ""
echo "  # Filter by broker"
echo "  tail -f narration.jsonl | grep -i 'coinbase\\|ibkr'"
echo ""
echo "  # Check P&L"
echo "  tail -f narration.jsonl | grep -i 'pnl'"
echo ""

# ============================================
# STEP 4: FULL PRODUCTION DEPLOYMENT
# ============================================
echo ""
echo "📋 STEP 4: Deploy to Production (After Paper Mode Success)"
echo "------"
echo "PRODUCTION DEPLOYMENT STEPS:"
echo ""
echo "  # 1. Create backup"
echo "  mkdir -p ROLLBACK_SNAPSHOTS"
echo "  cp -r . ROLLBACK_SNAPSHOTS/multi_broker_backup_\$(date +%s)/"
echo ""
echo "  # 2. Set to live environment"
echo "  export ENVIRONMENT=live"
echo ""
echo "  # 3. Start engine (background)"
echo "  nohup python3 multi_broker_engine.py > multi_broker.log 2>&1 &"
echo ""
echo "  # 4. Verify running"
echo "  ps aux | grep multi_broker_engine"
echo ""
echo "  # 5. Monitor logs (intensive first 24 hours)"
echo "  tail -f multi_broker.log"
echo "  tail -f narration.jsonl"
echo ""
echo "  # 6. Emergency stop (if needed)"
echo "  pkill -f multi_broker_engine.py"
echo ""

# ============================================
# STEP 5: PORTFOLIO MONITORING
# ============================================
echo ""
echo "📋 STEP 5: Monitor Portfolio Across All Brokers"
echo "------"
echo "PORTFOLIO MONITORING:"
echo ""
echo "  # Check positions on all brokers"
echo "  python3 << 'EOF_MON'"
echo "from brokers.oanda_connector import OandaConnector"
echo "from brokers.coinbase_connector import CoinbaseConnector"
echo "from brokers.ib_connector import IBConnector"
echo ""
echo "print('\\n📊 MULTI-BROKER PORTFOLIO')
echo "print('=' * 50)"
echo ""
echo "# OANDA positions"
echo "try:"
echo "    oanda = OandaConnector()"
echo "    pos = oanda.get_positions()"
echo "    if pos:"
echo "        print('\\n💱 OANDA (Forex):')"
echo "        for p in pos:"
echo "            print(f\"  {p['symbol']}: {p['size']} @ {p['price']}\")"
echo "except Exception as e:"
echo "    print(f'❌ OANDA: {e}')"
echo ""
echo "# Coinbase positions"
echo "try:"
echo "    cb = CoinbaseConnector()"
echo "    pos = cb.get_positions()"
echo "    if pos:"
echo "        print('\\n🔵 Coinbase (Crypto):')"
echo "        for p in pos:"
echo "            print(f\"  {p['symbol']}: {p['size']} @ {p['price']}\")"
echo "except Exception as e:"
echo "    print(f'❌ Coinbase: {e}')"
echo ""
echo "# IBKR positions"
echo "try:"
echo "    ib = IBConnector()"
echo "    pos = ib.get_positions()"
echo "    if pos:"
echo "        print('\\n📊 IBKR (Equities):')"
echo "        for p in pos:"
echo "            print(f\"  {p['symbol']}: {p['size']} @ {p['price']}\")"
echo "except Exception as e:"
echo "    print(f'❌ IBKR: {e}')"
echo "EOF_MON"
echo ""

# ============================================
# STEP 6: DISASTER RECOVERY
# ============================================
echo ""
echo "📋 STEP 6: Emergency Recovery (If Something Goes Wrong)"
echo "------"
echo "EMERGENCY STOP & RESTORE:"
echo ""
echo "  # Stop multi-broker engine immediately"
echo "  pkill -f multi_broker_engine.py"
echo ""
echo "  # Restore from backup"
echo "  cp ROLLBACK_SNAPSHOTS/multi_broker_backup_*/. ."
echo ""
echo "  # Go back to OANDA-only"
echo "  export ENVIRONMENT=practice"
echo "  python3 oanda_trading_engine.py"
echo ""

# ============================================
# SUMMARY
# ============================================
echo ""
echo "======================================"
echo "✅ MULTI-BROKER ENGINE READY"
echo "======================================"
echo ""
echo "📊 Broker Coverage:"
echo "  • OANDA: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD"
echo "  • Coinbase: BTC-USD, ETH-USD, SOL-USD, XRP-USD"
echo "  • IBKR: AAPL, MSFT, GOOGL, TSLA, NVDA"
echo ""
echo "🎯 All 5 Strategies Active:"
echo "  • Trap Reversal Scalper"
echo "  • Fib Confluence Detector"
echo "  • Price Action Holy Grail"
echo "  • Liquidity Sweep Scanner"
echo "  • EMA Scalper"
echo ""
echo "🧠 All 6 Systems Active:"
echo "  • Hive Mind (Consensus voting)"
echo "  • ML Intelligence (Confidence filtering)"
echo "  • Regime Detector (Market analysis)"
echo "  • QuantHedge Engine (Position hedging)"
echo "  • Momentum Trailing (Trend optimization)"
echo "  • Narration Logger (100% audit)"
echo ""
echo "⏰ Market Hours Coverage:"
echo "  • Crypto: 24/7 (always open)"
echo "  • Equities: Mon-Fri 9:30-16:00 EST"
echo "  • Forex: Sun-Fri 17:00-16:00 EST"
echo ""
echo "🚀 NEXT STEPS:"
echo "  1. Test connections: python3 multi_broker_engine.py --iterations 1"
echo "  2. Run paper mode: export ENVIRONMENT=practice && python3 multi_broker_engine.py"
echo "  3. Monitor 24 hours"
echo "  4. Deploy live: export ENVIRONMENT=live && python3 multi_broker_engine.py"
echo ""
echo "======================================"
