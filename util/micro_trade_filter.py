#!/usr/bin/env python3
"""
Micro trade filter

Provides a single gate that blocks tiny / micro trades unless they pass
a configurable minimum net profit after estimated fees. Engines should call
should_block_micro_trade() prior to placing any orders (OCO or market).

This is intentionally conservative and uses simple USD-equivalent math.
"""
from typing import Tuple, Dict, Mapping, Optional, Any
import os
from decimal import Decimal
from util.dynamic_stops import get_pip_value
from util.notional_utils import estimate_usd_notional
from util.narration_logger import log_narration


def _get_env(env: Mapping[str, str] | None) -> Mapping[str, str]:
    if env is not None:
        return env
    return os.environ


def _float_env(env: Mapping[str, str], name: str, default: float) -> float:
    val = env.get(name)
    if val is None:
        return float(default)
    try:
        return float(val)
    except Exception:
        return float(default)


def should_block_micro_trade(
    symbol: str,
    side: str,
    entry_price: float,
    stop_loss_price: float,
    take_profit_price: float,
    units: float,
    venue: str,
    env: Optional[Mapping[str, str]] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """
    Return (block, info_dict) — whether the trade should be blocked because
    it is a micro-trade according to configured thresholds.
    """
    env_vars = _get_env(env)

    MIN_NET_PROFIT_USD = _float_env(env_vars, 'MIN_NET_PROFIT_USD', 5.0)
    MIN_RISK_PER_TRADE_USD = _float_env(env_vars, 'MIN_RISK_PER_TRADE_USD', 5.0)
    EST_FEE_RATE_BPS_OANDA = _float_env(env_vars, 'EST_FEE_RATE_BPS_OANDA', 1.5)
    EST_FEE_RATE_BPS_IBKR = _float_env(env_vars, 'EST_FEE_RATE_BPS_IBKR', 2.0)
    ALLOW_MICRO_TRADES = str(env_vars.get('ALLOW_MICRO_TRADES', '0')).strip()

    fee_rate_bps = EST_FEE_RATE_BPS_OANDA if venue.upper().startswith('O') or 'OANDA' in venue.upper() else EST_FEE_RATE_BPS_IBKR

    # Basic price-based risk/reward calculation (USD-approximation)
    try:
        pip = get_pip_value(symbol)
        risk_price = abs(float(entry_price) - float(stop_loss_price))
        reward_price = abs(float(take_profit_price) - float(entry_price))
        u = abs(float(units))
        # Convert to pips / values for reporting
        risk_pips = risk_price / pip if pip else 0.0
        reward_pips = reward_price / pip if pip else 0.0
    except Exception:
        # If conversion fails, block to be safe
        return True, {
            'venue': venue,
            'symbol': symbol,
            'risk_usd': 0.0,
            'reward_usd': 0.0,
            'estimated_fees_usd': 0.0,
            'net_expected_profit_usd': 0.0,
            'min_net_profit_usd': MIN_NET_PROFIT_USD,
            'min_risk_usd': MIN_RISK_PER_TRADE_USD,
            'reason': 'invalid_params'
        }

    # Risk and reward in USD-equivalent (approx): price difference * units
    # Using pip conversions to stay consistent with other utils
    # Use USD notional helper for a more accurate, deterministic conversion
    risk_usd = estimate_usd_notional(symbol, risk_price, u, env_vars)
    reward_usd = estimate_usd_notional(symbol, reward_price, u, env_vars)

    estimated_fees_usd = reward_usd * (fee_rate_bps / 10000.0)
    net_expected_profit_usd = reward_usd - estimated_fees_usd

    info = {
        'venue': venue,
        'symbol': symbol,
        'side': side,
        'units': u,
        'entry_price': entry_price,
        'stop_loss_price': stop_loss_price,
        'take_profit_price': take_profit_price,
        'pip': pip,
        'risk_pips': round(risk_pips, 4),
        'reward_pips': round(reward_pips, 4),
        'risk_usd': round(risk_usd, 4),
        'reward_usd': round(reward_usd, 4),
        'estimated_fees_usd': round(estimated_fees_usd, 4),
        'net_expected_profit_usd': round(net_expected_profit_usd, 4),
        'fee_rate_bps': fee_rate_bps,
        'min_net_profit_usd': MIN_NET_PROFIT_USD,
        'min_risk_usd': MIN_RISK_PER_TRADE_USD,
        'allow_micro_trades': ALLOW_MICRO_TRADES,
    }

    if ALLOW_MICRO_TRADES == '1':
        # Micro trades enabled — do not block but log info
        try:
            log_narration('MICRO_TRADE_CHECK_PASSED', info, symbol=symbol, venue=venue)
        except Exception:
            pass
        return False, info

    # Block rules
    block = False
    if risk_usd < MIN_RISK_PER_TRADE_USD:
        block = True
        info['reason'] = 'risk_below_min'
    elif net_expected_profit_usd < MIN_NET_PROFIT_USD:
        block = True
        info['reason'] = 'net_profit_below_min'
    elif net_expected_profit_usd <= 0:
        block = True
        info['reason'] = 'fees_eat_profit'

    # Log blocked trades
    try:
        if block:
            log_narration('MICRO_TRADE_BLOCKED', info, symbol=symbol, venue=venue)
        else:
            log_narration('MICRO_TRADE_CHECK_PASSED', info, symbol=symbol, venue=venue)
    except Exception:
        # Never fail due to logging
        pass

    return block, info


if __name__ == '__main__':
    # Quick manual test
    print(should_block_micro_trade('EUR_USD', 'LONG', 1.10, 1.095, 1.12, 1_000, 'OANDA', env={'ALLOW_MICRO_TRADES': '0'}))
