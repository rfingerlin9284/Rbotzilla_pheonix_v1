#!/usr/bin/env bash
# QUICK REFERENCE CARD - Print this for your monitor

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════════╗
║                  RICK AGGRESSIVE MONEY MACHINE - QUICK REF                    ║
║                                                                               ║
║  $5K → $50K in 10 months | 70% win rate | 1min+ timeframes | Autonomous     ║
╚═══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAUNCH COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  START ENGINE:
    bash launch_aggressive_machine.sh

  VERIFY READY:
    python3 aggressive_money_machine.py

  MONITOR LOGS:
    tail -f logs/aggressive_money_machine.log

  WATCH EVENTS:
    tail -f logs/narration.jsonl | jq '.'

  STOP:
    Ctrl+C (emergency close all positions)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTIVE COMPONENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✓ Wolf Pack Selector     │ Regime → Strategy
  ✓ Quant Hedge Engine     │ Conditions → Multiplier  
  ✓ Trailing Stop Manager  │ Profits → Extraction
  ✓ Guardian Gates         │ Charter → Compliance
  ✓ Hive Autonomous Loop   │ Market → Continuous Trading

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WOLF PACK STRATEGIES (Selected by Regime)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  BULLISH (1.3x)   │ RSI bounce + EMA(9)>EMA(21)      │ Aggressive
  BEARISH (1.0x)   │ Reversal bounce + EMA(9)<EMA(21) │ Neutral
  SIDEWAYS (0.8x)  │ Range touches + Support/Res      │ Conservative
  TRIAGE (0.5x)    │ >80% confidence only             │ Safe mode

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUANT HEDGE GATES (Position Sizing)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  VOLATILITY     │ Low: 1.2x │ Mod: 1.0x │ High: 0.7x │ Extreme: 0.3x
  MARGIN         │ <20%: OK  │ 20-30%: 0.8x │ 30-35%: Stop Entry
  CORRELATION    │ Low: OK   │ Mod: 0.9x │ High: BLOCKED
  POSITIONS      │ 0-1: Full │ 2: Caution │ 3: MAX (stop entry)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRAILING STOP PROFIT EXTRACTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  +25 pips   → Move SL to breakeven (zero loss protection)
  +50 pips   → CLOSE 25% (lock profit) | Trail rest @ 10 pips
  +100 pips  → CLOSE 50% more (50% total) | Trail rest @ 5 pips
  +200 pips  → CLOSE last 50% (lock max) | Let runner with 3-pip trail

  Result: Captures profits at each level while maximizing upside

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GUARDIAN GATES (Charter Enforcement)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Margin Cap        │ ≤35% utilization
  Max Positions     │ ≤3 concurrent  
  Correlation       │ Block same-side USD
  Min Notional      │ ≥$15K per trade
  Min Risk-Reward   │ ≥3.2:1 ratio

  All gates must pass before trade execution. None bypass override.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HIVE AUTONOMOUS LOOP (Every 60 seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. DETECT REGIME  → Bull / Bear / Sideways / Triage / Crash
  2. SELECT PACK    → Choose wolf pack strategy
  3. SCAN MARKET    → Find opportunities matching pattern
  4. ANALYZE HEDGE  → Check quant conditions
  5. VALIDATE GATES → Pass guardian gate checks
  6. PLACE TRADE    → OCO with SL + TP
  7. MANAGE POS.    → Tight trailing stops
  8. LOG EVENT      → narration.jsonl
  9. REPEAT         → Sleep 60s, loop again

  Runs continuously without human intervention.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAPITAL GROWTH PATH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Month  │ Capital  │ Deposits │ Trading PnL │ Target
  ───────┼──────────┼──────────┼─────────────┼─────────
    1    │ $9,600   │ $6,000   │ +$3,600     │ 70% win
    3    │ $18,800  │ $8,000   │ +$10,800    │ Paper val
    6    │ $32,600  │ $11,000  │ +$21,600    │ Hybrid mode
    10   │ $51,000  │ $15,000  │ +$36,000    │ ✅ TARGET

  Requires: 70% win rate + $150 avg win / -$150 avg loss

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Q: Not trading?
  A: Check regime (triage = cautious), margin level (>30%?), 
     position count (3 limit?). Review logs/aggressive_money_machine.log

  Q: Trades blocked?
  A: Check narration.jsonl for gate reason. Common: notional < $15K,
     R:R < 3.2, margin > 35%. Adjust config.

  Q: Low win rate?
  A: Too many triage trades? Increase confidence. SL too tight?
     Try 120 pips. Check narration.jsonl for pattern.

  Q: Capital not growing?
  A: Verify win rate is actually 70%+. Risk too high? Lower to 1.5%.
     Check deposits added each month.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  File: config/aggressive_machine_config.py

  Edit these if needed:
    risk_per_trade_pct: 0.02        (2% = aggressive growth)
    trailing_stop_pips: 15          (tight profit extraction)
    max_concurrent: 3               (Charter limit)
    timeframes: ["M1", "M5", "M15"] (1min+ only)

  PIN: 841921 (required for all changes)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE LOCATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Main:        aggressive_money_machine.py
  Config:      config/aggressive_machine_config.py
  Launch:      launch_aggressive_machine.sh
  Logs:        logs/aggressive_money_machine.log
  Events:      logs/narration.jsonl
  Wolf Packs:  logic/regime_detector.py
  Hedging:     hive/quant_hedge_rules.py
  Gates:       foundation/rick_charter.py
  Docs:        AGGRESSIVE_MACHINE_DEPLOYMENT.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PIN: 841921 | Status: READY | Mode: AGGRESSIVE CAPITAL GROWTH

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
