#!/bin/bash
# RICK Phoenix V2 - GitHub Repository Push Script
# Pushes core files to: https://github.com/rfingerlin9284/Rbotzilla_pheonix_v1.git

set -e

echo "=================================================================================================="
echo "🚀 RICK PHOENIX V2 - GITHUB REPOSITORY PUSH"
echo "=================================================================================================="
echo "Target: https://github.com/rfingerlin9284/Rbotzilla_pheonix_v1.git"
echo "=================================================================================================="

# Create temporary staging directory
STAGE_DIR="/tmp/phoenix_v2_github_push_$(date +%s)"
mkdir -p "$STAGE_DIR"

echo "📦 Staging core files to: $STAGE_DIR"

# Core PhoenixV2 system files
echo "  → PhoenixV2/ (core system)"
cp -r PhoenixV2 "$STAGE_DIR/"

# Remove logs and cache
rm -rf "$STAGE_DIR/PhoenixV2/logs"/*.log 2>/dev/null || true
rm -rf "$STAGE_DIR/PhoenixV2"/__pycache__ 2>/dev/null || true
find "$STAGE_DIR/PhoenixV2" -name "*.pyc" -delete 2>/dev/null || true
find "$STAGE_DIR/PhoenixV2" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Configuration files (sanitized)
echo "  → Configuration files"
cp paper_acct_env.env.TEMPLATE "$STAGE_DIR/.env.template" 2>/dev/null || \
  echo "# Phoenix V2 Environment Template
# Copy this to .env and fill in your credentials
OANDA_PRACTICE_ACCOUNT_ID=your_account_id_here
OANDA_PRACTICE_TOKEN=your_token_here
TRADING_ENVIRONMENT=sandbox
MAX_CONCURRENT_POSITIONS=12
MAX_MARGIN_UTILIZATION=0.70
" > "$STAGE_DIR/.env.template"

# Startup scripts
echo "  → Startup scripts"
cp start_phoenix_v2.sh "$STAGE_DIR/" 2>/dev/null || true
cp supervisor.py "$STAGE_DIR/" 2>/dev/null || true
cp -r scripts "$STAGE_DIR/" 2>/dev/null || true

# VS Code Config
echo "  → VS Code Config"
mkdir -p "$STAGE_DIR/.vscode"
cp .vscode/tasks.json "$STAGE_DIR/.vscode/" 2>/dev/null || true

# Documentation
echo "  → Documentation"
mkdir -p "$STAGE_DIR/docs"
cp DIAGNOSIS_NO_TRADING_ACTIVITY.md "$STAGE_DIR/docs/" 2>/dev/null || true
cp AGENT_CHARTER_v2.md "$STAGE_DIR/docs/" 2>/dev/null || true
cp ALL_INTERFACES_GUIDE.md "$STAGE_DIR/docs/" 2>/dev/null || true
cp COMPLETE_SYSTEM_INVENTORY.md "$STAGE_DIR/docs/" 2>/dev/null || true

# Codeless Control
echo "  → Codeless Control"
cp CODELESS_CONTROL_REGISTRY.md "$STAGE_DIR/" 2>/dev/null || true
cp AGENT_CODELESS_MANDATE.md "$STAGE_DIR/" 2>/dev/null || true

# Backtest results
echo "  → Backtest results"
mkdir -p "$STAGE_DIR/backtest_results"
cp -r backtest_results/*.json "$STAGE_DIR/backtest_results/" 2>/dev/null || true

# Tests
echo "  → Test files"
mkdir -p "$STAGE_DIR/tests"
find . -maxdepth 1 -name "*test*.py" -exec cp {} "$STAGE_DIR/tests/" \; 2>/dev/null || true

# HiveMind integration
echo "  → HiveMind system"
cp -r rick_hive "$STAGE_DIR/" 2>/dev/null || cp -r hive "$STAGE_DIR/rick_hive" 2>/dev/null || true

# Create comprehensive README
echo "  → Generating README.md"
cat > "$STAGE_DIR/README.md" << 'EOFREADME'
# 🔥 RICK Phoenix V2 Trading System

**Institutional-Grade Autonomous Trading System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Overview

RICK Phoenix V2 is a sophisticated autonomous trading system featuring:

- **Multi-Broker Support**: OANDA (Forex), Coinbase Advanced (Crypto), IBKR (Stocks/Options)
- **HiveMind AI**: Multi-agent consensus system with GPT/Grok/DeepSeek integration
- **WolfPack Strategies**: 5 battle-tested strategies with voting consensus
- **Immutable Charter**: PIN-protected risk management (841921)
- **Amplifier Protocol**: 12 concurrent positions, 70% margin utilization
- **Real-time Monitoring**: Supervisor pattern with health checks

## 📊 Performance

Based on 1-year historical backtest (see `backtest_results/`):

- **Initial Capital**: $5,000
- **Monthly Deposits**: $1,000
- **Charter Compliance**: 100%
- **Risk Management**: 2% per trade, 3:1 R:R minimum

## 🚀 Quick Start

### Prerequisites

```bash
python >= 3.8
pandas
numpy
requests
python-dotenv
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/rfingerlin9284/Rbotzilla_pheonix_v1.git
cd Rbotzilla_pheonix_v1
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.template .env
# Edit .env with your API credentials
```

4. Start the system:
```bash
./start_phoenix_v2.sh
```

## 🏗️ Architecture

```
PhoenixV2/
├── brain/              # Strategy aggregation (HiveMind + WolfPack)
├── config/             # Charter and trading pairs
├── core/               # Authentication and state management
├── execution/          # Broker connectors (OANDA, Coinbase, IBKR)
├── gate/               # Risk management and validation
├── operations/         # Position management (Surgeon)
└── logic/              # Technical indicators and regime detection
```

### Key Components

**Charter System** (`config/charter.py`):
- Immutable risk rules
- PIN protection (841921)
- Position limits and margin caps

**HiveMind** (`brain/hive_mind.py`):
- Multi-AI agent delegation
- Consensus-based signals
- 3:1 R:R enforcement

**WolfPack** (`brain/wolf_pack.py`):
- 5 strategy voting system
- Confidence-weighted decisions
- Learning-driven allocation

**Risk Gate** (`gate/risk_gate.py`):
- Final trade validation
- Correlation monitoring
- Charter compliance enforcement

## 📈 Trading Strategy

1. **Signal Generation**:
   - HiveMind checks for ML-validated setups (3:1 R:R minimum)
   - WolfPack generates consensus from 5 strategies
   - Cross-market correlation checks (BTC vs SPX)

2. **Risk Validation**:
   - Charter compliance (position count, margin, R:R)
   - Correlation check (prevents overexposure)
   - Notional size validation

3. **Execution**:
   - OCO orders (Stop Loss + Take Profit mandatory)
   - Position tracking via Surgeon
   - Stagnant winner harvest (6h + $5 profit)

## 🔐 Charter Rules

The Charter enforces institutional-grade risk management:

```python
MAX_CONCURRENT_POSITIONS = 12  # Amplifier Protocol
MAX_MARGIN_UTILIZATION = 0.70  # 70% hard cap
MAX_RISK_PER_TRADE = 0.02      # 2% per trade
MIN_TIMEFRAME = "M15"           # No noise trading
OCO_MANDATORY = True            # Must have SL/TP
```

**Charter modifications require PIN: 841921**

## 🧠 HiveMind Integration

The system delegates analysis to multiple AI agents:

- **GPT-4**: Technical pattern recognition (35% weight)
- **Grok**: Market sentiment analysis (35% weight)
- **DeepSeek**: Cross-asset correlation (30% weight)

Consensus confidence threshold: **65%**

## 📊 Monitoring

Check system status:
```bash
cat PhoenixV2/logs/system_status.json
```

View audit trail:
```bash
tail -f PhoenixV2/logs/audit.log
```

Check portfolio:
```bash
python3 check_portfolio.py
```

## 🧪 Testing

Run backtests:
```bash
python3 comprehensive_1year_backtest.py
```

View results:
```bash
cat backtest_results/*.json | python3 -m json.tool
```

## 🔧 Configuration

### Master Environment File

`paper_acct_env.env` is the **single source of truth**. All updates require:
- PIN verification (841921), OR
- Explicit chat confirmation

### Broker Setup

**OANDA** (Forex):
```bash
OANDA_PRACTICE_ACCOUNT_ID=your_account_id
OANDA_PRACTICE_TOKEN=your_token
OANDA_PRACTICE_BASE_URL=https://api-fxpractice.oanda.com/v3
```

**Coinbase Advanced** (Crypto):
```bash
COINBASE_LIVE_API_KEY=organizations/xxx/apiKeys/xxx
COINBASE_LIVE_API_SECRET=-----BEGIN EC PRIVATE KEY-----...
COINBASE_LIVE_BASE_URL=https://api.coinbase.com
```

**IBKR** (Stocks):
```bash
IB_GATEWAY_HOST=127.0.0.1
IB_GATEWAY_PORT=4002
IB_ACCOUNT_ID=your_account_id
```

## 🐛 Troubleshooting

### No Trading Activity

1. Check processes:
```bash
ps aux | grep -E "supervisor|main.py"
```

2. Verify environment variables:
```bash
cat /proc/$(pgrep -f main.py)/environ | tr '\0' '\n' | grep OANDA
```

3. Test connection:
```bash
python3 -c "from PhoenixV2.core.auth import AuthManager; from PhoenixV2.execution.router import BrokerRouter; auth = AuthManager(); router = BrokerRouter(auth)"
```

See `docs/DIAGNOSIS_NO_TRADING_ACTIVITY.md` for comprehensive troubleshooting.

### Signal Generation Issues

HiveMind requires market data access. Verify:
```bash
python3 -c "from PhoenixV2.brain.aggregator import StrategyBrain; from PhoenixV2.execution.router import BrokerRouter; from PhoenixV2.core.auth import AuthManager; auth = AuthManager(); router = BrokerRouter(auth); brain = StrategyBrain(router); print('OK' if brain.get_signal('EUR_USD') else 'No signal')"
```

## 📚 Documentation

- `docs/AGENT_CHARTER_v2.md` - Charter rules and philosophy
- `docs/ALL_INTERFACES_GUIDE.md` - Complete interface documentation
- `docs/DIAGNOSIS_NO_TRADING_ACTIVITY.md` - Troubleshooting guide
- `docs/COMPLETE_SYSTEM_INVENTORY.md` - Full component inventory

## 🤝 Contributing

This is a personal trading system. Fork at your own risk.

## ⚖️ License

MIT License - See LICENSE file

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK**

This software is for educational purposes. Trading involves substantial risk of loss. Past performance does not guarantee future results. The authors assume no liability for financial losses.

## 📞 Support

- Issues: GitHub Issues
- Documentation: `/docs` folder
- System Status: `PhoenixV2/logs/system_status.json`

---

**Built with institutional discipline. Powered by AI consensus. Protected by immutable charter.**

🔥 RICK Phoenix V2 - The Money Machine
EOFREADME

# Create requirements.txt
cat > "$STAGE_DIR/requirements.txt" << 'EOFREQ'
pandas>=1.3.0
numpy>=1.21.0
requests>=2.26.0
python-dotenv>=0.19.0
EOFREQ

# Create .gitignore
cat > "$STAGE_DIR/.gitignore" << 'EOFGITIGNORE'
# Environment files
.env
paper_acct_env.env
*.env.bak

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Logs
*.log
logs/
PhoenixV2/logs/*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Credentials
*_credentials.json
*_token.txt
EOFGITIGNORE

echo ""
echo "✅ Files staged successfully"
echo ""
echo "📂 Staged directory contents:"
ls -lah "$STAGE_DIR"
echo ""

# Initialize git if needed
cd "$STAGE_DIR"
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
    git config user.name "RFing"
    git config user.email "rfingerlin9284@gmail.com"
    git config commit.gpgsign false
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Commit
echo "💾 Creating commit..."
git commit -m "RICK Phoenix V2 - Strategic Pivot: Quality over Quantity

- Reduced MAX_CONCURRENT_POSITIONS to 6
- Increased WolfPack confidence threshold to 0.60
- Increased WolfPack Sharpe threshold to 1.0
- Added Narration Stream for real-time monitoring
- Phoenix V2 autonomous trading system
- HiveMind multi-AI delegation
- WolfPack strategy consensus
- 1-year backtest results
- Complete documentation

Charter PIN: 841921
Date: $(date -u +%Y-%m-%d)"

# Add remote (if not exists)
if ! git remote | grep -q origin; then
    echo "🔗 Adding remote repository..."
    git remote add origin https://github.com/rfingerlin9284/Rbotzilla_pheonix_v1.git
fi

echo ""
echo "=================================================================================================="
echo "✅ READY TO PUSH"
echo "=================================================================================================="
echo ""
echo "To complete the push, run:"
echo ""
echo "  cd $STAGE_DIR"
echo "  git push -u origin main --force"
echo ""
echo "Or execute this command to push now:"
echo ""
echo "  cd $STAGE_DIR && git push -u origin main --force"
echo ""
echo "=================================================================================================="
echo "📦 Staged directory: $STAGE_DIR"
echo "🎯 Remote: https://github.com/rfingerlin9284/Rbotzilla_pheonix_v1.git"
echo "=================================================================================================="
