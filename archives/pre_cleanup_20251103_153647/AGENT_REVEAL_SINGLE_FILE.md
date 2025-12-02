# AGENT REVEAL – SINGLE FILE
_Generated: 2025-10-26T21:47:14.554122 • PIN: 841921_

## Scope & What This File Proves

This report reveals exactly what exists for:
- Wolf-pack routing `wolf_packs/orchestrator.py`
- Quant Hedge Rules `hive/quant_hedge_rules.py`
- Charter engine `ghost_trading_charter_compliant.py`
- Guardian gates `hive/guardian_gates.py`
- Crypto entry gates `hive/crypto_entry_gate_system.py`
- Regime detector `logic/regime_detector.py`
- Correlation monitor `util/correlation_monitor.py`
- Dynamic sizing `risk/dynamic_sizing.py`
- Log evidence `logs/narration.jsonl`

## Existence Check (must-have files)

```bash
[OK]   ghost_trading_charter_compliant.py
[OK]   wolf_packs/orchestrator.py
[OK]   hive/quant_hedge_rules.py
[OK]   hive/guardian_gates.py
[OK]   hive/crypto_entry_gate_system.py
[OK]   logic/regime_detector.py
[OK]   util/correlation_monitor.py
[OK]   risk/dynamic_sizing.py
[MISS] logs/narration.jsonl
```

## Quick Grep: Installer Hooks?

```bash
./hive/quant_hedge_rules.py:90:class QuantHedgeRules:
./hive/quant_hedge_rules.py:98:            raise PermissionError("Invalid PIN for QuantHedgeRules")
./hive/quant_hedge_rules.py:121:        self.logger.info("QuantHedgeRules initialized with PIN verification")
./hive/quant_hedge_rules.py:585:        qh = QuantHedgeRules(pin=841921)
./hive/quant_hedge_rules.py:615:        print("\n✅ QuantHedgeRules module validated")
```

## Key Files with Context

### hive/quant_hedge_rules.py
```python
#!/usr/bin/env python3
"""
Quant Hedge Rules System - Multi-Condition Analysis Engine
Analyzes market conditions and provides hedging/positioning recommendations
PIN: 841921 | Phase: Active Analysis
"""

import numpy as np
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.rick_charter import RickCharter
from logic.regime_detector import StochasticRegimeDetector, MarketRegime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HedgeAction(Enum):
    """Recommended hedge actions based on market conditions"""
    FULL_LONG = "full_long"           # Aggressive long positions
    MODERATE_LONG = "moderate_long"    # Conservative long positions
    REDUCE_EXPOSURE = "reduce_exposure" # Cut position size by 50%
    CLOSE_ALL = "close_all"            # Exit all positions immediately
    HEDGE_SHORT = "hedge_short"        # Add offsetting short hedge
    PAUSE_TRADING = "pause_trading"    # Stop new entries temporarily
    WAIT_FOR_CLARITY = "wait_for_clarity"  # Hold and monitor

class VolatilityLevel(Enum):
    """Volatility classification"""
    LOW = "low"           # 0-1.5% annualized
    MODERATE = "moderate" # 1.5-3.0% annualized
    HIGH = "high"         # 3.0-5.0% annualized
    EXTREME = "extreme"   # 5%+ annualized

class CorrelationLevel(Enum):
    """Correlation risk classification"""
    LOW = "low"           # Different assets moving independently
    MODERATE = "moderate" # Some correlation detected
    HIGH = "high"         # Strong correlation (risky for diversification)
    EXTREME = "extreme"   # Perfect/near-perfect correlation

@dataclass
class HedgeCondition:
    """Individual condition evaluation for hedge decision"""
    condition_name: str
    current_value: float
    th
```

### foundation/rick_charter.py
```python
#!/usr/bin/env python3
"""
RICK Charter Enforcement Module - RBOTzilla UNI Phase 2
Immutable trading constants and enforcement logic.
PIN: 841921 | Generated: 2025-09-26
"""

import logging
from typing import Dict, List, Optional, Union
from datetime import timedelta
from enum import Enum

class TimeFrame(Enum):
    """Allowed trading timeframes"""
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    
class RejectedTimeFrame(Enum):
    """Explicitly rejected timeframes"""
    M1 = "M1"
    M5 = "M5"

class RickCharter:
    """
    RICK Charter Core Enforcement - Immutable Constants
    All values are hardcoded for safety and cannot be overridden.
    """
    
    # CORE AUTHENTICATION
    PIN = 841921
    CHARTER_VERSION = "2.0_IMMUTABLE"
    
    # TRADING CONSTRAINTS
    MAX_HOLD_DURATION_HOURS = 6
    MAX_HOLD_DURATION = timedelta(hours=MAX_HOLD_DURATION_HOURS)
    
    # =========================================================================
    # INCOME GOAL & SMART AGGRESSION STRATEGY (PIN 841921)
    # User Goal: $600/day income using $2K initial + $1K/month deposits
    # Strategy: Bootstrap → Scale → Automate (AI hive-driven)
    # =========================================================================
    
    # INCOME TARGETS (IMMUTABLE - AI-driven with smart aggression)
    DAILY_INCOME_TARGET_USD = 600.00  # Daily profit target
    MONTHLY_INCOME_TARGET_USD = 12600.00  # 21 trading days × $600
    ANNUAL_INCOME_TARGET_USD = 151200.00  # 252 trading days × $600
    DAILY_RISK_PER_TRADE = 0.02  # 2% risk per trade (immutable)
    
    # BOOTSTRAP PHASE (Month 0-3): Prove system works on small capital
    BOOTSTRAP_PHASE_CAPITAL_START_USD = 2000.00
    BOOTSTRAP_PHASE_CAPITAL_END_USD = 5300.00  # After deposits + P&L
    BOOTSTRAP_PHASE_DAILY_TARGET_USD = 100.00  # Start small, prove win rate
    BOOTSTRAP_PHASE_MIN_WIN_RATE = 0.60  # 60% win rate target
    BOOTSTRAP_PHASE_TRADES_PER_DAY = 5  # 3-5 trades for ML pattern testing
    
    # SCALE PHASE (Mo
```

### wolf_packs/orchestrator.py
```python
"""Simple orchestrator stub for smoke tests."""

from typing import Any


def detect_regime(data: Any = None) -> str:
    """Return a randomized market regime label for smoke tests.

    Uses `stochastic.random_choice` to ensure non-deterministic regime labels.
    """
    try:
        from stochastic import random_choice

        return random_choice(["neutral", "bull", "bear"])
    except Exception:
        return "neutral"

```

## Logs Evidence

_No logs/narration.jsonl present._