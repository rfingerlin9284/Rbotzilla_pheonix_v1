#!/usr/bin/env python3
import math
from util.dynamic_stops import compute_dynamic_sl_tp, get_pip_value


def test_compute_dynamic_sl_tp_long_atr_based():
    symbol = 'EUR_USD'
    entry = 1.1000
    atr = 0.0010  # 10 pips
    sl, tp = compute_dynamic_sl_tp('LONG', symbol, entry, atr, last_liquidity_level=None, rr=3.2)
    pip = get_pip_value(symbol)
    # Default ATR_MULTIPLE=1.5 -> 15 pips -> this should translate
    expected_risk_pips = max(10.0, min(80.0, max(1.5 * (atr / pip), 0.0)))
    expected_risk_price = expected_risk_pips * pip
    assert math.isclose(sl, round(entry - expected_risk_price, 5))
    assert math.isclose(tp, round(entry + 3.2 * expected_risk_price, 5))


def test_compute_dynamic_sl_tp_short_liquidity_based():
    symbol = 'GBP_JPY'
    entry = 150.50
    # ATR small, but liquidity level makes risk larger
    atr = 0.005
    last_liq = 150.70
    sl, tp = compute_dynamic_sl_tp('SHORT', symbol, entry, atr, last_liquidity_level=last_liq, rr=3.2)
    pip = get_pip_value(symbol)
    liquidity_pips = abs(entry - last_liq) / pip + 3.0
    expected_risk_pips = max(10.0, min(80.0, max(1.5 * (atr / pip), liquidity_pips)))
    expected_risk_price = expected_risk_pips * pip
    assert math.isclose(sl, round(entry + expected_risk_price, 3))
    # Round expected tp by pip increments (JPY uses 0.01 pips) to match implementation
    pip = get_pip_value(symbol)
    expected_tp_exact = entry - 3.2 * expected_risk_price
    expected_tp_quantized = round(round(expected_tp_exact / pip) * pip, 3)
    assert math.isclose(tp, expected_tp_quantized)


def test_compute_dynamic_sl_tp_respects_broker_min_stop():
    symbol = 'EUR_USD'
    entry = 1.1000
    atr = 0.0004  # 4 pips
    # If broker min stop pips is 8 but ATR suggests 6, the computed pips should be >=8
    sl, tp = compute_dynamic_sl_tp('LONG', symbol, entry, atr, last_liquidity_level=None, rr=3.2, broker_min_stop_pips=8.0)
    pip = get_pip_value(symbol)
    sl_pips = round((entry - sl) / pip)
    assert sl_pips >= 8


def test_compute_dynamic_sl_tp_spread_effect():
    symbol = 'EUR_USD'
    entry = 1.1000
    atr = 0.0010
    # With a large spread buffer, min risk should increase
    sl_small, tp_small = compute_dynamic_sl_tp('LONG', symbol, entry, atr, last_liquidity_level=None, rr=3.2, spread_pips=2.0)
    sl_big, tp_big = compute_dynamic_sl_tp('LONG', symbol, entry, atr, last_liquidity_level=None, rr=3.2, spread_pips=20.0)
    assert sl_big < sl_small  # bigger spread -> wider stop (smaller price for long SL)


def test_compute_dynamic_sl_tp_max_rr_cap():
    symbol = 'EUR_USD'
    entry = 1.1000
    atr = 0.0010
    # If rr is very large, the max_rr cap should limit the TP
    sl, tp = compute_dynamic_sl_tp('LONG', symbol, entry, atr, last_liquidity_level=None, rr=100.0, max_rr=5.0)
    # Compute risk price
    pip = get_pip_value(symbol)
    atr_pips = atr / pip
    expected_risk_pips = max(10.0, min(80.0, max(1.5 * atr_pips, 0.0)))
    expected_risk_price = expected_risk_pips * pip
    assert math.isclose(tp, round(entry + 5.0 * expected_risk_price, 5))


if __name__ == '__main__':
    test_compute_dynamic_sl_tp_long_atr_based()
    test_compute_dynamic_sl_tp_short_liquidity_based()
    print('Dynamic stops tests passed')
