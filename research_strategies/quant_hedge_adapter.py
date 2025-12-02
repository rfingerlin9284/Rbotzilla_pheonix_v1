from __future__ import annotations
from typing import Dict, Any
import numpy as np
from hive.quant_hedge_rules import QuantHedgeRules


def compute_hedge_recommendation(close_prices, volume, account_nav=10000.0, margin_used=0.0, open_positions=0, correlation_matrix=None):
    """Wrapper to produce quant hedge analysis for research backtests.
    Returns a dict with the primary action and position multiplier.
    """
    try:
        q = QuantHedgeRules()
        analysis = q.analyze_market_conditions(
            prices=np.array(close_prices),
            volume=np.array(volume),
            account_nav=account_nav,
            margin_used=margin_used,
            open_positions=open_positions,
            correlation_matrix=correlation_matrix,
            lookback_periods=50
        )
        return {
            'primary_action': analysis.primary_action,
            'position_size_multiplier': analysis.position_size_multiplier,
            'confidence': analysis.confidence,
            'summary': analysis.summary
        }
    except Exception as e:
        return {'primary_action': 'WAIT_FOR_CLARITY', 'position_size_multiplier': 1.0, 'confidence': 0.0, 'summary': str(e)}
