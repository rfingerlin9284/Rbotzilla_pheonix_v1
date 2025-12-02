# RICK Phoenix Consolidated Strategies
## Version 1.0.0 | PIN: 841921

This package consolidates **116 strategy-related files** from the RICK Phoenix trading system into **5 core modules** containing all non-redundant logic.

---

## Module Summary

### 1. `consolidated_core_strategies.py` (~600 lines)
All trading strategies consolidated:
- **WolfPack Strategies**: Momentum, MeanReversion, Breakout, Trend, Range
- **Wolf Market Strategies**: BullishWolf, BearishWolf, SidewaysWolf
- **Breakout Strategies**: FibConfluenceBreakout, CryptoBreakout, BreakoutVolumeExpansion
- **Signal Generation**: MomentumSignals, TechnicalIndicators
- **Aggregation**: StrategyAggregator (weighted voting system)

### 2. `consolidated_risk_management.py` (~600 lines)
All risk modules consolidated:
- **DynamicSizing**: Kelly Criterion position sizing with volatility adjustment
- **CorrelationMonitor**: USD exposure tracking, max 70% correlation
- **SessionBreaker**: -5% daily loss halt
- **QuantHedgeRules**: Multi-condition hedge analysis (5 conditions, 7 actions)
- **UnifiedRiskManager**: Combined interface

### 3. `consolidated_ml_learning.py` (~500 lines)
All ML/learning modules consolidated:
- **StochasticRegimeDetector**: Bull/Bear/Sideways/Crash/Triage classification
- **PatternLearner**: Historical pattern similarity matching
- **MLRewardSystem**: Confidence adjustment from outcomes
- **AdaptiveRick**: Combined ML interface

### 4. `consolidated_gates.py` (~400 lines)
All pre-trade gates consolidated:
- **GuardianGates**: 4 cascading gates (Margin, Concurrent, Correlation, Crypto)
- **CryptoEntryGate**: 90% consensus requirement
- **ExecutionGate**: 3:1 R:R ratio enforcement
- **UnifiedGateSystem**: Combined validation

### 5. `consolidated_utilities.py` (~500 lines)
All utility modules consolidated:
- **SmartTrailingSystem**: Progressive trailing stops
- **QuantHedgeEngine**: Correlation-based hedging
- **DynamicStops**: ATR-based stop/take calculation
- **SmartAggression**: Adaptive position sizing
- **TradingUtilities**: Combined interface

---

## Usage Example

```python
from consolidated_core_strategies import StrategyAggregator, StrategySignal
from consolidated_risk_management import UnifiedRiskManager
from consolidated_ml_learning import AdaptiveRick
from consolidated_gates import UnifiedGateSystem
from consolidated_utilities import TradingUtilities

# Initialize with PIN
PIN = 841921

# Strategy analysis
aggregator = StrategyAggregator(PIN)
signal = aggregator.get_aggregated_signal("EUR_USD", prices, volumes, "BULL")

# Risk management
risk_mgr = UnifiedRiskManager(PIN, account_balance=100000)
can_trade, reason = risk_mgr.can_enter_trade(symbol, direction, size, account, positions)
position_size = risk_mgr.get_position_size(symbol, current_price, confidence)

# ML analysis
ml = AdaptiveRick(PIN)
market_analysis = ml.analyze_market(prices, symbol)
adjusted_conf = ml.get_adjusted_confidence(base_confidence, regime)

# Gate validation
gates = UnifiedGateSystem(PIN)
decision = gates.validate_trade(signal, account, positions, volatility)

# Utilities
utils = TradingUtilities(PIN)
stops = utils.calculate_stops("BUY", entry_price, atr, regime)
trailing = utils.update_trailing_stop(entry, current, stop, "BUY", atr)
```

---

## Charter Compliance

All modules enforce RICK Charter rules:
- PIN verification: 841921
- Max margin utilization: 35%
- Max concurrent positions: 3
- Max USD correlation: 70%
- Crypto consensus: 90%
- Minimum R:R ratio: 3:1
- Daily loss limit: 5%

---

## Original Files Consolidated

| Source Location | Files Count | Modules |
|-----------------|-------------|---------|
| strategies/ | 8 | BullishWolf, BearishWolf, SidewaysWolf, etc. |
| PhoenixV2/brain/ | 4 | WolfPack, HiveMind, QuantHedge |
| PhoenixV2/gate/ | 3 | CorrelationMonitor, ExecutionGate |
| risk/ | 5 | DynamicSizing, SessionBreaker |
| hive/ | 6 | GuardianGates, QuantHedgeRules |
| ml_learning/ | 4 | PatternLearner, MLModels |
| util/ | 8 | MomentumTrailing, QuantHedgeEngine |
| logic/ | 3 | RegimeDetector |
| systems/ | 2 | MomentumSignals |
| research_strategies/ | 12 | Various experimental |
| ROLLBACK_SNAPSHOTS/ | ~50 | Backups (reviewed for unique logic) |

**Total: 116+ files → 5 consolidated modules**

---

## Self-Test

Each module includes a self-test at the bottom. Run directly:

```bash
python consolidated_core_strategies.py
python consolidated_risk_management.py
python consolidated_ml_learning.py
python consolidated_gates.py
python consolidated_utilities.py
```

---

## Dependencies

- numpy (for calculations)
- Python 3.8+

---

Generated: $(date)
RICK Phoenix System | Charter PIN: 841921
