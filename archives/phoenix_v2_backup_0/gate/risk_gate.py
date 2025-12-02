"""
PhoenixV2 Gate Module - Risk Gate

The Final Authority on whether a trade is executed.
Enforces all charter rules: timeframes, sizes, margins, and correlations.
"""
import logging
import sys
import os
from typing import Dict, Any, Tuple, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.charter import Charter
from .correlation_monitor import CorrelationMonitor

logger = logging.getLogger("RiskGate")


class RiskGate:
    """
    The Risk Gate - Guardian of the Account.
    All trade signals must pass through this gate before execution.
    """
    
    def __init__(self, auth_manager):
        self.is_live = auth_manager.is_live()
        self.min_size = Charter.get_min_size(self.is_live)
        self.correlation_monitor = CorrelationMonitor(max_correlated_positions=2)

    def check_portfolio_state(self, portfolio_state: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check overall portfolio health.
        Called before any trade to ensure system is in safe state.
        """
        # 1. Check Daily Loss Breaker (5% max daily loss)
        daily_dd = portfolio_state.get('daily_drawdown_pct', 0)
        if daily_dd > 0.05:
            logger.warning(f"🛑 DAILY LOSS BREAKER: {daily_dd*100:.1f}% drawdown")
            return False, "DAILY_LOSS_BREAKER_ACTIVE"
        
        # 2. Check Margin Utilization
        margin_pct = portfolio_state.get('margin_used_pct', 0)
        if margin_pct > Charter.MAX_MARGIN_UTILIZATION:
            logger.warning(f"🛑 MARGIN CAP: {margin_pct*100:.1f}% used")
            return False, "MARGIN_CAP_HIT"
        
        # 3. Check Position Count (max 5 concurrent)
        position_count = len(portfolio_state.get('open_positions', []))
        if position_count >= 5:
            logger.warning(f"🛑 MAX POSITIONS: {position_count} open")
            return False, "MAX_POSITIONS_REACHED"
            
        return True, "OK"

    def validate_signal(self, signal: Dict[str, Any], 
                       current_positions: List[Dict[str, Any]] = None) -> Tuple[bool, str]:  # type: ignore
        """
        Validate a trading signal against all charter rules.
        
        Args:
            signal: The trade signal to validate
            current_positions: List of current open positions (for correlation check)
        
        Returns:
            Tuple of (is_approved: bool, reason: str)
        """
        symbol = signal.get('symbol', 'UNKNOWN')
        direction = signal.get('direction', 'BUY')
        
        # 1. Timeframe Check
        tf = signal.get('timeframe', 'M15')
        if tf in ['M1', 'M5']:
            logger.info(f"🛡️ REJECTED: {symbol} - Timeframe {tf} below M15 floor")
            return False, "TIMEFRAME_TOO_LOW_M15_REQ"

        # 2. Size Check
        notional = float(signal.get('notional_value', 0))
        if notional < self.min_size:
            logger.info(f"🛡️ REJECTED: {symbol} - Size ${notional:,.0f} < ${self.min_size:,}")
            return False, f"SIZE_TOO_SMALL_MIN_${self.min_size}"

        # 3. OCO Check (Stop Loss + Take Profit required)
        if Charter.OCO_MANDATORY:
            if not signal.get('sl') or not signal.get('tp'):
                logger.info(f"🛡️ REJECTED: {symbol} - Missing SL/TP")
                return False, "MISSING_OCO_SL_TP"

        # 4. Risk/Reward Check (3:1 minimum)
        entry = signal.get('entry', 0)
        sl = signal.get('sl', 0)
        tp = signal.get('tp', 0)
        
        if entry and sl and tp:
            risk = abs(entry - sl)
            reward = abs(tp - entry)
            if risk > 0:
                rr_ratio = reward / risk
                if rr_ratio < 3.0:
                    logger.info(f"🛡️ REJECTED: {symbol} - RR {rr_ratio:.1f}:1 < 3:1")
                    return False, f"RR_RATIO_TOO_LOW_{rr_ratio:.1f}"

        # 5. Correlation Check
        if current_positions:
            corr_ok, corr_reason = self.correlation_monitor.check_correlation(
                symbol, direction, current_positions
            )
            if not corr_ok:
                logger.info(f"🛡️ REJECTED: {symbol} - {corr_reason}")
                return False, corr_reason

        logger.info(f"✅ APPROVED: {symbol} {direction}")
        return True, "APPROVED"

    def get_gate_status(self) -> Dict[str, Any]:
        """Return current gate configuration."""
        return {
            "mode": "LIVE" if self.is_live else "PAPER",
            "min_size": self.min_size,
            "max_margin": Charter.MAX_MARGIN_UTILIZATION,
            "max_risk_per_trade": Charter.MAX_RISK_PER_TRADE,
            "oco_mandatory": Charter.OCO_MANDATORY,
            "min_timeframe": Charter.MIN_TIMEFRAME
        }
