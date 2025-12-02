# RICK_LIVE_CLEAN - Complete Active Components System Map
**Generated**: 2025-10-12  
**PIN**: 841921  
**Total Components**: 34 Active Modules

---

## 📊 System Overview

```
RICK_LIVE_CLEAN Trading System
├── 🏛️  Core Foundation (2 components)
├── 🎮  Mode Management (1 component)
├── 📝  Logging Infrastructure (2 components)
├── 🔌  Trading Connectors (2 components)
├── 🤖  ML Intelligence (3 components)
├── 🧠  Smart Logic (2 components)
├── 🛡️  Risk Management (7 components)
├── 📈  Futures Trading (3 components)
├── 🐺  Wolfpack Orchestration (4 components)
├── 🐝  Swarm Execution (1 component)
├── 👻  Ghost Trading (2 components)
├── ⏭️  Promotion System (1 component)
├── 📊  Monitoring Dashboard (2 components)
└── 🔧  Utilities (2 components)
```

---

## 🏛️ CORE FOUNDATION

### foundation/rick_charter.py ✅ VERIFIED
**Purpose**: Immutable trading constants with self-validation  
**Status**: ACTIVE

**Key Features**:
- MIN_RISK_REWARD_RATIO = 3.2
- MIN_NOTIONAL_USD = $15,000
- PIN validation (841921)
- Self-test on import
- Max placement latency: 300ms

**Dependencies**: None  
**Critical**: Blocks system startup if validation fails

---

### foundation/progress.py ✅ VERIFIED
**Purpose**: Phase tracking and system progress management  
**Status**: ACTIVE

**Key Features**:
- Phase status tracking
- Atomic progress updates
- Change tracker integration

**Dependencies**: rick_charter.py

---

## 🎮 MODE MANAGEMENT

### util/mode_manager.py ✅ VERIFIED
**Purpose**: .upgrade_toggle integration for OFF/GHOST/CANARY/LIVE modes  
**Status**: ACTIVE

**Key Features**:
- Mode mappings: OFF/GHOST/CANARY/LIVE
- Environment auto-detection
- PIN validation for LIVE mode
- Connector environment mapping
- SimpleLogger (avoids util/logging.py conflict)

**Mode Configuration**:
```
OFF     → OANDA: practice, Coinbase: sandbox
GHOST   → OANDA: practice, Coinbase: sandbox
CANARY  → OANDA: practice, Coinbase: sandbox
LIVE    → OANDA: live,     Coinbase: live (requires PIN 841921)
```

**Dependencies**: rick_charter.py

---

## 📝 LOGGING INFRASTRUCTURE

### util/narration_logger.py ✅ VERIFIED
**Purpose**: Centralized event and P&L logging  
**Status**: ACTIVE

**Key Features**:
- `log_narration()` for trading events
- `log_pnl()` for trade P&L tracking
- `get_session_summary()` for metrics
- `get_latest_narration(n)` for recent events
- Writes to narration.jsonl and pnl.jsonl
- Fallback import chain support

**Log Files**:
- `pre_upgrade/headless/logs/narration.jsonl` (232k+ lines)
- `pre_upgrade/headless/logs/pnl.jsonl`

**Dependencies**: None

---

### util/progress_tracker.py ✅ VERIFIED
**Purpose**: Immutable progress tracking with auto-README generation  
**Status**: ACTIVE

**Key Features**:
- Append-only progress log
- Automatic README.md generation
- Timestamped backups
- Active files registry
- Atomic file operations

**Dependencies**: None

---

## 🔌 TRADING CONNECTORS

### brokers/oanda_connector.py ✅ VERIFIED
**Purpose**: OANDA FX trading connector with OCO support  
**Status**: ACTIVE

**Asset Class**: FX  
**Symbols**: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD

**Key Features**:
- Environment auto-detection (practice/live)
- Min-notional enforcement ($15k)
- Auto-upsize units (500→12,907)
- OCO placement with latency logging
- Narration event logging
- Import fallback chain

**Dependencies**: rick_charter.py, mode_manager.py, narration_logger.py

---

### brokers/coinbase_connector.py ✅ VERIFIED
**Purpose**: Coinbase Advanced crypto trading connector  
**Status**: ACTIVE

**Asset Class**: CRYPTO  
**Symbols**: BTC-USD, ETH-USD, BNB-USD, SOL-USD, XRP-USD

**Key Features**:
- Environment auto-detection (sandbox/live)
- Min-notional enforcement ($15k)
- OCO placement logging
- Advanced API integration
- Import fallback chain

**Dependencies**: rick_charter.py, mode_manager.py, narration_logger.py

---

## 🤖 ML INTELLIGENCE

### ml_learning/ml_models.py 🔥 ACTIVE
**Purpose**: ML model loader with stochastic signal generation  
**Status**: ACTIVE

**Model Types**:
- **A**: Forex
- **B**: Spot Crypto
- **C**: Derivatives/Futures

**Key Features**:
- Regime-aware signal generation
- Confidence scoring (0.0-1.0)
- Stochastic behavior support
- MLSignal dataclass output

**Dependencies**: regime_detector.py

---

### ml_learning/pattern_learner.py 🔥 ACTIVE
**Purpose**: ML-powered pattern memorization and similarity matching  
**Status**: ACTIVE

**Key Features**:
- Trade pattern storage with outcomes
- Similarity scoring using indicator distance
- Win/loss learning loop
- Performance-based filtering (55% min win rate)
- Max 10,000 patterns storage

**Indicator Weights**:
- RSI: 20%
- MACD: 20%
- Bollinger Bands: 15%
- ATR: 10%
- Volume: 10%
- SMA Distance: 15%
- Confidence: 10%

**Dependencies**: rick_charter.py

---

### ml_learning/optimizer.py 🔥 ACTIVE
**Purpose**: Strategy parameter optimization  
**Status**: ACTIVE

**Key Features**:
- Parameter tuning
- Performance optimization
- Backtesting integration

**Dependencies**: None

---

## 🧠 SMART LOGIC

### logic/smart_logic.py 🔥 ACTIVE
**Purpose**: Signal validation with RR, FVG, Fibonacci confluence  
**Status**: ACTIVE

**Filters**:
1. Risk/Reward ratio check (≥3.2)
2. FVG alignment validation
3. Fibonacci level confluence
4. Trend strength analysis
5. Volume confirmation

**Key Features**:
- Filter scoring system (0.0-1.0)
- SignalValidation dataclass
- FilterScore with weights
- Confluence detection

**Dependencies**: rick_charter.py

---

### logic/regime_detector.py 🔥 ACTIVE
**Purpose**: Market regime classification  
**Status**: ACTIVE

**Regime Types**:
- **BULL**: Positive trend, controlled volatility
- **BEAR**: Negative trend
- **SIDEWAYS**: Low trend, low volatility
- **CRASH**: Extreme negative + high vol
- **TRIAGE**: Uncertainty baseline

**Key Features**:
- Volatility-based detection
- Trend strength calculation
- Stochastic regime probabilities
- Confidence scoring

**Dependencies**: None

---

## 🛡️ RISK MANAGEMENT

### risk/oco_validator.py 🔥 ACTIVE
**Purpose**: Hard-enforce OCO on every open position  
**Status**: ACTIVE

**Key Features**:
- Every position must have TP and SL
- Auto-close positions without OCO
- Risk exposure calculation
- Max risk per position: 2%
- Force close threshold: 5%
- Validation interval: 30 seconds

**Dependencies**: alerting system (optional)

---

### risk/dynamic_sizing.py 🔥 ACTIVE
**Purpose**: Kelly Criterion-based position sizing  
**Status**: ACTIVE

**Key Features**:
- Kelly optimal fraction calculation
- Volatility adjustment
- Max position: 10% capital
- Min position: 0.1% capital
- Kelly multiplier: 0.25 (quarter Kelly)
- Volatility target: 2% daily
- Sharpe ratio integration
- Emergency stop at 15% drawdown

**Dependencies**: rick_charter.py

---

### risk/session_breaker.py 🔥 ACTIVE
**Purpose**: Final risk circuit breaker beyond daily limits  
**Status**: ACTIVE

**Key Features**:
- Cumulative P&L monitoring
- Halt trading at -5% threshold
- Consecutive trigger limit: 3
- Session reset: 24 hours
- System shutdown procedures
- Alerting integration

**Dependencies**: alerting system (optional)

---

### risk/correlation_monitor.py 🔥 ACTIVE
**Purpose**: Portfolio correlation tracking and exposure control  
**Status**: ACTIVE

**Key Features**:
- Real-time symbol correlations
- Block trades >0.7 correlation
- Warning at >0.5 correlation
- Min 20 data points for reliability
- 30-day lookback window

**Asset Groups**:
- FX Major: EUR_USD, GBP_USD, USD_JPY, etc.
- FX Minor: EUR_GBP, EUR_JPY, GBP_JPY, etc.
- Crypto Major: BTC-USD, ETH-USD, BNB-USD, etc.
- Crypto Alt: ADA-USD, DOT-USD, LINK-USD, etc.
- Indices: US30, SPX500, NAS100, etc.

**Dependencies**: rick_charter.py

---

### risk/oco_integration_example.py 🔥 ACTIVE
**Purpose**: OCO integration examples and templates  
**Status**: ACTIVE

---

### risk/session_breaker_integration.py 🔥 ACTIVE
**Purpose**: Session breaker integration helpers  
**Status**: ACTIVE

---

### risk/risk_control_center.py 🔥 ACTIVE
**Purpose**: Central risk management coordination  
**Status**: ACTIVE

---

## 📈 FUTURES TRADING

### connectors/futures/futures_engine.py 🔥 ACTIVE
**Purpose**: Futures trading engine with venue management  
**Status**: ACTIVE

**Key Features**:
- Multi-venue support
- Leverage management
- Margin monitoring
- Funding rate tracking
- Max positions: 8
- Emergency mode support

**Dependencies**: leverage_calculator.py, venue_manager.py

---

### connectors/futures/leverage_calculator.py 🔥 ACTIVE
**Purpose**: Dynamic leverage calculation  
**Status**: ACTIVE

**Key Features**:
- Max leverage: 25x
- Base risk per trade: 2%
- Confidence-based multipliers
- Volatility adjustments
- Market condition scaling
- Position concentration penalty
- Max 15% balance per position

**Confidence Multipliers**:
- 0.95: 1.5x
- 0.85: 1.2x
- 0.75: 1.0x
- 0.65: 0.7x
- 0.55: 0.4x

**Dependencies**: None

---

### connectors/futures/venue_manager.py 🔥 ACTIVE
**Purpose**: Multi-venue futures trading management  
**Status**: ACTIVE

**Dependencies**: None

---

## 🐺 WOLFPACK ORCHESTRATION

### wolf_packs/orchestrator.py 🔥 ACTIVE
**Purpose**: Wolfpack strategy orchestration  
**Status**: ACTIVE

**Key Features**:
- Regime-based strategy selection
- Stochastic regime detection
- Strategy coordination

**Dependencies**: regime_detector.py

---

### wolf_packs/_base.py 🔥 ACTIVE
**Purpose**: Base wolfpack class and interfaces  
**Status**: ACTIVE

---

### wolf_packs/extracted_oanda.py 🔥 ACTIVE
**Purpose**: OANDA-specific wolfpack strategies  
**Status**: ACTIVE

---

### wolf_packs/stochastic_config.py 🔥 ACTIVE
**Purpose**: Stochastic parameter configuration  
**Status**: ACTIVE

---

## 🐝 SWARM EXECUTION

### swarm/swarm_bot.py 🔥 ACTIVE
**Purpose**: Individual bot for single position management  
**Status**: ACTIVE

**Key Features**:
- Trailing stop management
- TTL expiration (6 hours default)
- Position lifecycle tracking
- Volatility multiplier: 1.5x ATR
- Update interval: 10 seconds

**Trail Types**:
- FIXED: Fixed pip trailing
- VOLATILITY: ATR-based trailing
- PERCENTAGE: Percentage-based trailing

**Position States**:
- ACTIVE → TRAILING → CLOSING → CLOSED
- EXPIRED, STOPPED

**Dependencies**: rick_charter.py

---

## 👻 GHOST TRADING

### ghost_trading_engine.py 🔥 RUNNING
**Purpose**: 45-minute ghost trading validation  
**Status**: ACTIVE - CURRENTLY RUNNING (PID 855309)

**Current Performance**:
- Trades: 9 completed
- Win Rate: 66.7%
- Capital: $2,282.42 (+$11.04)

**Key Features**:
- Real-time paper trading simulation
- OANDA FX pairs only
- 45-minute session duration
- Promotion criteria evaluation
- Narration logging integration
- P&L tracking

**Promotion Criteria**:
- Min trades: 10
- Min win rate: 70%
- Min P&L: $50
- Max consecutive losses: 3
- Min avg RR: 2.5

**Dependencies**: narration_logger.py, mode_manager.py

---

### test_ghost_trading.py ✅ VERIFIED
**Purpose**: 2-minute ghost trading test suite  
**Status**: ACTIVE

**Key Features**:
- Quick validation (2 minutes)
- 5 trade simulation
- Mode switching verification
- Logging verification

**Dependencies**: ghost_trading_engine.py

---

## ⏭️ PROMOTION SYSTEM

### canary_to_live.py ✅ TESTED
**Purpose**: Automated GHOST→CANARY→LIVE promotion  
**Status**: ACTIVE

**Key Features**:
- Reads from narration_logger
- Uses mode_manager for promotion
- PIN validation for LIVE
- Min 3 successful sessions
- 70% min win rate
- 100+ total trades required
- $50+ avg P&L per session
- 85% consistency threshold

**Dependencies**: narration_logger.py, mode_manager.py, rick_charter.py

---

## 📊 MONITORING DASHBOARD

### dashboard/generate_dashboard.py ✅ VERIFIED
**Purpose**: Static HTML dashboard generator  
**Status**: ACTIVE

**Key Features**:
- No Flask dependency
- Mode badges with color coding
- Performance metrics
- Recent activity feed
- Auto-refresh every 10 seconds
- Quick command reference

**Dependencies**: narration_logger.py, mode_manager.py

---

### scripts/monitor_ghost_session.py ✅ VERIFIED
**Purpose**: Real-time ghost session monitoring  
**Status**: ACTIVE

**Key Features**:
- Live session tracking
- Trade-by-trade updates
- P&L summary display
- Auto-refresh every 5 seconds
- Process status detection

**Dependencies**: narration_logger.py

---

## 🔧 UTILITIES

### util/logging.py 🔥 ACTIVE
**Purpose**: System logging utilities  
**Status**: ACTIVE

---

### util/retry.py 🔥 ACTIVE
**Purpose**: Retry logic for API calls  
**Status**: ACTIVE

---

## 📈 COMPONENT INTERACTION MAP

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER/OPERATOR                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MODE MANAGER                                 │
│           OFF / GHOST / CANARY / LIVE                           │
│         (reads .upgrade_toggle, manages env)                    │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ├──────► OANDA Connector (FX) ──────┐
       │                                     │
       └──────► Coinbase Connector (Crypto) ┤
                                             │
                                             ▼
                        ┌────────────────────────────────────┐
                        │    NARRATION LOGGER                │
                        │  (events + P&L tracking)           │
                        └────────────┬───────────────────────┘
                                     │
                                     ├──► narration.jsonl
                                     └──► pnl.jsonl
                                     
┌─────────────────────────────────────────────────────────────────┐
│                      TRADING LOGIC FLOW                         │
└─────────────────────────────────────────────────────────────────┘

1. REGIME DETECTOR ────► Identifies market state
         │
         ▼
2. ML MODELS ──────────► Generates signals (A/B/C)
         │
         ▼
3. SMART LOGIC ────────► Validates signals (RR, FVG, Fib)
         │
         ▼
4. DYNAMIC SIZING ─────► Calculates position size (Kelly)
         │
         ▼
5. CORRELATION MONITOR ► Checks portfolio exposure
         │
         ▼
6. LEVERAGE CALC ──────► Determines leverage (futures)
         │
         ▼
7. OCO VALIDATOR ──────► Enforces TP/SL on every trade
         │
         ▼
8. SWARM BOT ──────────► Manages position lifecycle
         │
         ▼
9. SESSION BREAKER ────► Monitors cumulative risk
         │
         ▼
10. PATTERN LEARNER ───► Learns from outcomes
```

---

## 🎯 SYSTEM STATUS

**Current Mode**: GHOST  
**Ghost Session**: RUNNING (PID 855309)  
**Trades**: 9 completed, 66.7% win rate  
**Active Components**: 34 modules  
**Risk Controls**: 7 active systems  
**ML Intelligence**: 3 models active  

**Safety Status**: ✅ ALL GUARDRAILS OPERATIONAL

---

## 📝 QUICK REFERENCE

### Check System Status
```bash
cat .upgrade_toggle                    # Current mode
python3 canary_to_live.py --check-only # Promotion readiness
ps aux | grep ghost_trading            # Ghost session status
```

### Monitor Performance
```bash
python3 scripts/monitor_ghost_session.py  # Real-time monitoring
python3 dashboard/generate_dashboard.py   # Update dashboard
```

### Access Logs
```bash
tail -f pre_upgrade/headless/logs/narration.jsonl | jq .
tail -f pre_upgrade/headless/logs/pnl.jsonl | jq .
```

---

**Generated**: 2025-10-12  
**Total Active Components**: 34  
**System Health**: 🟢 OPTIMAL
