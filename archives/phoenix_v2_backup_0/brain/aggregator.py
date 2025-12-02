"""
PhoenixV2 Brain Module - Strategy Aggregator

The central brain that coordinates HiveMind, WolfPack strategies,
and QuantHedge regime-based adjustments. Outputs a unified trade recommendation.
"""
import time
import logging
from typing import Dict, Any, Optional

from .hive_mind import HiveMindBridge
from .wolf_pack import WolfPack
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
    
    def __init__(self):
        self.hive_mind = HiveMindBridge()
        self.wolf_pack = WolfPack()
        self.quant_hedge = QuantHedgeRules()
        self.regime_detector = RegimeDetector()
        self.min_rr = 3.0
        self.default_notional = 16000  # Passes $15k institutional floor

    def get_signal(self) -> Optional[Dict[str, Any]]:
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
        
        # 2. If HiveMind has no signal, check WolfPack
        # WolfPack needs market data - for now we pass empty dict
        wolf_consensus = self.wolf_pack.get_consensus({})
        
        if wolf_consensus["direction"] != "HOLD":
            logger.info(f"🐺 WOLFPACK CONSENSUS: {wolf_consensus['direction']} ({wolf_consensus['confidence']:.0%})")
            # WolfPack doesn't provide entry/sl/tp, so we can't trade on it alone
            # In a real system, this would trigger a deeper analysis
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
