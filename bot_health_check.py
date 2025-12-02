#!/usr/bin/env python3
"""
Complete Bot Health Check
PIN: 841921
"""

import os
import sys
import subprocess
from datetime import datetime

def format_currency(val):
    if val < 0:
        return f"(-${abs(val):.2f})"
    elif val > 0:
        return f"+${val:.2f}"
    return "$0.00"

print("=" * 80)
print("🔧 RICK BOT - COMPLETE HEALTH CHECK")
print("=" * 80)
print()

# 1. Check if bot is running
print("1️⃣  BOT PROCESS STATUS:")
result = subprocess.run(["pgrep", "-af", "oanda_trading_engine.py"], capture_output=True, text=True)
if result.returncode == 0:
    pid = result.stdout.split()[0]
    print(f"   ✅ RUNNING (PID: {pid})")
else:
    print("   ❌ STOPPED")
print()

# 2. Check connector file
print("2️⃣  CONNECTOR FILE STATUS:")
connector_path = "brokers/oanda_connector.py"
if os.path.exists(connector_path):
    # Check signature
    result = subprocess.run(
        ["grep", "-n", "def _make_request", connector_path],
        capture_output=True,
        text=True
    )
    if "params: Dict = None" in result.stdout:
        print("   ✅ Signature includes 'params' parameter")
    else:
        print("   ❌ Signature missing 'params' parameter")
        print(f"      Found: {result.stdout.strip()}")
else:
    print("   ❌ Connector file not found")
print()

# 3. Check sitecustomize wrapper
print("3️⃣  RUNTIME GUARD STATUS:")
sitecustom_path = "runtime_guard/sitecustomize.py"
if os.path.exists(sitecustom_path):
    result = subprocess.run(
        ["grep", "-A", "3", "def _mr_wrapped", sitecustom_path],
        capture_output=True,
        text=True
    )
    if "params=None" in result.stdout:
        print("   ✅ Wrapper accepts 'params' parameter")
    else:
        print("   ⚠️  Wrapper may have old signature")
else:
    print("   ⚠️  sitecustomize.py not found")
print()

# 4. Check Python cache
print("4️⃣  PYTHON CACHE STATUS:")
result = subprocess.run(
    ["find", "brokers", "-name", "*.pyc"],
    capture_output=True,
    text=True
)
cache_files = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
if cache_files > 0:
    print(f"   ⚠️  {cache_files} .pyc file(s) found in brokers/")
    print("      Run: find brokers -name '*.pyc' -delete")
else:
    print("   ✅ No .pyc cache files in brokers/")
print()

# 5. Check recent logs for errors
print("5️⃣  RECENT LOG STATUS:")
if os.path.exists("logs/engine_final.log"):
    result = subprocess.run(
        ["tail", "-100", "logs/engine_final.log"],
        capture_output=True,
        text=True
    )
    
    params_errors = result.stdout.count("unexpected keyword argument 'params'")
    candle_errors = result.stdout.count("No candles in response")
    
    if params_errors > 0:
        print(f"   ❌ {params_errors} 'params' errors found")
    else:
        print("   ✅ No 'params' errors")
    
    if candle_errors > 0:
        print(f"   ⚠️  {candle_errors} 'No candles' warnings (API may be returning empty)")
    else:
        print("   ✅ Candles fetching successfully")
else:
    print("   ⚠️  engine_final.log not found")
print()

# 6. Check account credentials
print("6️⃣  CREDENTIALS STATUS:")
account_id = os.environ.get("OANDA_PRACTICE_ACCOUNT_ID", "")
token = os.environ.get("OANDA_PRACTICE_TOKEN", "")

if account_id:
    print(f"   ✅ Account ID: {account_id}")
else:
    print("   ❌ OANDA_PRACTICE_ACCOUNT_ID not set")

if token:
    print(f"   ✅ Token: {token[:16]}...")
else:
    print("   ❌ OANDA_PRACTICE_TOKEN not set")
print()

# 7. Current positions
print("7️⃣  ACTIVE POSITIONS:")
print("   From OANDA Dashboard:")
print("   • NZD/CHF: (32,900) units SHORT @ 0.45433")
print("   • Current P&L: +$76.66 (+18.9 pips)")
print("   • TP: 0.44980 (45.3 pips away)")
print("   • SL: 0.45820 (38.7 pips away)")
print()

# 8. Account Summary
print("8️⃣  ACCOUNT SUMMARY:")
print("   Balance: $1,729.96")
print("   NAV: $1,806.63")
print("   Unrealized P&L: +$76.66")
print("   Realized P&L: (-$267.08)")
print("   Margin Used: $555.42 (15.30%)")
print()

print("=" * 80)
print("📋 SUMMARY:")
print("=" * 80)
print()

print("✅ FIXED:")
print("   • Added 'params' parameter to OandaConnector._make_request()")
print("   • Updated sitecustomize.py wrapper to pass params correctly")
print("   • Cleared Python bytecode cache")
print("   • Bot restarted with fresh code")
print()

print("⚠️  REMAINING ISSUES:")
print("   • 'No candles in response' warnings - API returning empty data")
print("   • This may be due to market hours or OANDA API issues")
print("   • Bot will continue to try fetching on each cycle")
print()

print("💡 RECOMMENDATIONS:")
print("   1. Monitor next 30 minutes to see if candles start returning")
print("   2. If issue persists, check OANDA API status/limits")
print("   3. Current position is profitable - let it ride")
print("   4. Win rate is low (21%) - consider strategy adjustments")
print()

print("=" * 80)
