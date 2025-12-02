#!/usr/bin/env python3
"""
RICK System - Strategy Aggregator
=================================
Aggregates trading signals from multiple strategy sources.
Enforces timeframe filtering (M15 minimum) and noise rejection.

AUTH CODE: 841921
CHARTER: Noise trading (M1/M5) REJECTED by default.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RICK.StrategyAggregator")


class Timeframe(Enum):
    """Trading timeframes with numeric minutes for comparison."""
    M1 = 1
    M5 = 5
    M15 = 15
    M30 = 30
    H1 = 60
    H4 = 240
    D1 = 1440
    W1 = 10080
    
    @classmethod
    def from_string(cls, tf_str: str) -> 'Timeframe':
        """Convert string like 'M15', '15m', '15' to Timeframe enum."""
        tf_str = tf_str.upper().strip()
        # Handle various formats
        mappings = {
            'M1': cls.M1, '1M': cls.M1, '1': cls.M1,
            'M5': cls.M5, '5M': cls.M5, '5': cls.M5,
            'M15': cls.M15, '15M': cls.M15, '15': cls.M15,
            'M30': cls.M30, '30M': cls.M30, '30': cls.M30,
            'H1': cls.H1, '1H': cls.H1, '60': cls.H1, '60M': cls.H1,
            'H4': cls.H4, '4H': cls.H4, '240': cls.H4,
            'D1': cls.D1, '1D': cls.D1, 'DAILY': cls.D1,
            'W1': cls.W1, '1W': cls.W1, 'WEEKLY': cls.W1,
        }
        return mappings.get(tf_str, cls.M15)  # Default to M15 if unknown


class SignalType(Enum):
    """Signal direction."""
    BUY = "BUY"
    SELL = "SELL"
    CLOSE = "CLOSE"
    HOLD = "HOLD"


@dataclass
class TradingSignal:
    """Represents a trading signal from any strategy."""
    symbol: str
    signal_type: SignalType
    timeframe: Timeframe
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float = 0.5
    strategy_name: str = "unknown"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def risk_reward_ratio(self) -> float:
        """Calculate R:R ratio."""
        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.take_profit - self.entry_price)
        return reward / risk if risk > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "symbol": self.symbol,
            "signal_type": self.signal_type.value,
            "timeframe": self.timeframe.name,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "confidence": self.confidence,
            "strategy_name": self.strategy_name,
            "timestamp": self.timestamp.isoformat(),
            "risk_reward_ratio": self.risk_reward_ratio,
            "metadata": self.metadata
        }


@dataclass
class AggregationResult:
    """Result of signal aggregation with rejection reasons."""
    accepted: List[TradingSignal] = field(default_factory=list)
    rejected_noise: List[TradingSignal] = field(default_factory=list)
    rejected_rr: List[TradingSignal] = field(default_factory=list)
    rejected_confidence: List[TradingSignal] = field(default_factory=list)
    rejected_other: List[TradingSignal] = field(default_factory=list)
    
    @property
    def total_processed(self) -> int:
        return len(self.accepted) + self.total_rejected
    
    @property
    def total_rejected(self) -> int:
        return (len(self.rejected_noise) + len(self.rejected_rr) + 
                len(self.rejected_confidence) + len(self.rejected_other))
    
    def summary(self) -> Dict[str, int]:
        return {
            "total_processed": self.total_processed,
            "accepted": len(self.accepted),
            "rejected_noise_trading": len(self.rejected_noise),
            "rejected_risk_reward": len(self.rejected_rr),
            "rejected_low_confidence": len(self.rejected_confidence),
            "rejected_other": len(self.rejected_other)
        }


class StrategyAggregator:
    """
    Central aggregator for trading signals from multiple strategies.
    
    ENFORCES:
    - M15 minimum timeframe (rejects M1/M5 noise trading)
    - Risk/Reward ratio minimum (default 3.0)
    - Confidence threshold (default 0.6)
    """
    
    # CHARTER CONSTANTS - Immutable
    MINIMUM_TIMEFRAME = Timeframe.M15
    MIN_RISK_REWARD_RATIO = 3.0
    MIN_CONFIDENCE = 0.6
    AUTH_PIN = 841921
    
    def __init__(self):
        """Initialize the strategy aggregator."""
        self.signals_queue: List[TradingSignal] = []
        self.last_aggregation: Optional[AggregationResult] = None
        self.allow_noise_trading = self._load_noise_trading_override()
        self.strategy_sources: Dict[str, Any] = {}
        
        # Load config from environment
        self.min_rr = float(os.getenv("MIN_RR", self.MIN_RISK_REWARD_RATIO))
        self.min_confidence = float(os.getenv("MIN_SIGNAL_CONFIDENCE", self.MIN_CONFIDENCE))
        
        logger.info(f"🔧 StrategyAggregator initialized")
        logger.info(f"   - Minimum Timeframe: {self.MINIMUM_TIMEFRAME.name}")
        logger.info(f"   - Noise Trading Override: {self.allow_noise_trading}")
        logger.info(f"   - Min R:R Ratio: {self.min_rr}")
        logger.info(f"   - Min Confidence: {self.min_confidence}")
    
    def _load_noise_trading_override(self) -> bool:
        """Check if noise trading is explicitly allowed via env."""
        override = os.getenv("ALLOW_NOISE_TRADING", "false").lower()
        return override in ("true", "1", "yes")
    
    def register_strategy(self, name: str, strategy_module: Any) -> None:
        """Register an external strategy module as a signal source."""
        self.strategy_sources[name] = strategy_module
        logger.info(f"📊 Registered strategy source: {name}")
    
    def ingest_signal(self, signal: TradingSignal) -> bool:
        """
        Ingest a single signal into the queue.
        Returns True if signal passes initial validation.
        """
        # Basic validation
        if not signal.symbol or signal.entry_price <= 0:
            logger.warning(f"⚠️ Invalid signal rejected: {signal.symbol}")
            return False
        
        self.signals_queue.append(signal)
        logger.debug(f"📥 Signal ingested: {signal.symbol} {signal.signal_type.value} @ {signal.entry_price}")
        return True
    
    def ingest_from_dict(self, data: Dict[str, Any]) -> bool:
        """Ingest signal from dictionary (e.g., from JSON file or API)."""
        try:
            signal = TradingSignal(
                symbol=data.get("symbol", ""),
                signal_type=SignalType(data.get("signal_type", "HOLD")),
                timeframe=Timeframe.from_string(data.get("timeframe", "M15")),
                entry_price=float(data.get("entry_price", 0)),
                stop_loss=float(data.get("stop_loss", 0)),
                take_profit=float(data.get("take_profit", 0)),
                confidence=float(data.get("confidence", 0.5)),
                strategy_name=data.get("strategy_name", "external"),
                metadata=data.get("metadata", {})
            )
            return self.ingest_signal(signal)
        except Exception as e:
            logger.error(f"❌ Failed to parse signal dict: {e}")
            return False
    
    def ingest_from_file(self, filepath: str) -> int:
        """Load signals from a JSON file. Returns count of signals ingested."""
        path = Path(filepath)
        if not path.exists():
            logger.error(f"❌ Signal file not found: {filepath}")
            return 0
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            signals = data if isinstance(data, list) else [data]
            ingested = sum(1 for s in signals if self.ingest_from_dict(s))
            logger.info(f"📂 Loaded {ingested}/{len(signals)} signals from {filepath}")
            return ingested
        except Exception as e:
            logger.error(f"❌ Failed to load signals from {filepath}: {e}")
            return 0
    
    def _validate_timeframe(self, signal: TradingSignal) -> bool:
        """
        CRITICAL: Enforce M15 minimum timeframe.
        M1/M5 signals are NOISE TRADING and must be rejected.
        """
        if self.allow_noise_trading:
            logger.debug(f"⚠️ Noise trading override active - allowing {signal.timeframe.name}")
            return True
        
        if signal.timeframe.value < self.MINIMUM_TIMEFRAME.value:
            logger.warning(
                f"🚫 NOISE TRADING REJECTED: {signal.symbol} on {signal.timeframe.name} "
                f"(minimum: {self.MINIMUM_TIMEFRAME.name})"
            )
            return False
        return True
    
    def _validate_risk_reward(self, signal: TradingSignal) -> bool:
        """Validate minimum risk/reward ratio."""
        rr = signal.risk_reward_ratio
        if rr < self.min_rr:
            logger.warning(
                f"🚫 R:R REJECTED: {signal.symbol} has R:R {rr:.2f} (minimum: {self.min_rr})"
            )
            return False
        return True
    
    def _validate_confidence(self, signal: TradingSignal) -> bool:
        """Validate minimum confidence threshold."""
        if signal.confidence < self.min_confidence:
            logger.warning(
                f"🚫 LOW CONFIDENCE REJECTED: {signal.symbol} confidence {signal.confidence:.2f} "
                f"(minimum: {self.min_confidence})"
            )
            return False
        return True
    
    def aggregate(self) -> AggregationResult:
        """
        Process all queued signals through validation filters.
        Returns AggregationResult with categorized signals.
        """
        result = AggregationResult()
        
        logger.info(f"🔄 Aggregating {len(self.signals_queue)} signals...")
        
        for signal in self.signals_queue:
            # Filter 1: Timeframe (Noise Trading Gate)
            if not self._validate_timeframe(signal):
                result.rejected_noise.append(signal)
                continue
            
            # Filter 2: Risk/Reward Ratio
            if not self._validate_risk_reward(signal):
                result.rejected_rr.append(signal)
                continue
            
            # Filter 3: Confidence
            if not self._validate_confidence(signal):
                result.rejected_confidence.append(signal)
                continue
            
            # All filters passed
            result.accepted.append(signal)
            logger.info(
                f"✅ ACCEPTED: {signal.symbol} {signal.signal_type.value} "
                f"@ {signal.entry_price} (R:R={signal.risk_reward_ratio:.2f}, "
                f"TF={signal.timeframe.name}, conf={signal.confidence:.2f})"
            )
        
        # Clear queue after processing
        self.signals_queue.clear()
        self.last_aggregation = result
        
        # Log summary
        summary = result.summary()
        logger.info(f"📊 Aggregation Complete: {summary}")
        
        return result
    
    def get_actionable_signals(self) -> List[TradingSignal]:
        """Get only BUY/SELL signals that passed all filters."""
        if not self.last_aggregation:
            return []
        return [
            s for s in self.last_aggregation.accepted 
            if s.signal_type in (SignalType.BUY, SignalType.SELL)
        ]
    
    def export_results(self, filepath: str) -> bool:
        """Export last aggregation results to JSON file."""
        if not self.last_aggregation:
            logger.warning("⚠️ No aggregation results to export")
            return False
        
        try:
            output = {
                "timestamp": datetime.utcnow().isoformat(),
                "summary": self.last_aggregation.summary(),
                "accepted": [s.to_dict() for s in self.last_aggregation.accepted],
                "rejected_noise_trading": [s.to_dict() for s in self.last_aggregation.rejected_noise],
                "rejected_risk_reward": [s.to_dict() for s in self.last_aggregation.rejected_rr],
                "rejected_low_confidence": [s.to_dict() for s in self.last_aggregation.rejected_confidence]
            }
            
            with open(filepath, 'w') as f:
                json.dump(output, f, indent=2)
            
            logger.info(f"💾 Results exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            return False


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
_aggregator_instance: Optional[StrategyAggregator] = None

def get_aggregator() -> StrategyAggregator:
    """Get or create the singleton StrategyAggregator instance."""
    global _aggregator_instance
    if _aggregator_instance is None:
        _aggregator_instance = StrategyAggregator()
    return _aggregator_instance


# ============================================================================
# MODULE TEST
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("RICK Strategy Aggregator - Self Test")
    print("=" * 60)
    
    agg = get_aggregator()
    
    # Create test signals
    test_signals = [
        # Should be REJECTED - M5 noise trading
        TradingSignal(
            symbol="EUR_USD", signal_type=SignalType.BUY,
            timeframe=Timeframe.M5, entry_price=1.0850,
            stop_loss=1.0820, take_profit=1.0950,
            confidence=0.8, strategy_name="noise_test"
        ),
        # Should be REJECTED - M1 noise trading
        TradingSignal(
            symbol="GBP_USD", signal_type=SignalType.SELL,
            timeframe=Timeframe.M1, entry_price=1.2650,
            stop_loss=1.2680, take_profit=1.2550,
            confidence=0.9, strategy_name="scalper"
        ),
        # Should be REJECTED - Poor R:R (less than 3:1)
        TradingSignal(
            symbol="USD_JPY", signal_type=SignalType.BUY,
            timeframe=Timeframe.H1, entry_price=149.50,
            stop_loss=149.00, take_profit=150.00,  # 1:1 R:R
            confidence=0.7, strategy_name="bad_rr"
        ),
        # Should be REJECTED - Low confidence
        TradingSignal(
            symbol="AUD_USD", signal_type=SignalType.BUY,
            timeframe=Timeframe.H4, entry_price=0.6500,
            stop_loss=0.6450, take_profit=0.6700,  # 4:1 R:R
            confidence=0.3, strategy_name="low_conf"
        ),
        # Should be ACCEPTED - All criteria met
        TradingSignal(
            symbol="EUR_USD", signal_type=SignalType.BUY,
            timeframe=Timeframe.H1, entry_price=1.0850,
            stop_loss=1.0800, take_profit=1.1050,  # 4:1 R:R
            confidence=0.75, strategy_name="good_signal"
        ),
        # Should be ACCEPTED - M15 minimum timeframe
        TradingSignal(
            symbol="GBP_JPY", signal_type=SignalType.SELL,
            timeframe=Timeframe.M15, entry_price=188.50,
            stop_loss=189.00, take_profit=186.50,  # 4:1 R:R
            confidence=0.65, strategy_name="m15_signal"
        ),
    ]
    
    # Ingest all signals
    for signal in test_signals:
        agg.ingest_signal(signal)
    
    # Aggregate and filter
    result = agg.aggregate()
    
    print("\n" + "=" * 60)
    print("AGGREGATION RESULTS")
    print("=" * 60)
    print(f"Total Processed: {result.total_processed}")
    print(f"Accepted: {len(result.accepted)}")
    print(f"Rejected (Noise Trading): {len(result.rejected_noise)}")
    print(f"Rejected (Risk/Reward): {len(result.rejected_rr)}")
    print(f"Rejected (Low Confidence): {len(result.rejected_confidence)}")
    
    print("\n✅ ACCEPTED SIGNALS:")
    for s in result.accepted:
        print(f"   - {s.symbol} {s.signal_type.value} @ {s.entry_price} (TF={s.timeframe.name})")
    
    print("\n🚫 NOISE TRADING REJECTED:")
    for s in result.rejected_noise:
        print(f"   - {s.symbol} on {s.timeframe.name}")
    
    print("\n" + "=" * 60)
    print("Self-test complete.")
