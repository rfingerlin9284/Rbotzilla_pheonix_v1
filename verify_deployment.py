#!/usr/bin/env python3
"""
Verify all core strategies and modules are importable and provide basic diagnostics
This script runs quick checks to ensure the core modules and connectors can import and basic functions work.
"""
import importlib
import os
from typing import List

MODULES_TO_CHECK = {
    'required': [
        'logic.smart_logic',
        'oanda.oanda_trading_engine',
        'util.dynamic_leverage',
        'util.leverage_plan',
        'util.narration_logger',
    ],
    'optional': [
        'ibkr_gateway.ibkr_trading_engine',
    ]
}

def check_imports(mods: List[str]) -> bool:
    ok = True
    for m in mods:
        try:
            importlib.import_module(m)
            print(f"✅ {m} imported")
        except Exception as e:
            print(f"❌ {m} failed to import: {e}")
            ok = False
    return ok

def check_env():
    print('\nEnvironment overview:')
    keys = ['RICK_PIN','RICK_DEV_MODE','RICK_AGGRESSIVE_PLAN','RICK_AGGRESSIVE_LEVERAGE','RICK_LEVERAGE_MAX','RICK_LEVERAGE_AGGRESSIVENESS']
    for k in keys:
        print(f"  {k}: {os.getenv(k, '<unset>')}")

def main():
    print('VERIFY DEPLOYMENT — RICK CORE CHECKS')
    print('------------------------------------\n')
    ok_required = check_imports(MODULES_TO_CHECK['required'])
    print('\nOptional modules:')
    ok_optional = check_imports(MODULES_TO_CHECK['optional'])
    check_env()
    overall_ok = ok_required
    print('\nResult: ' + ('OK' if overall_ok else 'FAIL'))
    return 0 if overall_ok else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
