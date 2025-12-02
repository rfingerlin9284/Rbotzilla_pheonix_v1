#!/usr/bin/env bash
# Check whether IBKR gateway and IBKR engine is running
set -euo pipefail
echo "Checking IBKR processes..."
ps aux | egrep "(IBGateway|ibkr_trading_engine.py|ibkr_connector)" | egrep -v "egrep|check_ibkr_status.sh" || echo "No IBKR processes detected"
echo "Check IBKR logs at logs/ibkr_engine.log if present"
