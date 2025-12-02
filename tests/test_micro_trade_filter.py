#!/usr/bin/env python3
import os
import pytest
from util.micro_trade_filter import should_block_micro_trade


def test_small_trade_blocked():
    env = {
        'MIN_NET_PROFIT_USD': '5',
        'MIN_RISK_PER_TRADE_USD': '5',
        'EST_FEE_RATE_BPS_OANDA': '1.5',
        'EST_FEE_RATE_BPS_IBKR': '2.0',
        'ALLOW_MICRO_TRADES': '0'
    }
    # tiny units -> tiny reward
    block, info = should_block_micro_trade('EUR_USD', 'LONG', 1.10, 1.0995, 1.1005, 10, 'OANDA', env)
    assert block is True
    assert info['reason'] in ('risk_below_min', 'net_profit_below_min', 'fees_eat_profit')
    assert 'risk_usd' in info and 'reward_usd' in info


def test_medium_trade_allowed():
    env = {
        'MIN_NET_PROFIT_USD': '5',
        'MIN_RISK_PER_TRADE_USD': '5',
        'EST_FEE_RATE_BPS_OANDA': '1.5',
        'EST_FEE_RATE_BPS_IBKR': '2.0',
        'ALLOW_MICRO_TRADES': '0'
    }
    # Larger units and wider TP -> pass
    block, info = should_block_micro_trade('EUR_USD', 'LONG', 1.10, 1.0900, 1.1100, 2000, 'OANDA', env)
    assert block is False
    assert info['net_expected_profit_usd'] >= float(env['MIN_NET_PROFIT_USD'])
    assert info['risk_usd'] >= float(env['MIN_RISK_PER_TRADE_USD'])


def test_allow_micro_override():
    env = {
        'MIN_NET_PROFIT_USD': '500',
        'MIN_RISK_PER_TRADE_USD': '500',
        'EST_FEE_RATE_BPS_OANDA': '1.5',
        'EST_FEE_RATE_BPS_IBKR': '2.0',
        'ALLOW_MICRO_TRADES': '1'
    }
    # Small trade but override allows
    block, info = should_block_micro_trade('EUR_USD', 'LONG', 1.10, 1.0995, 1.1005, 10, 'OANDA', env)
    assert block is False


def test_ibkr_fee_rate_switch():
    env = {
        'MIN_NET_PROFIT_USD': '1',
        'MIN_RISK_PER_TRADE_USD': '1',
        'EST_FEE_RATE_BPS_OANDA': '1.0',
        'EST_FEE_RATE_BPS_IBKR': '50.0',  # huge fee bps to simulate IBKR
        'ALLOW_MICRO_TRADES': '0'
    }
    # For same trade, IBKR fees high enough to block
    # Units such that reward_usd = 10; with IBKR fee 50 bps => fees = 0.5*10 = 5 -> net = 5 -> above min 1
    # Make fees so net falls below min
    env['MIN_NET_PROFIT_USD'] = '1'
    # Use small units so fees can meaningfully reduce net profit for IBKR
    block_ibkr, info_ibkr = should_block_micro_trade('EUR_USD', 'LONG', 1.10, 1.0990, 1.1100, 100, 'IBKR', env)
    assert block_ibkr is True
    assert 'estimated_fees_usd' in info_ibkr


def test_estimate_usd_notional():
    from util.notional_utils import estimate_usd_notional
    # EUR_USD -> price * units
    assert estimate_usd_notional('EUR_USD', 1.0, 100) == pytest.approx(100.0)
    # USD_JPY -> units
    assert estimate_usd_notional('USD_JPY', 150.0, 100) == pytest.approx(100.0)
    # GBP_JPY (cross) -> price * units * scale (default 1.0)
    assert estimate_usd_notional('GBP_JPY', 150.0, 2) == pytest.approx(300.0)


if __name__ == '__main__':
    test_small_trade_blocked()
    test_medium_trade_allowed()
    test_allow_micro_override()
    test_ibkr_fee_rate_switch()
    print('ok')
