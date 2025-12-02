import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from util.micro_trade_filter import should_block_micro_trade
import util.micro_trade_filter as mtf

def test_ibkr_paper_thresholds():
    # Mock environment for IBKR Paper
    env = {
        'ENV_NAME': 'paper',
        'TRADING_ENVIRONMENT': 'sandbox',
        'PAPER_MODE': 'true',
    }

    # Mock estimate_usd_notional to return (price_diff * units) for simplicity
    original_estimate = mtf.estimate_usd_notional
    mtf.estimate_usd_notional = lambda symbol, price_diff, units, env: price_diff * units
    
    # Mock get_pip_value
    original_get_pip = mtf.get_pip_value
    mtf.get_pip_value = lambda symbol: 0.0001

    try:
        # 1. Tiny Trade: Risk $0.10 -> Should be BLOCKED
        # Entry 100, SL 99.9 (Diff 0.1). Units 1. Risk = $0.10.
        blocked, info = should_block_micro_trade(
            symbol='BTC_USD', side='LONG',
            entry_price=100.0, stop_loss_price=99.9, take_profit_price=100.2,
            units=1.0, venue='IBKR', env=env
        )
        assert blocked, f"Tiny trade ($0.10 risk) should be blocked. Info: {info}"
        assert info['reason'] == 'risk_below_min'

        # 2. Small Trade: Risk $3.00 -> Should be ALLOWED in paper mode (Threshold 2.5)
        # Entry 100, SL 97.0 (Diff 3.0). Units 1. Risk = $3.00.
        blocked, info = should_block_micro_trade(
            symbol='BTC_USD', side='LONG',
            entry_price=100.0, stop_loss_price=97.0, take_profit_price=106.0,
            units=1.0, venue='IBKR', env=env
        )
        assert not blocked, f"Small trade ($3.00 risk) should be allowed in paper mode. Info: {info}"

        # 3. Standard Trade: Risk $10.00 -> Should be ALLOWED
        # Entry 100, SL 90.0 (Diff 10.0). Units 1. Risk = $10.00.
        blocked, info = should_block_micro_trade(
            symbol='BTC_USD', side='LONG',
            entry_price=100.0, stop_loss_price=90.0, take_profit_price=120.0,
            units=1.0, venue='IBKR', env=env
        )
        assert not blocked, f"Standard trade ($10.00 risk) should be allowed. Info: {info}"

    finally:
        mtf.estimate_usd_notional = original_estimate
        mtf.get_pip_value = original_get_pip
