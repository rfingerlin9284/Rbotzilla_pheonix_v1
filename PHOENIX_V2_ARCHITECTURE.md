# PHOENIX V2 ARCHITECTURE BLUEPRINT
**Status**: DRAFT
**Date**: 2025-11-28
**Goal**: Unified, Python-only, TA-Lib-free trading system ($1M/3yr target).

## 1. CORE PHILOSOPHY
- **Unified Engine**: One engine to rule them all. No separate `paper_trading_engine.py`, `rbotzilla_engine.py`, `multi_broker_engine.py`. One `PhoenixEngine` class that handles both Paper and Live modes via configuration.
- **Modular Brokers**: Brokers are plugins. `IBKR`, `OANDA`, `Coinbase` are subclasses of a generic `BrokerAdapter`.
- **Strategy Voting**: Strategies (Wolfpack, ML, Hive) emit *Votes*, not Orders. The `SignalAggregator` tallies votes.
- **Risk First**: `ExecutionGate` and `RiskManager` are the final authority. They can veto any trade.
- **No TA-Lib**: All indicators calculated using `pandas`, `numpy`, or custom Python math. Zero binary dependencies.

## 2. DIRECTORY STRUCTURE (PROPOSED)
```
PHOENIX_V2/
├── config/
│   ├── config.yaml          # Main system config
│   ├── secrets.yaml         # API keys (gitignored)
│   └── trading_params.yaml  # Risk limits, pairs, timeframes
├── src/
│   ├── core/
│   │   ├── engine.py        # PhoenixEngine (The main loop)
│   │   ├── event_bus.py     # Internal messaging (Signals, Fills, Errors)
│   │   └── state.py         # Global system state (Positions, Balance)
│   ├── brokers/
│   │   ├── base.py          # Abstract Base Class
│   │   ├── ibkr.py          # IBKR TWS/Gateway implementation
│   │   ├── oanda.py         # OANDA v20 implementation
│   │   └── coinbase.py      # Coinbase Advanced Trade implementation
│   ├── strategies/
│   │   ├── base.py          # Strategy Interface
│   │   ├── hive_mind.py     # The "Brain" bridge
│   │   ├── wolfpack.py      # The 5-strategy voter
│   │   └── ml_regime.py     # Regime detection
│   ├── risk/
│   │   ├── gate.py          # ExecutionGate (Pre-trade checks)
│   │   ├── manager.py       # Position sizing & Portfolio risk
│   │   └── circuit_breaker.py # Emergency stops
│   └── utils/
│       ├── logger.py        # Structured logging
│       └── math_lib.py      # Custom indicator math (No TA-Lib)
├── tests/                   # Pytest suite
├── main.py                  # Entry point
└── requirements.txt         # Minimal dependencies (pandas, numpy, requests, ib_insync)
```

## 3. MIGRATION STRATEGY
We will migrate "Canonical" components from the Export into this new structure.

| Legacy Component | V2 Destination | Notes |
| ---------------- | -------------- | ----- |
| `rbotzilla_engine.py` | `src/core/engine.py` | The main loop logic (tick, sleep, heartbeat) moves here. |
| `ibkr_connector.py` | `src/brokers/ibkr.py` | Needs heavy refactoring to remove global state. |
| `oanda_connection.py` | `src/brokers/oanda.py` | Already clean, just needs adapting to BaseBroker. |
| `execution_gate.py` | `src/risk/gate.py` | Logic is sound, move as-is. |
| `hive_mind_bridge.py` | `src/strategies/hive_mind.py` | Adapt to emit "Votes". |
| `ignite_phoenix.py` | *DEPRECATED* | Replaced by `main.py` and `config/`. |

## 4. NEXT STEPS
1. **Scaffold**: Create the directory tree.
2. **Base Classes**: Define `BrokerAdapter` and `Strategy` interfaces.
3. **Port OANDA**: Move `oanda_connection.py` to `src/brokers/oanda.py`.
4. **Port Engine**: Create `PhoenixEngine` based on `rbotzilla`.
