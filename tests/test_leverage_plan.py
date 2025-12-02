#!/usr/bin/env python3
import os
from util.leverage_plan import plan_enabled, get_current_leverage, compute_units_with_leverage


def test_leverage_plan_units_calculation(monkeypatch):
    # Simulate aggressive plan enabled and leverage 3x
    monkeypatch.setenv('RICK_AGGRESSIVE_PLAN', '1')
    monkeypatch.setenv('RICK_AGGRESSIVE_LEVERAGE', '3')
    # Mock start date far in the past to get default schedule
    monkeypatch.setenv('RICK_AGGRESSIVE_START', '2024-01-01T00:00:00+00:00')

    assert plan_enabled()
    lev = get_current_leverage()
    assert lev >= 3.0

    # Suppose entry price is 1.0, account nav 5000, min notional 15000
    units, used_lev = compute_units_with_leverage(entry_price=1.0, account_nav=5000.0, min_notional=15000.0)
    # max_notional = account_nav * lev >= 5000 * 3 = 15000, so units should attempt to 15000 / 1 = 15000 approx
    assert units >= 15000
    assert used_lev >= 3.0


if __name__ == '__main__':
    os.environ['RICK_AGGRESSIVE_PLAN'] = '1'
    os.environ['RICK_AGGRESSIVE_LEVERAGE'] = '3'
    os.environ['RICK_AGGRESSIVE_START'] = '2024-01-01T00:00:00+00:00'
    test_leverage_plan_units_calculation(monkeypatch=type('M', (), {'setenv': os.environ.__setitem__})())
    print('leverage plan test PASSED')
