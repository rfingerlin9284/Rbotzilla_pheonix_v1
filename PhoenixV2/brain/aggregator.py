"""
PhoenixV2 Brain Module - Strategy Aggregator

The central brain that coordinates HiveMind, WolfPack strategies,
and QuantHedge regime-based adjustments. Outputs a unified trade recommendation.
"""
import time
import os
from pathlib import Path
import logging
from typing import Dict, Any, Optional
from PhoenixV2.execution.router import BrokerRouter

from .hive_mind import HiveMindBridge
from .wolf_pack import WolfPack
from PhoenixV2.core.state_manager import StateManager
from PhoenixV2.config.charter import Charter
from .quant_hedge import QuantHedgeRules, RegimeDetector
# Import MarketRegime from the logic detector to normalize regimes across detectors
from logic.regime_detector import MarketRegime

logger = logging.getLogger("Brain")


class StrategyBrain:
    """
    The Unified Strategy Aggregator.
    
    Collects signals from:
    1. HiveMind (ML-based 3:1 filter)
    2. WolfPack (5-strategy voting)
    
    Applies:
    - QuantHedge regime-based size/stop adjustments
    
    Outputs a single, consolidated trade recommendation.
    """
    
    

    def __init__(self, router: Optional[BrokerRouter] = None):
        self.hive_mind = HiveMindBridge()
        # instantiate state manager for learning-driven strategy weights
        self.state_manager = StateManager(str(Path(__file__).resolve().parents[1] / 'core' / 'phoenix_state.json'))
        self.wolf_pack = WolfPack(state_manager=self.state_manager)
        self.quant_hedge = QuantHedgeRules()
        self.regime_detector = RegimeDetector()
        self.min_rr = 3.0
        self.default_notional = 50000  # Aggressive Mode: Aim high, let RiskGate cap at 2% risk
        self.router = router

    def get_signal(self, symbol: Optional[str] = None, market_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Returns a trade signal or None if no valid setup.
        
        Signal Format:
        {
            "symbol": "EUR_USD",
            "direction": "BUY" | "SELL",
            "timeframe": "H1",
            "notional_value": 16000,
            "sl": float,
            "tp": float,
            "confidence": 0.0-1.0,
            "source": "HiveMind" | "WolfPack" | "Consensus"
        }
        """
        # 1. Detect current regime first
        regime, volatility = self.regime_detector.detect()
        # Normalize regime to MarketRegime string (bull/bear/sideways/crash/triage)
        regime = self._normalize_regime(regime)
        # Map MarketRegime to quant hedge regime format expected by QuantHedgeRules
        quant_regime = 'TRIAGE'
        if regime == MarketRegime.BULL.value:
            quant_regime = 'BULL_STRONG'
        elif regime == MarketRegime.BEAR.value:
            quant_regime = 'BEAR_STRONG'
        elif regime == MarketRegime.SIDEWAYS.value:
            quant_regime = 'SIDEWAYS'
        elif regime == MarketRegime.CRASH.value:
            quant_regime = 'CRISIS'

        hedge_params = self.quant_hedge.get_hedge_params(quant_regime, volatility)
        
        # 2. Try HiveMind first (it has built-in 3:1 filter)
        hive_signal = self.hive_mind.fetch_inference()
        
        if hive_signal:
            # Convert HiveMind format to standard signal format
            signal = self._normalize_hive_signal(hive_signal)
            # Apply hedge adjustments
            signal = self.quant_hedge.adjust_signal(signal)
            return signal
        
        # 2. If HiveMind has no signal, optionally check WolfPack
        # WolfPack needs market data - for now we pass empty dict
        # If no market_data provided, try to fetch via router.get_candles if router and symbol available
        md = market_data or {}
        if not md and self.router and symbol:
            try:
                df = self.router.get_candles(symbol, timeframe='M15', limit=200)
                if df is not None:
                    md = {"price": float(df.iloc[-1]['close']), "timeframe": 'M15', "df": df}
                    # If it's a crypto instrument, fetch correlation asset candles (SPX) for correlation-based wolves
                    try:
                        # Only add correlation data for crypto instruments
                        if '-' in symbol or 'BTC' in symbol or 'ETH' in symbol:
                            corr_index = os.getenv('CORRELATION_INDEX', 'SPX500_USD')
                            # Get hourly candles for correlation analysis
                            spx_df = self.router.get_candles(corr_index, timeframe='H1', limit=200)
                            if spx_df is not None:
                                md['spx_df'] = spx_df
                                md['btc_df'] = df
                                # Calculate correlation (BTC vs SPX) and SPX trend for cross-market checks
                                try:
                                    import pandas as pd
                                    btc_returns = df['close'].pct_change().dropna().tail(50)
                                    spx_returns = spx_df['close'].pct_change().dropna().tail(50)
                                    if len(btc_returns) >= 5 and len(spx_returns) >= 5:
                                        # Align by array values to avoid strict timestamp join issues
                                        a = btc_returns.values[-min(len(btc_returns), len(spx_returns)):]
                                        b = spx_returns.values[-min(len(btc_returns), len(spx_returns)):]
                                        if len(a) >= 5 and len(b) >= 5:
                                            import numpy as np
                                            try:
                                                corr = float(pd.Series(a).corr(pd.Series(b)))
                                            except Exception:
                                                # Fallback to numpy correlation
                                                corr = float(np.corrcoef(a, b)[0, 1])
                                            md['spx_correlation'] = corr
                                            # Calculate SPX trend using a small EMA crossover
                                            spx_fast = spx_df['close'].ewm(span=20).mean().iloc[-1]
                                            spx_slow = spx_df['close'].ewm(span=50).mean().iloc[-1]
                                            md['spx_trend'] = 'BULL' if spx_fast > spx_slow else 'BEAR'
                                            logger.info(f"🧠 CROSS-MARKET: {symbol} vs SPX Corr: {corr:.2f} Trend: {md['spx_trend']}")
                                except Exception:
                                    pass
                    except Exception:
                        pass
            except Exception:
                md = {}

        if not Charter.USE_WOLF_PACK:
            logger.debug("⚙️ Charter: USE_WOLF_PACK disabled - HiveMind-only mode")
            return None

        wolf_consensus = self.wolf_pack.get_consensus(md or {})
        
        if wolf_consensus["direction"] != "HOLD":
            logger.info(f"🐺 WOLFPACK CONSENSUS: {wolf_consensus['direction']} ({wolf_consensus['confidence']:.0%})")
            # WolfPack can be used as a signal generator here - in the brain we do a deeper pass
            # Acceptance rule for WolfPack consensus:
            #   - For crypto: require confidence >= 0.85 (sniper mode)
            #   - For forex: require one of: confidence >= 0.25 OR at least 2 wolves voting OR top strategy sharpe >= 0.5
            # This restricts low-quality single-vote spam while allowing high-conviction WolfPack signals.
            try:
                votes_map = wolf_consensus.get('strategy_votes', {}) or {}
                vote_count_for_direction = sum(1 for v in votes_map.values() if v.get('vote') == wolf_consensus.get('direction'))
                top_strategy_name = wolf_consensus.get('top_strategy')
                top_sharpe = 0.0
                try:
                    if self.state_manager and top_strategy_name:
                        top_params = self.state_manager.get_strategy_params(top_strategy_name) or {}
                        top_sharpe = float(top_params.get('sharpe', 0.0) or 0.0)
                except Exception:
                    top_sharpe = 0.0
            except Exception:
                vote_count_for_direction = 0
                top_sharpe = 0.0
            # Enforce higher thresholds for Crypto (sniper mode for safety): require confidence >= 0.85
            if symbol and ('BTC' in symbol or 'ETH' in symbol or ('-' in symbol and symbol.split('-')[0] in ['BTC', 'ETH'])):
                if wolf_consensus.get('confidence', 0.0) < float(os.getenv('WOLF_CRYPTO_MIN_CONFIDENCE', Charter.WOLF_CRYPTO_MIN_CONFIDENCE)):
                    logger.info("🐺 WOLFPACK Crypto consensus below sniper threshold - ignoring")
                    return None
            # Cross-market veto: for crypto, if highly correlated with SPX and SPX trend opposes the direction, block the trade
            # e.g., SPX BEAR and consensus BUY for crypto -> veto
            try:
                if symbol and ('BTC' in symbol or 'ETH' in symbol or ('-' in symbol and symbol.split('-')[0] in ['BTC', 'ETH'])):
                    corr = md.get('spx_correlation', 0.0)
                    spx_trend = md.get('spx_trend')
                    if corr and corr >= float(os.getenv('CORRELATION_WOLF_VETO_THRESHOLD', '0.7')):
                        direction = wolf_consensus.get('direction')
                        if (direction == 'BUY' and spx_trend == 'BEAR') or (direction == 'SELL' and spx_trend == 'BULL'):
                            logger.info(f"🧠 CORRELATION VETO: Blocking {direction} on {symbol} - SPX trend: {spx_trend} corr: {corr:.2f}")
                            return None
            except Exception:
                pass

            # For non-crypto symbols: require a minimal consensus acceptance
            # Allow WolfPack only when: confidence >= Charter.WOLF_MIN_CONFIDENCE OR vote_count_for_direction >= Charter.WOLF_MIN_VOTES OR top_sharpe >= Charter.WOLF_MIN_TOP_SHARPE
            if not (symbol and ('BTC' in symbol or 'ETH' in symbol or ('-' in symbol and symbol.split('-')[0] in ['BTC', 'ETH']))):
                conf_ok = float(wolf_consensus.get('confidence', 0.0) or 0.0) >= float(os.getenv('WOLF_MIN_CONFIDENCE', Charter.WOLF_MIN_CONFIDENCE))
                votes_ok = int(vote_count_for_direction) >= int(os.getenv('WOLF_MIN_VOTES', str(Charter.WOLF_MIN_VOTES)))
                sharpe_ok = float(top_sharpe) >= float(os.getenv('WOLF_MIN_TOP_SHARPE', str(Charter.WOLF_MIN_TOP_SHARPE)))
                if not (conf_ok or votes_ok or sharpe_ok):
                    logger.info(f"🐺 WOLFPACK: Not enough consensus for {symbol}: conf={wolf_consensus.get('confidence',0):.3f}, votes={vote_count_for_direction}, top_sharpe={top_sharpe:.3f}")
                    return None

            # Return a minimal consensus signal; in real life, a deeper strategy would populate SL/TP
            strategy_name = wolf_consensus.get('top_strategy') or wolf_consensus.get('strategy') or wolf_consensus.get('top_strat')
            contributing = wolf_consensus.get('strategy_votes', {})
            return {
                "symbol": symbol or "UNSPECIFIED",
                "direction": wolf_consensus['direction'],
                "timeframe": (market_data or {}).get('timeframe', 'M15'),
                "notional_value": self.default_notional,
                "entry": (market_data or {}).get('price', 0),
                "sl": (market_data or {}).get('sl'),
                "tp": (market_data or {}).get('tp'),
                "confidence": wolf_consensus.get('confidence', 0.0),
                "strategy": strategy_name,
                "contributing_strategies": contributing,
                "source": "WolfPack"
            }
            pass
        
        return None

    def _normalize_hive_signal(self, hive_signal: Dict[str, Any]) -> Dict[str, Any]:
        """Convert HiveMind signal format to standard output format."""
        return {
            "symbol": hive_signal.get("pair"),
            "direction": hive_signal.get("direction"),
            "timeframe": hive_signal.get("timeframe", "M15"),
            "notional_value": self.default_notional,
            "entry": hive_signal.get("entry"),
            "sl": hive_signal.get("sl"),
            "tp": hive_signal.get("tp"),
            "confidence": hive_signal.get("confidence", 0.75),
            "source": "HiveMind",
            "ml_note": hive_signal.get("ml_note", "")
        }

    def _normalize_regime(self, reg) -> str:
        """Normalize various regime outputs to known MarketRegime values.

        Accepts strings or enum values from detectors and returns MarketRegime.value string.
        """
        # If it's an enum, just return its value
        try:
            if hasattr(reg, 'value'):
                return reg.value
        except Exception:
            pass

        if not isinstance(reg, str):
            return MarketRegime.TRIAGE.value

        r = reg.lower()
        if 'bull' in r:
            return MarketRegime.BULL.value
        if 'bear' in r:
            return MarketRegime.BEAR.value
        if 'crash' in r or 'crisis' in r:
            return MarketRegime.CRASH.value
        if 'side' in r or 'sideways' in r:
            return MarketRegime.SIDEWAYS.value
        return MarketRegime.TRIAGE.value

    def _validate_rr(self, signal: Dict[str, Any]) -> bool:
        """Validate Risk/Reward ratio."""
        entry = signal.get('entry', 0)
        sl = signal.get('sl', 0)
        tp = signal.get('tp', 0)
        
        if entry == 0 or abs(entry - sl) == 0:
            return False
            
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        rr = reward / risk
        
        if rr < self.min_rr:
            logger.debug(f"RR FAIL: {signal.get('symbol')} RR={rr:.2f}")
            return False
        
        return True
