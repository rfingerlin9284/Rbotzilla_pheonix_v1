"""
PhoenixV2 Gate Module - Risk Gate

The Final Authority on whether a trade is executed.
Enforces all charter rules: timeframes, sizes, margins, and correlations.
"""
import logging
import sys
import os
from typing import Dict, Any, Tuple, List, Optional
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PhoenixV2.config.charter import Charter
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
        # Allow smaller min size for crypto instruments (defaults to $10)
        self.min_crypto_notional = int(os.getenv('MIN_CRYPTO_NOTIONAL', '10'))
        self.correlation_monitor = CorrelationMonitor(max_correlated_positions=2)

    def check_portfolio_state(self, portfolio_state: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check overall portfolio health.
        Called before any trade to ensure system is in safe state.
        Implements a 'Profit Ratchet' mechanism: once the daily peak PnL reaches a configured
        threshold (default $300), a daily lock/floor is established at 80% of the observed peak.
        If current USD PnL subsequently drops below that lock/floor, the gate blocks new entries
        for the remainder of the day to preserve realized gains.
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
        
        # 3. Check Position Count (max concurrent)
        position_count = len(portfolio_state.get('open_positions', []))
        if position_count >= getattr(Charter, 'MAX_CONCURRENT_POSITIONS', 5):
            logger.warning(f"🛑 MAX POSITIONS: {position_count} open")
            return False, "MAX_POSITIONS_REACHED"

        # 4. Check Profit Ratchet Lock (do not give back a winning day)
        try:
            daily_start = float(portfolio_state.get('daily_start_balance', 0.0) or 0.0)
            current_balance = float(portfolio_state.get('current_balance', portfolio_state.get('total_nav', 0.0) or 0.0) or 0.0)
            # compute USD PnL
            current_pnl = float(current_balance - daily_start)
            # Prefer explicit lock level computed by StateManager (router sets 'profit_lock_level')
            lock_level = portfolio_state.get('profit_lock_level', None)
            # Also check fixed daily floor level (e.g., $300) provided by StateManager
            daily_floor = portfolio_state.get('daily_floor', None)
            if daily_floor is None:
                daily_floor = float('-inf')
            if lock_level is None:
                # fallback compute from daily_peak_pnl if present
                daily_peak = float(portfolio_state.get('daily_peak_pnl', 0.0) or 0.0)
                if daily_peak >= 300:
                    lock_level = daily_peak * 0.8
                else:
                    lock_level = float('-inf')
            # Check the hard floor (call it quits) first; if current pnl falls back to the fixed daily floor, halt
            if daily_floor != float('-inf') and current_pnl <= float(daily_floor):
                logger.warning(f"🛑 DAILY PROFIT FLOOR HIT: Current PnL ${current_pnl:.2f} <= Floor ${float(daily_floor):.2f}")
                return False, f"DAILY_PROFIT_FLOOR_TRIGGERED (PnL {current_pnl:.2f} <= Floor {float(daily_floor):.2f})"
            # If current pnl falls below lock level (ratio-based), call it quits for the day
            if lock_level != float('-inf') and current_pnl <= float(lock_level):
                logger.warning(f"🛑 DAILY PROFIT PROTECTION TRIGGERED: Current PnL ${current_pnl:.2f} < Lock ${float(lock_level):.2f}")
                return False, f"DAILY_PROFIT_PROTECTION_TRIGGERED (PnL {current_pnl:.2f} < Lock {float(lock_level):.2f})"
        except Exception:
            # Non-fatal - continue with other checks
            pass
            
        return True, "OK"

    def validate_signal(self, signal: Dict[str, Any], 
                       current_positions: Optional[List[Dict[str, Any]]] = None,
                       portfolio_state: Optional[Dict[str, Any]] = None,
                       market_data: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:  # type: ignore
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
        # if the symbol is a Coinbase/crypto product (has '-') allow smaller min_notional
        symbol = signal.get('symbol', '')
        required_min = self.min_size
        if '-' in symbol:
            required_min = self.min_crypto_notional
        if notional < required_min:
            logger.info(f"🛡️ REJECTED: {symbol} - Size ${notional:,.0f} < ${self.min_size:,}")
            return False, f"SIZE_TOO_SMALL_MIN_${required_min}"

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

        # 4.5 Symbol Concentration Check (Diversity Enforcement)
        if current_positions:
            # Count existing positions for this symbol
            # OANDA uses 'instrument', internal signals use 'symbol'
            symbol_count = sum(1 for p in current_positions if p.get('instrument') == symbol or p.get('symbol') == symbol)
            max_per_symbol = getattr(Charter, 'MAX_POSITIONS_PER_SYMBOL', 3)
            
            if symbol_count >= max_per_symbol:
                logger.info(f"🛡️ REJECTED: {symbol} - Max positions ({symbol_count}/{max_per_symbol}) reached for this symbol")
                return False, f"MAX_POSITIONS_PER_SYMBOL_REACHED_{symbol_count}"

        # 5. Correlation Check
        if current_positions:
            corr_ok, corr_reason = self.correlation_monitor.check_correlation(
                symbol, direction, current_positions
            )
            if not corr_ok:
                logger.info(f"🛡️ REJECTED: {symbol} - {corr_reason}")
                return False, corr_reason

        # 6. Scaling check - only allow adding to position if unrealized pnl is positive
        # 7. Per-Trade Risk Limit: ensure notional doesn't exceed charter limit based on SL
        try:
            # We need portfolio nav to compute allowed notional
            nav = 0.0
            if portfolio_state:
                nav = float(portfolio_state.get('total_nav', portfolio_state.get('current_balance', 0.0) or 0.0))
            entry = float(signal.get('entry') or 0.0)
            sl = float(signal.get('sl') or 0.0)
            if nav > 0 and entry and sl and entry != 0:
                risk_per_unit = abs(entry - sl)
                risk_pct = (risk_per_unit / abs(entry)) if entry != 0 else 0.0
                if risk_pct > 0:
                    allowed_notional = (nav * Charter.MAX_RISK_PER_TRADE) / risk_pct
                else:
                    allowed_notional = nav * Charter.MAX_RISK_PER_TRADE
                if notional > allowed_notional:
                    logger.info(f"🛡️ REJECTED: {symbol} - Notional ${notional:,.0f} exceeds allowed based on risk ${allowed_notional:,.0f}")
                    return False, "NOTIONAL_EXCEEDS_RISK_LIMIT"
        except Exception:
            pass
        add_to_position = signal.get('add_to_position') or signal.get('scaling') or signal.get('pyramid')
        if add_to_position:
            # If portfolio_state not provided, be conservative and disallow
            if not portfolio_state:
                logger.warning(f"🛑 REJECTED: {symbol} - Scaling attempted but no portfolio_state provided")
                return False, "SCALING_NOT_ALLOWED_NO_PORTFOLIO_STATE"
            unreal = float(portfolio_state.get('unrealized_pnl', 0.0))
            if unreal <= 0.0:
                logger.warning(f"🛑 REJECTED: {symbol} - Scaling requires positive unrealized PnL; current {unreal}")
                return False, "SCALING_NOT_ALLOWED_NO_WINNER"

        # If we have candle data compute volatility regime and log it
        try:
            if market_data and market_data.get('df') is not None:
                df = market_data.get('df')
                # basic duck-typing to avoid mandatory pandas import
                if hasattr(df, 'iloc') and hasattr(df, 'columns') and all(c in df.columns for c in ['high', 'low', 'close']):
                    tr = pd.concat([
                        df['high'] - df['low'],
                        (df['high'] - df['close'].shift()).abs(),
                        (df['low'] - df['close'].shift()).abs()
                    ], axis=1).max(axis=1)
                    avg_atr = float(tr.rolling(100).mean().iloc[-1]) if len(tr) >= 100 else float(tr.mean())
                    current_atr = float(tr.iloc[-1])
                    vol_ratio = current_atr / avg_atr if avg_atr and avg_atr > 0 else 1.0
                    regime = 'NORMAL'
                    if vol_ratio < 0.8:
                        regime = 'CALM'
                    elif vol_ratio > 1.5:
                        regime = 'CHAOS'
                    logger.info(f"🧭 MARKET REGIME: {regime} (ATR ratio {vol_ratio:.2f})")
        except Exception:
            pass
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
