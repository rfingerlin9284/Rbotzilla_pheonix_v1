"""
Allocation Manager
Calculates adjusted position size based on strategy weights and base notional.
ENHANCED with The Architect (Alpha Intelligence).
"""
from typing import Dict, Any, Optional
import pandas as pd
from PhoenixV2.core.state_manager import StateManager
from PhoenixV2.config.charter import Charter
from PhoenixV2.brain.architect import AlphaArchitect
import logging

logger = logging.getLogger("AllocationManager")

class AllocationManager:
    """Manage strategy-based allocation size adjustments.

    Uses StateManager to fetch strategy weights, applies caps, and returns an adjusted notional.
    Now powered by The Architect for dynamic volatility sizing.
    """

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.architect = AlphaArchitect()
        # hard caps - conservative defaults
        self.max_multiplier = 3.0
        self.min_multiplier = 0.5

    def calculate_size(self, strategy_name: str, base_notional: float, portfolio_state: Optional[Dict[str, Any]] = None, entry: Optional[float] = None, sl: Optional[float] = None, market_data: Optional[Dict[str, Any]] = None) -> float:
        """Return adjusted notional based on strategy weight and portfolio constraints.

        Caps the size between min and max multipliers and also ensures the result meets
        the charter minimum notional requirements.
        """
        try:
            weight = float(self.state_manager.get_strategy_weight(strategy_name) or 1.0)
        except Exception:
            weight = 1.0

        # 2. The Architect: Dynamic Volatility Sizing (Regime Awareness)
        vol_multiplier = 1.0
        try:
            if market_data and isinstance(market_data.get('df', None), pd.DataFrame):
                df = market_data['df']
                # Ask the Architect for the regime
                regime_data = self.architect.detect_regime(df)
                current_atr = regime_data.get('atr', 0.0)
                vol_ratio = regime_data.get('vol_ratio', 1.0)
                
                # Get Quant Analysis if possible
                quant_mult = None
                try:
                    prices = df['close'].values
                    volume = df['volume'].values
                    analysis = self.architect.analyze_market_conditions(prices, volume)
                    if analysis:
                        quant_mult = analysis.position_size_multiplier
                        logger.debug(f"ALLOCATION: QuantHedgeRules suggests {quant_mult}x multiplier.")
                except Exception:
                    pass
                
                # Calculate dynamic multiplier based on volatility
                # If volatility is LOW, we can size UP safely.
                # If volatility is HIGH, we size DOWN.
                nav = float(portfolio_state.get('total_nav', 0.0)) if portfolio_state else 10000.0
                if current_atr > 0:
                     vol_multiplier = self.architect.get_dynamic_leverage_size(nav, current_atr, vol_ratio, quant_multiplier=quant_mult)
                
                logger.debug(f"ALLOCATION: Architect suggests {vol_multiplier:.2f}x based on {regime_data.get('regime')} regime.")
        except Exception as e:
            logger.debug(f"Allocation Architect Error: {e}")
            vol_multiplier = 1.0

        adjusted = base_notional * weight * vol_multiplier
        if adjusted > base_notional * self.max_multiplier:
            adjusted = base_notional * self.max_multiplier
        if adjusted < base_notional * self.min_multiplier:
            adjusted = base_notional * self.min_multiplier

        # Ensure adjusted size respects charter min_size for live/paper
        try:
            min_size = Charter.get_min_size(self.state_manager.get_state().get('mode') == 'LIVE')
        except Exception:
            min_size = Charter.MIN_NOTIONAL_PAPER

        if adjusted < min_size:
            adjusted = min_size

        # Profit Ratchet Aggression Scaling: if the system has made at least $300 in profit for the day,
        # scale up aggression linearly by 1 + (current_daily_pnl - 300)/1000, capped 2.0x.
        try:
            profit_multiplier = 1.0
            if portfolio_state:
                start = float(portfolio_state.get('daily_start_balance', 0.0) or 0.0)
                current_balance = float(portfolio_state.get('current_balance', 0.0) or 0.0)
                if start > 0:
                    current_daily_pnl = float(current_balance - start)
                    if current_daily_pnl > 300:
                        profit_multiplier = 1.0 + (current_daily_pnl - 300.0) / 1000.0
                        if profit_multiplier > 2.0:
                            profit_multiplier = 2.0
                        logger.warning(f"🔥 HOT HAND: Scaling up due to daily profit ${current_daily_pnl:.2f} → multiplier {profit_multiplier:.2f}")
            adjusted = adjusted * profit_multiplier
        except Exception:
            pass

        # If we have portfolio state and entry/sl, cap the size based on charter risk
        try:
            nav = float(portfolio_state.get('total_nav', 0.0)) if portfolio_state else 0.0
            if nav > 0 and entry and sl and entry != 0:
                # Risk per unit in price terms
                risk_per_unit = abs(entry - sl)
                # risk percent relative to entry price
                risk_pct = (risk_per_unit / abs(entry)) if entry != 0 else 0.0
                if risk_pct > 0:
                    allowed_notional = (nav * Charter.MAX_RISK_PER_TRADE) / risk_pct
                else:
                    allowed_notional = (nav * Charter.MAX_RISK_PER_TRADE)
                # cap adjusted to not exceed allowed_notional
                if adjusted > allowed_notional:
                    adjusted = allowed_notional
        except Exception:
            pass

        return float(adjusted)
