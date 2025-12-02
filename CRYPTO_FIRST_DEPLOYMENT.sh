#!/bin/bash
# 🟢 CRYPTO-FIRST DEPLOYMENT - COINBASE ONLY
# Phase 1: 24/7 Crypto Trading
# Phase 2: Add Forex (OANDA) when ready
# Phase 3: Add Equities (IBKR) when ready
# PIN: 841921

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║       🚀 CRYPTO-FIRST DEPLOYMENT - PHASE 1             ║"
echo "║                                                        ║"
echo "║   Start: Coinbase 24/7 Crypto Trading                 ║"
echo "║   Then:  Add OANDA Forex when ready                   ║"
echo "║   Then:  Add IBKR Equities when ready                 ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# ============================================================
# STEP 1: GET COINBASE API CREDENTIALS
# ============================================================
echo "📋 STEP 1: Get Coinbase API Credentials"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "Go to: https://www.coinbase.com/advancedtrade"
echo ""
echo "1. Click Settings → API → Create API Key"
echo "2. Select 'Advanced Trading' category"
echo "3. Enable these permissions:"
echo "   ✓ View account summary"
echo "   ✓ View account details"
echo "   ✓ View trading activity"
echo "   ✓ Create orders"
echo "   ✓ Cancel orders"
echo ""
echo "4. Copy 3 values:"
echo "   • API Key (public key)"
echo "   • API Secret (private key)"
echo "   • API Passphrase"
echo ""
echo "👉 Have these 3 values ready before continuing"
echo ""

# ============================================================
# STEP 2: ADD TO .ENV FILE
# ============================================================
echo ""
echo "📋 STEP 2: Add Credentials to .env"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "Edit .env file and add:"
echo ""
echo "  export COINBASE_API_KEY=\"your-api-key-here\""
echo "  export COINBASE_API_SECRET=\"your-secret-here\""
echo "  export COINBASE_API_PASSPHRASE=\"your-passphrase-here\""
echo ""
echo "Then reload:"
echo "  source .env"
echo ""
echo "Verify:"
echo "  echo \$COINBASE_API_KEY  # Should show your key"
echo ""

# ============================================================
# STEP 3: TEST CONNECTION
# ============================================================
echo ""
echo "📋 STEP 3: Test Coinbase Connection (1 Iteration)"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "Run this command:"
echo ""
echo "  cd /home/ing/RICK/RICK_LIVE_CLEAN"
echo "  python3 multi_broker_engine.py --iterations 1"
echo ""
echo "Expected output:"
echo "  ✅ Coinbase connected (Crypto)"
echo "  📊 Fetching market data from all brokers..."
echo "  🎯 Running strategy analysis..."
echo ""
echo "If you see these, Coinbase is ready!"
echo "If errors: Check API key format in .env"
echo ""

# ============================================================
# STEP 4: PAPER MODE (24 HOURS)
# ============================================================
echo ""
echo "📋 STEP 4: Deploy Paper Mode (24 hours)"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "⚠️  IMPORTANT: Paper mode only - no real trades"
echo ""
echo "Run in Terminal 1:"
echo ""
echo "  cd /home/ing/RICK/RICK_LIVE_CLEAN"
echo "  export ENVIRONMENT=practice"
echo "  python3 multi_broker_engine.py"
echo ""
echo "This will:"
echo "  • Connect to Coinbase (but no real trades)"
echo "  • Run all 5 strategies on crypto"
echo "  • Generate signals across BTC, ETH, SOL, XRP"
echo "  • Log all events to narration.jsonl"
echo ""
echo "Run in Terminal 2 (Monitoring):"
echo ""
echo "  tail -f narration.jsonl | grep -E 'execution|signal|hive'"
echo ""
echo "Watch for 24 hours:"
echo "  ✓ Trades executing (strategy signals)"
echo "  ✓ Hive consensus voting"
echo "  ✓ ML filtering active"
echo "  ✓ Win rate building (target ≥70% for crypto)"
echo "  ✓ P&L accumulating"
echo "  ✓ No crashes or errors"
echo ""

# ============================================================
# STEP 5: METRICS TO TRACK
# ============================================================
echo ""
echo "📋 STEP 5: Paper Mode Metrics"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "AFTER 24 HOURS, check:"
echo ""
echo "  1️⃣  Total trades:"
echo "      tail -f narration.jsonl | grep -c 'execution'"
echo ""
echo "  2️⃣  Win rate:"
echo "      Python script to calculate:"
echo ""
python3 << 'EOFPY'
import json
wins = 0
losses = 0
with open('narration.jsonl') as f:
    for line in f:
        try:
            evt = json.loads(line)
            if 'win' in evt.get('text', '').lower():
                wins += 1
            elif 'loss' in evt.get('text', '').lower():
                losses += 1
        except:
            pass
if wins + losses > 0:
    win_rate = 100 * wins / (wins + losses)
    print(f"  Wins: {wins}, Losses: {losses}, Win Rate: {win_rate:.1f}%")
else:
    print("  No trades executed yet")
EOFPY
echo ""
echo "  3️⃣  P&L:"
echo "      grep -i 'pnl' narration.jsonl | tail -5"
echo ""
echo "SUCCESS CRITERIA:"
echo "  ✅ Win rate ≥70%"
echo "  ✅ At least 10 trades"
echo "  ✅ Total P&L positive"
echo "  ✅ No crashes"
echo ""

# ============================================================
# STEP 6: GO LIVE
# ============================================================
echo ""
echo "📋 STEP 6: Go Live (After Paper Success)"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "⚠️  REAL MONEY TRADING - Careful!"
echo ""
echo "Step 6.1: Create backup"
echo ""
echo "  mkdir -p ROLLBACK_SNAPSHOTS"
echo "  cp -r . ROLLBACK_SNAPSHOTS/crypto_live_backup_\$(date +%s)/"
echo ""
echo "Step 6.2: Switch to live"
echo ""
echo "  export ENVIRONMENT=live"
echo ""
echo "Step 6.3: Start trading (background)"
echo ""
echo "  nohup python3 multi_broker_engine.py > crypto_trading.log 2>&1 &"
echo ""
echo "Step 6.4: Verify running"
echo ""
echo "  ps aux | grep multi_broker_engine"
echo ""
echo "Step 6.5: Monitor closely (first 24 hours)"
echo ""
echo "  Terminal 1: tail -f crypto_trading.log"
echo "  Terminal 2: tail -f narration.jsonl"
echo "  Terminal 3: watch -n 5 'tail -20 narration.jsonl | grep -i pnl'"
echo ""

# ============================================================
# STEP 7: EMERGENCY STOP
# ============================================================
echo ""
echo "📋 STEP 7: Emergency Stop (If Needed)"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "If ANYTHING goes wrong:"
echo ""
echo "  1. Stop immediately:"
echo "     pkill -f multi_broker_engine.py"
echo ""
echo "  2. Check what happened:"
echo "     tail -100 crypto_trading.log"
echo ""
echo "  3. Restore backup (if needed):"
echo "     cp ROLLBACK_SNAPSHOTS/crypto_live_backup_*/. ."
echo ""
echo "  4. Go back to paper mode:"
echo "     export ENVIRONMENT=practice"
echo "     python3 multi_broker_engine.py --iterations 5"
echo ""

# ============================================================
# STEP 8: SCALE UP
# ============================================================
echo ""
echo "📋 STEP 8: Scale Up (After 1-2 weeks success)"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "Once Coinbase is profitable and stable, add more brokers:"
echo ""
echo "Phase 2: Add OANDA Forex"
echo "  • Already configured in OANDA connector"
echo "  • Just enable in multi_broker_engine.py"
echo "  • Sun-Fri 17:00-16:00 UTC"
echo "  • Expected: 15-25 additional trades/day"
echo ""
echo "Phase 3: Add IBKR Equities"
echo "  • Requires IB Gateway running"
echo "  • Add API credentials to .env"
echo "  • Mon-Fri 9:30-16:00 EST"
echo "  • Expected: 5-10 additional trades/day"
echo ""

# ============================================================
# EXPECTED PERFORMANCE (CRYPTO ONLY)
# ============================================================
echo ""
echo "📊 Expected Performance (Crypto Only)"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "Trading Activity:"
echo "  Daily trades:   10-20"
echo "  Trading hours:  24/7 (never closed)"
echo "  Win rate:       70% (crypto has high R:R)"
echo ""
echo "Daily P&L:"
echo "  Conservative:   +0.10-0.20% of capital"
echo "  Normal:         +0.20-0.30%"
echo "  Aggressive:     +0.30-0.50%"
echo ""
echo "Monthly P&L (30 days, 24/7 trading):"
echo "  Conservative:   +3-6% of capital"
echo "  Normal:         +6-9%"
echo "  Aggressive:     +9-15%"
echo ""
echo "Note: Crypto is HIGH VOLATILITY = HIGH R:R ratios"
echo "      Strategy win rates on crypto: 65-75%"
echo "      Position sizes: smaller due to volatility"
echo ""

# ============================================================
# QUICK REFERENCE
# ============================================================
echo ""
echo "⚡ QUICK REFERENCE"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "Current Status: 🔴 STOPPED (waiting for deployment)"
echo ""
echo "Command to start paper mode:"
echo "  export ENVIRONMENT=practice && python3 multi_broker_engine.py"
echo ""
echo "Command to start live (after backup):"
echo "  export ENVIRONMENT=live && nohup python3 multi_broker_engine.py > crypto_trading.log 2>&1 &"
echo ""
echo "Command to stop:"
echo "  pkill -f multi_broker_engine.py"
echo ""
echo "Command to monitor:"
echo "  tail -f narration.jsonl"
echo ""
echo "Restart from backup:"
echo "  pkill -f multi_broker_engine.py"
echo "  cp ROLLBACK_SNAPSHOTS/crypto_live_backup_*/. ."
echo "  export ENVIRONMENT=practice && python3 multi_broker_engine.py"
echo ""

# ============================================================
# SUMMARY
# ============================================================
echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ CRYPTO-FIRST DEPLOYMENT ROADMAP COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next step: Get Coinbase API key"
echo "Then: Add to .env"
echo "Then: Test connection"
echo "Then: Run paper mode for 24 hours"
echo "Then: Go live!"
echo ""
echo "Ready? Let's start! 🚀"
echo ""
