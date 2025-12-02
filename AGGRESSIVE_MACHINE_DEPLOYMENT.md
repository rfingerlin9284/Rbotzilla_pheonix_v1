#!/usr/bin/env python3
"""
🚀 RICK AGGRESSIVE MONEY MACHINE - DEPLOYMENT GUIDE
Full autonomous trading system for capital growth from $5K → $50K

PIN: 841921 | Version: 1.0 | Status: READY FOR DEPLOYMENT
"""

DEPLOYMENT_GUIDE = """
═══════════════════════════════════════════════════════════════════════════════
🚀 RICK AGGRESSIVE MONEY MACHINE - DEPLOYMENT GUIDE
═══════════════════════════════════════════════════════════════════════════════

WHAT IS THIS?
─────────────────────────────────────────────────────────────────────────────
A fully autonomous trading system that combines:

  ✅ WOLF PACK STRATEGIES (4 Regimes)
     - Bullish Wolf Pack (1.3x aggressive)
     - Bearish Wolf Pack (neutral)
     - Sideways/Range Wolf Pack (0.8x conservative)
     - Triage Wolf Pack (0.5x safety mode)

  ✅ QUANT HEDGE MULTI-CONDITION ANALYZER
     - Volatility gates (low/moderate/high/extreme)
     - Margin utilization gates (0-35% Charter max)
     - Correlation detection (same-side USD blocking)
     - Dynamic position scaling

  ✅ SMART TIGHT TRAILING STOPS
     - 15 pips base trailing distance
     - Breakeven activation at +25 pips profit
     - Acceleration: Tighten 5 pips per hour held
     - Multi-level profit taking (25%, 50%, 100%, 200%)

  ✅ RICK HIVE AUTONOMOUS LOOP
     - Real-time regime detection (Bull/Bear/Sideways/Triage)
     - Continuous position monitoring
     - Auto-hedging on inverse pairs
     - Emotional damping (reduce size on streaks)

  ✅ CHARTER ENFORCEMENT (Guardian Gates)
     - Margin cap: 35% maximum utilization
     - Max 3 concurrent positions
     - Correlation checks for USD exposure
     - $15K minimum notional per trade
     - 3.2:1 minimum risk-reward ratio


CAPITAL GROWTH MATH
─────────────────────────────────────────────────────────────────────────────

Starting: $5,000 + $1,000/month deposits
Target:   $50,000 in 10 months
Method:   70% win rate + 2% risk per trade + 3.2:1 R:R ratio

Timeline with 70% Win Rate:
  Month 1:  $9,600  (Deposits: $6K + Trading PnL: $3.6K)
  Month 3:  $18,800 (Deposits: $8K + Trading PnL: $10.8K)
  Month 6:  $32,600 (Deposits: $11K + Trading PnL: $21.6K)
  Month 10: $51,000 ✅ (Deposits: $15K + Trading PnL: $36K)

This requires:
  • 70%+ win rate (system targets 75%)
  • ~60 trades per month (~3 per trading day)
  • $150 average win / -$150 average loss
  • Consistent discipline (no revenge trading)


QUICK START
─────────────────────────────────────────────────────────────────────────────

1. VERIFY SETUP:
   $ python3 -c "from aggressive_money_machine import AggressiveMoneyMachine; m = AggressiveMoneyMachine(pin=841921); print('✅ Ready')"

2. LAUNCH PAPER TRADING:
   $ bash launch_aggressive_machine.sh
   
   OR directly:
   $ python3 aggressive_money_machine.py

3. MONITOR IN REAL-TIME:
   $ tail -f logs/aggressive_money_machine.log
   $ tail -f logs/narration.jsonl | jq '.'

4. CHECK SESSION PERFORMANCE:
   $ python3 -c "import json; trades = json.load(open('logs/session_stats.json')); print(f'Trades: {trades[\"count\"]}, Win Rate: {trades[\"win_pct\"]:.1%}')"


CONFIGURATION
─────────────────────────────────────────────────────────────────────────────

Primary config file: `config/aggressive_machine_config.py`

Key settings:

  Risk Per Trade:              2% (aggressive growth)
  Trailing Stop Distance:      15 pips (tight)
  Max Concurrent Positions:    3 (Charter limit)
  Wolf Pack Multipliers:       0.5x - 1.3x by regime
  Position Scaling:            Kelly Criterion
  Hive Poll Interval:          60 seconds
  Profit Target Levels:        +50%, +100%, +200%


WOLF PACK STRATEGIES EXPLAINED
─────────────────────────────────────────────────────────────────────────────

BULLISH WOLF PACK (1.3x aggressive)
  └─ Detects: Bull trend + oversold RSI bounce
  └─ Entry: EMA(9) > EMA(21) with volume confirmation
  └─ Trailing: Activates at +50% profit
  └─ Risk: Higher but better for trending markets
  └─ Active when: Regime = "bull"

BEARISH WOLF PACK (1.0x normal)
  └─ Detects: Bear trend + overbought RSI bounce  
  └─ Entry: EMA(9) < EMA(21) with volume
  └─ Trailing: Activates at +75% profit (more conservative)
  └─ Risk: Moderate, balanced approach
  └─ Active when: Regime = "bear"

SIDEWAYS WOLF PACK (0.8x conservative)
  └─ Detects: Range-bound, support/resistance bounces
  └─ Entry: Bollinger Band touches, reversal patterns
  └─ Trailing: Activates at +40% profit (quick exits)
  └─ Risk: Lower position size, range-bound thinking
  └─ Active when: Regime = "sideways"

TRIAGE WOLF PACK (0.5x safety)
  └─ Detects: Uncertain markets, low-confidence setups
  └─ Entry: Only >80% confidence setups
  └─ Trailing: Tight 100% (immediate profit-taking)
  └─ Risk: Lowest position size
  └─ Active when: Regime = "triage" or high volatility


QUANT HEDGE RULES DECISION TREE
─────────────────────────────────────────────────────────────────────────────

Market Condition Analysis:

  1. VOLATILITY CHECK
     - Low (0-1.5%): Position multiplier = 1.2x (aggressive)
     - Moderate (1.5-3%): Position multiplier = 1.0x (normal)
     - High (3-5%): Position multiplier = 0.7x (conservative)
     - Extreme (5%+): Position multiplier = 0.3x (minimal)

  2. MARGIN UTILIZATION CHECK
     - Safe (<20%): Full trading allowed
     - Cautious (20-30%): Scale positions down 20%
     - Warning (30-35%): Reduce new entries by 50%
     - Critical (>35%): NO NEW ENTRIES, close positions

  3. CORRELATION CHECK
     - Low correlation: Trade normally
     - Moderate: Reduce by 10%
     - High: Block (same-side USD exposure)
     - Extreme: Force close correlated positions

  4. OPEN POSITIONS CHECK
     - 0-1 positions: Full trading
     - 2 positions: Medium caution
     - 3 positions: No new entries (max reached)

  → RESULT: Position size multiplier applied to all trades


TIGHT TRAILING STOP MECHANISM
─────────────────────────────────────────────────────────────────────────────

The machine uses multi-stage profit-taking:

  Stage 1: ENTRY → +25 PIPS
    └─ Status: No action, just moving with position
    └─ Trail distance: 15 pips

  Stage 2: +25 TO +50 PIPS
    └─ Status: Move stop to breakeven (0 loss)
    └─ Trail distance: 15 pips
    └─ Action: "Breakeven hunting"

  Stage 3: +50 PIPS (LEVEL 1 TARGET)
    └─ Status: Close 25% of position, lock profit
    └─ Trail distance: 10 pips on remaining 75%
    └─ Action: "First profit level"

  Stage 4: +100 PIPS (LEVEL 2 TARGET)
    └─ Status: Close 50% of remaining (50% total), increase trail
    └─ Trail distance: 5 pips on remaining 50%
    └─ Action: "Second profit level"

  Stage 5: +200 PIPS (LEVEL 3 TARGET)
    └─ Status: Close final 50%, lock maximum profit
    └─ Trail distance: 3 pips on runner position
    └─ Action: "Let runner ride"

Result: Captures profit at multiple levels while maximizing upside on runners


RICK HIVE AUTONOMOUS CLOSED LOOP
─────────────────────────────────────────────────────────────────────────────

The Hive continuously (every 60 seconds):

  1. SENSE: Poll market regime, prices, volatility
  2. THINK: Analyze conditions, detect opportunities
  3. ACT: Place trades matching wolf pack strategy + quant hedge
  4. MONITOR: Manage open positions with tight trailing
  5. LEARN: Track win rate, adjust position sizing
  6. REPEAT: Loop back to step 1

This closed loop runs without human intervention. It:
  ✅ Detects regime changes automatically
  ✅ Switches wolf pack strategies mid-session if needed
  ✅ Scales positions based on performance
  ✅ Tightens trailing stops to lock profits
  ✅ Blocks trades that violate guardian gates
  ✅ Logs everything to narration.jsonl for audit


ACTIVE COMPONENTS (WHAT'S RUNNING)
─────────────────────────────────────────────────────────────────────────────

When you launch the machine:

  ✅ Regime Detector (StochasticRegimeDetector)
     Continuously classifies market as: Bull/Bear/Sideways/Triage/Crash

  ✅ Wolf Pack Orchestrator
     Selects strategy based on regime:
     - Bull market → Use Bullish Wolf Pack (1.3x)
     - Bear market → Use Bearish Wolf Pack (1.0x)
     - Ranging market → Use Sideways Wolf Pack (0.8x)
     - Uncertain → Use Triage Wolf Pack (0.5x safety)

  ✅ Quant Hedge Engine
     Real-time multi-condition analysis:
     - Checks volatility level
     - Checks margin utilization
     - Checks correlation risks
     - Outputs position multiplier (0.3x - 1.2x)

  ✅ Guardian Gates
     Pre-trade validation (ALL must pass):
     ① Margin check (≤35%)
     ② Position count check (≤3)
     ③ Correlation check (no same-side USD)
     ④ Notional check (≥$15K)
     ④ R:R ratio check (≥3.2:1)

  ✅ Trade Execution Engine
     Places OCO orders with:
     - Entry price (calculated from regime)
     - Stop loss (SL = entry ± 100 pips)
     - Take profit (TP = SL × 3.2, minimum Charter ratio)
     - Position size (calculated from quant hedge)

  ✅ Position Manager
     Monitors all open trades:
     - Updates trailing stops (15 pips tight)
     - Checks TP/SL hits
     - Manages multi-level profit taking
     - Logs exit reason (TP_HIT, SL_HIT, TRAILING, TIME_OUT)

  ✅ Narration Logger
     Continuous event logging to narration.jsonl:
     - TRADE_OPENED: New entry
     - TRADE_CLOSED: Exit reason + P&L
     - MACHINE_HEARTBEAT: Session stats
     - REGIME_CHANGE: Detected market shift
     - HEDGE_DECISION: Why position scaled
     - GUARDIAN_GATE: Trade rejected reason


PERFORMANCE METRICS (What Success Looks Like)
─────────────────────────────────────────────────────────────────────────────

After 1 Month (Target):
  ✅ 60 trades executed
  ✅ 70% win rate (42 wins, 18 losses)
  ✅ Average win: +$150
  ✅ Average loss: -$150
  ✅ Total PnL: +$3,600
  ✅ Capital: $9,600 (from $6K starting)
  ✅ Risk/Reward: Consistently >3.2:1

After 10 Months (Target):
  ✅ 600 trades executed
  ✅ 70% win rate (420 wins, 180 losses)
  ✅ Total PnL: +$36,000
  ✅ Capital: $51,000+ ✅
  ✅ Ready for $15K notional trades with full Charter compliance


EMERGENCY PROCEDURES
─────────────────────────────────────────────────────────────────────────────

STOP IMMEDIATELY:
  $ pkill -f aggressive_money_machine

EMERGENCY CLOSE ALL:
  Press Ctrl+C during execution
  System will force-close all open positions at market

CHECK FOR VIOLATIONS:
  $ grep "CHARTER_VIOLATION" logs/aggressive_money_machine.log
  $ grep "GUARDIAN_GATE_BLOCKED" logs/narration.jsonl

REVIEW SESSION:
  $ python3 -c "
  import json
  from pathlib import Path
  logs = Path('logs/narration.jsonl').read_text().split('\\n')
  trades = [json.loads(l) for l in logs if 'TRADE' in l]
  print(f'Total trades: {len(trades)}')
  for t in trades[-10:]:
      print(f'  {t.get(\"event_type\")}: {t.get(\"details\", {}).get(\"symbol\")}')
  "


TROUBLESHOOTING
─────────────────────────────────────────────────────────────────────────────

"Not trading"
  └─ Check: Is regime = "triage"? (low confidence, trade carefully)
  └─ Check: Is margin utilization > 30%? (quant hedge scaling down)
  └─ Check: Are there 3+ open positions? (max reached)
  └─ Check: logs/aggressive_money_machine.log for errors

"Trades getting blocked"
  └─ Check: Guardian gate reason in narration.jsonl
  └─ Common: Notional < $15K → increase position size in config
  └─ Common: R:R < 3.2 → increase TP distance
  └─ Common: Margin > 35% → close some positions

"Low win rate"
  └─ Too many triage trades? → Increase confidence threshold
  └─ Wolf pack not matching market? → Check regime detection
  └─ SL too tight? → Increase from 100 to 120 pips
  └─ Trailing stops cutting profits? → Increase 15 to 20 pips

"Capital not growing"
  └─ Is win rate actually 70%+? → Check narration.jsonl
  └─ Are losing trades too large? → Reduce risk_per_trade_pct
  └─ Are deposits being added? → Check capital_manager.py
  └─ Is system actually trading? → Check trade_history


FILE LOCATIONS
─────────────────────────────────────────────────────────────────────────────

Main Engine:
  aggressive_money_machine.py          ← Main autonomous loop
  config/aggressive_machine_config.py  ← Configuration (edit here)
  launch_aggressive_machine.sh         ← Quick start launcher

Core Systems:
  foundation/rick_charter.py           ← Guardian gates
  logic/regime_detector.py             ← Wolf pack selector
  hive/quant_hedge_rules.py            ← Multi-condition analyzer
  brokers/oanda_connector.py           ← Trade execution
  capital_manager.py                   ← Capital tracking

Logs:
  logs/aggressive_money_machine.log    ← Full debug logs
  logs/narration.jsonl                 ← Event stream
  logs/session_stats.json              ← Summary metrics


NEXT STEPS
─────────────────────────────────────────────────────────────────────────────

1. VALIDATE SETUP
   $ python3 aggressive_money_machine.py  (starts loop)

2. MONITOR FOR 1 HOUR
   $ tail -f logs/narration.jsonl | jq -r '.event_type + ": " + (.details.symbol // "SYSTEM")'

3. CHECK PERFORMANCE
   Month 1: Target ≥70% win rate + $3.6K profit
   Month 3: Target $18.8K capital
   Month 10: Target $51K capital ✅

4. SCALE UP
   Once proven on paper trading → Switch to live with confidence


═══════════════════════════════════════════════════════════════════════════════
PIN: 841921 | Status: READY FOR AGGRESSIVE CAPITAL GROWTH
═══════════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(DEPLOYMENT_GUIDE)
    
    # Save to file
    Path("AGGRESSIVE_MACHINE_DEPLOYMENT.md").write_text(DEPLOYMENT_GUIDE)
    print("\n✅ Saved to: AGGRESSIVE_MACHINE_DEPLOYMENT.md")
