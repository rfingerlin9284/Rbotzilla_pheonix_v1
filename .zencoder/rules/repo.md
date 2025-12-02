---
description: Repository Information Overview
alwaysApply: true
---

# RICK_LIVE_CLEAN Trading System Information

## Summary
RICK_LIVE_CLEAN is a live trading system designed for algorithmic trading across multiple brokers (OANDA, Coinbase, Interactive Brokers). The system operates in different modes (PAPER/LIVE) with a focus on risk management and performance monitoring. It includes ML-enhanced capabilities for pattern recognition and trading decisions.

## Structure
- **brokers/**: Connector implementations for OANDA, Coinbase, and Interactive Brokers
- **foundation/**: Core trading rules and charter with immutable constants
- **util/**: Utility modules for logging, mode management, and parameter management
- **ml_learning/**: Machine learning models and pattern recognition
- **logic/**: Smart logic filters and gated validation
- **scripts/**: Helper scripts for testing and monitoring
- **hive/**: Orchestration components for strategy coordination
- **config/**: Configuration files and parameters storage

## Language & Runtime
**Language**: Python
**Version**: 3.12
**Package Manager**: pip
**Configuration**: requirements.txt

## Dependencies
**Main Dependencies**:
- oandapyV20 (≥0.7.2): OANDA API client
- coinbase-advanced-py (≥1.2.0): Coinbase API client
- pandas (≥2.0.0): Data analysis
- numpy (≥1.24.0): Numerical computing
- scikit-learn (≥1.3.0): Machine learning
- requests (≥2.31.0): HTTP client for API interactions

**Development Dependencies**:
- pytest (≥7.4.0): Testing framework
- pytest-cov (≥4.1.0): Test coverage

## Build & Installation
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment
python load_env.py

# Start trading engine
./control_trading_mode.sh paper
```

## Main Components

### Parameter Management
**Main File**: util/parameter_manager.py
**Description**: Centralized parameter management with locking and audit trail
**Features**:
- Persistent parameter storage in JSON
- Parameter locking to prevent changes
- Audit logging of all parameter changes
- Backup creation before parameter updates

### Trading Engine
- **trading_engine.py**: Unified trading engine supporting both PAPER and LIVE modes
- **multi_broker_engine.py**: Unified trading across multiple brokers

### Core Framework
- **foundation/rick_charter.py**: Immutable trading constants and rules (RR ratio: 3.2)
- **util/mode_manager.py**: Manages system modes (PAPER/LIVE)
- **logic/smart_logic.py**: Gated logic for signal validation

### Broker Connectors
- **brokers/oanda_connector.py**: OANDA API integration
- **brokers/oanda_connector_enhanced.py**: OANDA with parameter manager integration
- **brokers/coinbase_connector.py**: Coinbase API integration
- **brokers/ib_connector.py**: Interactive Brokers API integration

### Charter Enforcement
- **foundation/rick_charter.py**: Immutable trading constants and enforcement logic
- **scripts/enforce_immutability.py**: Ensures critical files remain clean and immutable

## Testing
**Framework**: pytest
**Test Location**: Root directory (test_*.py)
**Naming Convention**: test_*.py
**Test Components**:
- Market data validation
- Integration testing
- Strategy verification
- Connector functionality
- Parameter management

**Run Command**:
```bash
python test_simple.py  # Parameter manager test
pytest  # All tests
```

## Operational Modes
- **PAPER**: Paper trading mode (api=true)
- **LIVE**: Full live trading with real money (api=false)

## Immutability Enforcement
**File**: scripts/enforce_immutability.py
**Purpose**: Ensures critical trading system files remain clean and immutable
**Features**:
- File checksums to detect modifications
- Automatic backups of critical files
- Read-only protection for charter files
- PIN-protected access (841921)

**Run Command**:
```bash
./enforce_charter_immutability.sh 841921
```