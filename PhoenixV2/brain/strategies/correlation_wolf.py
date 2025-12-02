"""
Correlation Wolf - Cross-market correlation based signals

Compares BTC vs. SPX (or NAS) correlation and votes accordingly.
"""
from typing import Dict, Any
import logging
try:
    import pandas as pd
except Exception:
    pd = None

logger = logging.getLogger("CorrelationWolf")


class CorrelationWolf:
    """Fetches additional market_data keys (btc_df and spx_df) and computes correlation.
    If high positive correlation and SPX is bullish -> BUY BTC. If SPX bearish -> SELL BTC.
    Otherwise HOLD.
    """

    name = 'correlation_wolf'

    def vote(self, market_data: Dict[str, Any]) -> str:
        try:
            btc_df = market_data.get('btc_df') or market_data.get('BTC') or None
            spx_df = market_data.get('spx_df') or market_data.get('SPX') or None
            if btc_df is None or spx_df is None:
                return 'HOLD'
            if pd is None:
                return 'HOLD'
            # Ensure we have close columns
            if 'close' not in getattr(btc_df, 'columns', []) or 'close' not in getattr(spx_df, 'columns', []):
                return 'HOLD'
            # Calculate returns and correlation over last 60 periods or available length
            btc_returns = btc_df['close'].pct_change().dropna().tail(60)
            spx_returns = spx_df['close'].pct_change().dropna().tail(60)
            if len(btc_returns) < 5 or len(spx_returns) < 5:
                return 'HOLD'
            # Align indexes
            combined = pd.concat([btc_returns, spx_returns], axis=1, join='inner')
            if combined.shape[0] < 5:
                return 'HOLD'
            corr = float(combined.iloc[:,0].corr(combined.iloc[:,1]))
            # Determine SPX direction (last close vs prev)
            spx_last = float(spx_df['close'].iloc[-1])
            spx_prev = float(spx_df['close'].iloc[-2]) if len(spx_df) > 1 else spx_last
            spx_bullish = spx_last > spx_prev
            # thresholds
            if corr > 0.8:
                return 'BUY' if spx_bullish else 'SELL'
            # if decoupled, don't push a direction
            if abs(corr) < 0.5:
                return 'HOLD'
            # for moderate correlation, let others decide
            return 'HOLD'
        except Exception as e:
            logger.debug(f"CorrelationWolf error: {e}")
            return 'HOLD'
