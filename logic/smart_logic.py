#!/usr/bin/env python3
"""
Smart Logic Filters - RBOTzilla UNI Phase 6
Signal validation with RR, FVG, Fibonacci confluence scoring.
PIN: 841921 | Generated: 2025-09-26
"""
#!/usr/bin/env python3
"""
Smart Logic Filters - RBOTzilla UNI Phase 6
Signal validation with RR, FVG, Fibonacci confluence scoring.
PIN: 841921 | Generated: 2025-09-26
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone
import json

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone
import json

# Simplified charter constants for testing
class RickCharter:
    MIN_RISK_REWARD_RATIO = 3.0
    PIN = 841921
    
    @classmethod
    def validate_pin(cls, pin):
        return pin == cls.PIN
    
    @classmethod
    def validate_risk_reward(cls, ratio):
        return ratio >= cls.MIN_RISK_REWARD_RATIO

# Simplified event tracking
class EventType:
    PHASE_START = "phase_start"
    PHASE_COMPLETE = "phase_complete"
    SYSTEM_ERROR = "system_error"

class SimpleTracker:
    def log_event(self, event_type, component, message, details=None):
        print(f"[{component}] {message}")

def get_tracker():
    return SimpleTracker()

class FilterResult(Enum):
    """Filter validation results"""
    PASS = "pass"
    FAIL = "fail"
    WEAK = "weak"
    STRONG = "strong"

class SignalStrength(Enum):
    """Signal strength classifications"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    WEAK_BUY = "weak_buy"
    NEUTRAL = "neutral"
    WEAK_SELL = "weak_sell"
    SELL = "sell"
    STRONG_SELL = "strong_sell"

@dataclass
class FilterScore:
    """Individual filter scoring result"""
    filter_name: str
    passed: bool
    score: float          # 0.0 to 1.0
    weight: float         # Filter importance weight
    reason: str
    details: Optional[Dict[str, Any]] = None

@dataclass
class SignalValidation:
    """Complete signal validation result"""
    passed: bool
    score: float          # Weighted average score
    reject_reason: Optional[str]
    filter_scores: List[FilterScore]
    risk_reward_ratio: float
    confluence_count: int
    validation_timestamp: str
    charter_compliant: bool

class SmartLogicFilter:
    """
    Advanced signal validation system with confluence scoring
    Enforces RICK Charter compliance with weighted filter system
    """
    
    def __init__(self, pin: int = None):
        """Initialize smart logic filter system"""
        if pin and not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid PIN for SmartLogicFilter access")
        
        self.pin_verified = pin == RickCharter.PIN if pin else False
        self.logger = logging.getLogger(__name__)
        self.tracker = get_tracker()
        
        # Filter weights (sum should equal 1.0)
        self.filter_weights = {
            "risk_reward": 0.30,      # Hard requirement, high weight
            "fvg_confluence": 0.25,   # Fair Value Gap alignment
            "fibonacci": 0.20,        # Fibonacci retracement/extension
            "volume_profile": 0.15,   # Volume-based validation
            "momentum": 0.10          # Momentum confirmation
        }
        
        # Minimum scores for passage
        self.min_total_score = 0.65    # 65% minimum confluence
        self.min_confluence_count = 2   # At least 2 filters must pass
        
        # Fibonacci levels for confluence
        self.fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.618, 2.618]
        
        self.logger.info("SmartLogicFilter initialized with charter enforcement")
    
    def _validate_risk_reward(self, signal_dict: Dict[str, Any]) -> FilterScore:
        """
        Hard RR validation - MUST pass Charter minimum
        This is a hard fail if not met
        """
        entry_price = signal_dict.get("entry_price", 0)
        target_price = signal_dict.get("target_price", 0) 
        stop_loss = signal_dict.get("stop_loss", 0)
        direction = signal_dict.get("direction", "buy").lower()
        
        if not all([entry_price, target_price, stop_loss]):
            return FilterScore(
                filter_name="risk_reward",
                passed=False,
                score=0.0,
                weight=self.filter_weights["risk_reward"],
                reason="Missing price levels for RR calculation",
                details={"entry": entry_price, "target": target_price, "stop": stop_loss}
            )
        
        # Calculate risk and reward
        if direction in ["buy", "long"]:
            risk = abs(entry_price - stop_loss)
            reward = abs(target_price - entry_price)
        else:  # sell/short
            risk = abs(stop_loss - entry_price)
            reward = abs(entry_price - target_price)
        
        if risk <= 0:
            return FilterScore(
                filter_name="risk_reward",
                passed=False,
                score=0.0,
                weight=self.filter_weights["risk_reward"],
                reason="Invalid risk calculation (risk <= 0)",
                details={"risk": risk, "reward": reward}
            )
        
        rr_ratio = reward / risk
        
        # Charter compliance check
        charter_compliant = RickCharter.validate_risk_reward(rr_ratio)
        
        if not charter_compliant:
            return FilterScore(
                filter_name="risk_reward",
                passed=False,
                score=0.0,
                weight=self.filter_weights["risk_reward"],
                reason=f"RR {rr_ratio:.2f} below charter minimum {RickCharter.MIN_RISK_REWARD_RATIO}",
                details={"calculated_rr": rr_ratio, "charter_min": RickCharter.MIN_RISK_REWARD_RATIO}
            )
        
        # Score based on how much above minimum
        excess_ratio = (rr_ratio - RickCharter.MIN_RISK_REWARD_RATIO) / RickCharter.MIN_RISK_REWARD_RATIO
        score = min(1.0, 0.7 + (excess_ratio * 0.3))  # 70% base + 30% bonus
        
        return FilterScore(
            filter_name="risk_reward",
            passed=True,
            score=score,
            weight=self.filter_weights["risk_reward"],
            reason=f"RR {rr_ratio:.2f} meets charter requirement",
            details={"calculated_rr": rr_ratio, "excess_ratio": excess_ratio}
        )
    
    def _validate_fvg_confluence(self, signal_dict: Dict[str, Any]) -> FilterScore:
        """
        Fair Value Gap confluence validation
        Simulates FVG detection and alignment with signal direction
        """
        entry_price = signal_dict.get("entry_price", 0)
        direction = signal_dict.get("direction", "buy").lower()
        high_prices = signal_dict.get("recent_highs", [])
        low_prices = signal_dict.get("recent_lows", [])
        close_prices = signal_dict.get("recent_closes", [])
        
        if not entry_price or len(high_prices) < 3:
            return FilterScore(
                filter_name="fvg_confluence",
                passed=False,
                score=0.3,  # Neutral score for insufficient data
                weight=self.filter_weights["fvg_confluence"],
                reason="Insufficient price data for FVG analysis",
                details={"data_points": len(high_prices)}
            )
        
        # Simulate FVG detection (simplified)
        # In reality, this would analyze 3-candle patterns for gaps
        fvg_zones = []
        
        # Look for potential FVG zones in recent price action
        for i in range(len(high_prices) - 2):
            candle1_high = high_prices[i]
            candle1_low = low_prices[i]
            candle2_high = high_prices[i + 1]  
            candle2_low = low_prices[i + 1]
            candle3_high = high_prices[i + 2]
            candle3_low = low_prices[i + 2]
            
            # Bullish FVG: candle1_low > candle3_high (gap up)
            if candle1_low > candle3_high:
                fvg_zones.append({
                    "type": "bullish",
                    "upper": candle1_low,
                    "lower": candle3_high,
                    "strength": (candle1_low - candle3_high) / entry_price
                })
            
            # Bearish FVG: candle1_high < candle3_low (gap down)
            if candle1_high < candle3_low:
                fvg_zones.append({
                    "type": "bearish", 
                    "upper": candle3_low,
                    "lower": candle1_high,
                    "strength": (candle3_low - candle1_high) / entry_price
                })
        
        if not fvg_zones:
            return FilterScore(
                filter_name="fvg_confluence",
                passed=False,
                score=0.4,
                weight=self.filter_weights["fvg_confluence"],
                reason="No FVG zones detected in recent price action",
                details={"zones_found": 0}
            )
        
        # Check alignment with signal direction
        aligned_zones = []
        for zone in fvg_zones:
            zone_contains_entry = zone["lower"] <= entry_price <= zone["upper"]
            direction_aligned = (
                (direction in ["buy", "long"] and zone["type"] == "bullish") or
                (direction in ["sell", "short"] and zone["type"] == "bearish")
            )
            
            if zone_contains_entry and direction_aligned:
                aligned_zones.append(zone)
        
        if not aligned_zones:
            return FilterScore(
                filter_name="fvg_confluence",
                passed=False,
                score=0.2,
                weight=self.filter_weights["fvg_confluence"],
                reason="No FVG zones align with signal direction and entry",
                details={"total_zones": len(fvg_zones), "aligned_zones": 0}
            )
        
        # Score based on strongest aligned zone
        strongest_zone = max(aligned_zones, key=lambda z: z["strength"])
        strength_score = min(1.0, strongest_zone["strength"] * 100)  # Convert to 0-1 scale
        
        return FilterScore(
            filter_name="fvg_confluence",
            passed=True,
            score=max(0.6, strength_score),  # Minimum 60% for passing
            weight=self.filter_weights["fvg_confluence"],
            reason=f"FVG confluence detected with {strongest_zone['type']} zone",
            details={"aligned_zones": len(aligned_zones), "strongest_strength": strongest_zone["strength"]}
        )
    
    def _validate_fibonacci_confluence(self, signal_dict: Dict[str, Any]) -> FilterScore:
        """
        Fibonacci retracement/extension confluence validation
        Checks if entry aligns with key Fibonacci levels
        """
        entry_price = signal_dict.get("entry_price", 0)
        swing_high = signal_dict.get("swing_high", 0)
        swing_low = signal_dict.get("swing_low", 0)
        direction = signal_dict.get("direction", "buy").lower()
        
        if not all([entry_price, swing_high, swing_low]) or swing_high <= swing_low:
            return FilterScore(
                filter_name="fibonacci",
                passed=False,
                score=0.3,
                weight=self.filter_weights["fibonacci"],
                reason="Missing or invalid swing high/low for Fibonacci analysis",
                details={"swing_high": swing_high, "swing_low": swing_low}
            )
        
        # Calculate Fibonacci levels
        swing_range = swing_high - swing_low
        fib_levels_prices = {}
        
        # Retracement levels (from swing high)
        for level in self.fib_levels:
            if level <= 1.0:  # Retracement
                fib_price = swing_high - (swing_range * level)
                fib_levels_prices[f"ret_{level}"] = fib_price
            else:  # Extension
                fib_price = swing_high + (swing_range * (level - 1.0))
                fib_levels_prices[f"ext_{level}"] = fib_price
        
        # Find closest Fibonacci level to entry price
        closest_level = None
        min_distance = float('inf')
        
        for level_name, fib_price in fib_levels_prices.items():
            distance = abs(entry_price - fib_price)
            relative_distance = distance / entry_price  # Relative to entry price
            
            if relative_distance < min_distance:
                min_distance = relative_distance
                closest_level = (level_name, fib_price)
        
        # Tolerance for Fibonacci confluence (within 0.5% of price)
        tolerance = 0.005
        
        if min_distance > tolerance:
            return FilterScore(
                filter_name="fibonacci",
                passed=False,
                score=0.3,
                weight=self.filter_weights["fibonacci"],
                reason=f"Entry not close to Fibonacci level (closest: {min_distance:.1%} away)",
                details={"closest_level": closest_level[0] if closest_level else None, "distance": min_distance}
            )
        
        # Score based on how close to the Fibonacci level
        proximity_score = 1.0 - (min_distance / tolerance)
        
        # Bonus for key levels (0.618, 0.5, 1.618)
        level_value = float(closest_level[0].split('_')[1])
        key_levels = [0.5, 0.618, 1.618]
        is_key_level = any(abs(level_value - key) < 0.01 for key in key_levels)
        
        final_score = proximity_score
        if is_key_level:
            final_score = min(1.0, final_score + 0.2)  # 20% bonus for key levels
        
        return FilterScore(
            filter_name="fibonacci",
            passed=True,
            score=max(0.6, final_score),
            weight=self.filter_weights["fibonacci"],
            reason=f"Entry aligns with Fibonacci {closest_level[0]} level",
            details={"level": closest_level[0], "fib_price": closest_level[1], "distance": min_distance, "is_key_level": is_key_level}
        )
    
    def _validate_volume_profile(self, signal_dict: Dict[str, Any]) -> FilterScore:
        """
        Volume profile and behavior-based signal validation
        Simulates volume analysis for signal strength
        """
        entry_price = signal_dict.get("entry_price", 0)
        volumes = signal_dict.get("recent_volumes", [])
        prices = signal_dict.get("recent_closes", [])
        direction = signal_dict.get("direction", "buy").lower()
        
        if len(volumes) < 10 or len(prices) < 10:
            return FilterScore(
                filter_name="volume_profile",
                passed=False,
                score=0.4,
                weight=self.filter_weights["volume_profile"],
                reason="Insufficient volume data for analysis",
                details={"volume_points": len(volumes), "price_points": len(prices)}
            )
        
        # Calculate volume metrics
        avg_volume = np.mean(volumes)
        recent_volume = volumes[-1] if volumes else 0
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0
        
        # Volume trend analysis (last 5 vs previous 5)
        if len(volumes) >= 10:
            recent_vol_avg = np.mean(volumes[-5:])
            previous_vol_avg = np.mean(volumes[-10:-5])
            volume_trend = (recent_vol_avg - previous_vol_avg) / previous_vol_avg if previous_vol_avg > 0 else 0
        else:
            volume_trend = 0
        
        # Price-volume relationship
        price_changes = np.diff(prices) if len(prices) > 1 else [0]
        volume_changes = np.diff(volumes) if len(volumes) > 1 else [0]
        
        # Positive correlation between price and volume movement
        if len(price_changes) > 0 and len(volume_changes) > 0:
            try:
                correlation = np.corrcoef(price_changes[-10:], volume_changes[-10:])[0, 1]
                if np.isnan(correlation):
                    correlation = 0
            except:
                correlation = 0
        else:
            correlation = 0
        
        # Scoring based on volume confirmation
        score_components = []
        
        # Volume surge (above average)
        if volume_ratio > 1.5:  # 50% above average
            score_components.append(("volume_surge", 0.3, f"Volume {volume_ratio:.1f}x average"))
        elif volume_ratio > 1.2:  # 20% above average  
            score_components.append(("volume_above_avg", 0.2, f"Volume {volume_ratio:.1f}x average"))
        else:
            score_components.append(("volume_low", -0.1, f"Volume only {volume_ratio:.1f}x average"))
        
        # Volume trend alignment
        expected_trend = 1 if direction in ["buy", "long"] else -1
        if (volume_trend > 0 and expected_trend > 0) or (volume_trend < 0 and expected_trend < 0):
            score_components.append(("trend_aligned", 0.2, f"Volume trend aligned ({volume_trend:.1%})"))
        else:
            score_components.append(("trend_misaligned", -0.1, f"Volume trend misaligned ({volume_trend:.1%})"))
        
        # Price-volume correlation
        if abs(correlation) > 0.3:  # Decent correlation
            score_components.append(("correlation", 0.2, f"Price-volume correlation {correlation:.2f}"))
        else:
            score_components.append(("weak_correlation", 0.0, f"Weak correlation {correlation:.2f}"))
        
        # Calculate final score
        base_score = 0.5
        for component, adjustment, reason in score_components:
            base_score += adjustment
        
        final_score = max(0.0, min(1.0, base_score))
        passed = final_score >= 0.5
        
        reasons = [comp[2] for comp in score_components]
        
        return FilterScore(
            filter_name="volume_profile",
            passed=passed,
            score=final_score,
            weight=self.filter_weights["volume_profile"],
            reason="; ".join(reasons),
            details={
                "volume_ratio": volume_ratio,
                "volume_trend": volume_trend,
                "price_volume_correlation": correlation,
                "score_components": [{"name": c[0], "adjustment": c[1]} for c in score_components]
            }
        )
    
    def _validate_momentum(self, signal_dict: Dict[str, Any]) -> FilterScore:
        """
        Momentum confirmation using simple technical indicators
        RSI, MACD-like momentum analysis
        """
        prices = signal_dict.get("recent_closes", [])
        direction = signal_dict.get("direction", "buy").lower()
        
        if len(prices) < 14:
            return FilterScore(
                filter_name="momentum",
                passed=False,
                score=0.4,
                weight=self.filter_weights["momentum"],
                reason="Insufficient price data for momentum analysis",
                details={"price_points": len(prices)}
            )
        
        # Simple RSI calculation (14-period)
        def calculate_rsi(prices_array, period=14):
            deltas = np.diff(prices_array)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        # Simple momentum (rate of change)
        def calculate_momentum(prices_array, period=10):
            if len(prices_array) < period:
                return 0
            current = prices_array[-1]
            previous = prices_array[-period]
            return (current - previous) / previous if previous != 0 else 0
        
        rsi = calculate_rsi(np.array(prices))
        momentum = calculate_momentum(np.array(prices))
        
        # Momentum scoring
        score_components = []
        
        # RSI analysis
        if direction in ["buy", "long"]:
            if rsi < 30:
                score_components.append(("rsi_oversold", 0.3, f"RSI oversold {rsi:.1f}"))
            elif rsi > 50:
                score_components.append(("rsi_bullish", 0.2, f"RSI bullish {rsi:.1f}"))
            elif rsi > 70:
                score_components.append(("rsi_overbought", -0.2, f"RSI overbought {rsi:.1f}"))
            else:
                score_components.append(("rsi_neutral", 0.1, f"RSI neutral {rsi:.1f}"))
        else:  # sell/short
            if rsi > 70:
                score_components.append(("rsi_overbought", 0.3, f"RSI overbought {rsi:.1f}"))
            elif rsi < 50:
                score_components.append(("rsi_bearish", 0.2, f"RSI bearish {rsi:.1f}"))
            elif rsi < 30:
                score_components.append(("rsi_oversold", -0.2, f"RSI oversold {rsi:.1f}"))
            else:
                score_components.append(("rsi_neutral", 0.1, f"RSI neutral {rsi:.1f}"))
        
        # Momentum direction alignment
        expected_momentum = 1 if direction in ["buy", "long"] else -1
        if (momentum > 0.01 and expected_momentum > 0) or (momentum < -0.01 and expected_momentum < 0):
            score_components.append(("momentum_aligned", 0.3, f"Momentum aligned {momentum:.1%}"))
        elif abs(momentum) < 0.01:
            score_components.append(("momentum_flat", 0.0, f"Momentum flat {momentum:.1%}"))
        else:
            score_components.append(("momentum_contrary", -0.2, f"Momentum contrary {momentum:.1%}"))
        
        # Calculate final score
        base_score = 0.4
        for component, adjustment, reason in score_components:
            base_score += adjustment
        
        final_score = max(0.0, min(1.0, base_score))
        passed = final_score >= 0.5
        
        reasons = [comp[2] for comp in score_components]
        
        return FilterScore(
            filter_name="momentum",
            passed=passed,
            score=final_score,
            weight=self.filter_weights["momentum"],
            reason="; ".join(reasons),
            details={
                "rsi": rsi,
                "momentum": momentum,
                "score_components": [{"name": c[0], "adjustment": c[1]} for c in score_components]
            }
        )
    
    def validate_signal(self, signal_dict: Dict[str, Any]) -> SignalValidation:
        """
        Main signal validation function
        Returns comprehensive validation result with weighted scoring
        """
        start_time = datetime.now()
        
        # Log validation start
        self.tracker.log_event(
            EventType.PHASE_START,
            "smart_logic",
            f"Starting signal validation for {signal_dict.get('symbol', 'UNKNOWN')}",
            {"signal_keys": list(signal_dict.keys())}
        )
        
        try:
            # Run all filters
            filter_results = []
            
            # 1. Risk-Reward (hard requirement)
            rr_result = self._validate_risk_reward(signal_dict)
            filter_results.append(rr_result)
            
            # If RR fails, immediately reject
            if not rr_result.passed:
                return SignalValidation(
                    passed=False,
                    score=0.0,
                    reject_reason=rr_result.reason,
                    filter_scores=filter_results,
                    risk_reward_ratio=signal_dict.get("risk_reward_ratio", 0),
                    confluence_count=0,
                    validation_timestamp=datetime.now(timezone.utc).isoformat(),
                    charter_compliant=False
                )
            
            # 2. FVG Confluence
            fvg_result = self._validate_fvg_confluence(signal_dict)
            filter_results.append(fvg_result)
            
            # 3. Fibonacci Confluence  
            fib_result = self._validate_fibonacci_confluence(signal_dict)
            filter_results.append(fib_result)
            
            # 4. Volume Profile
            volume_result = self._validate_volume_profile(signal_dict)
            filter_results.append(volume_result)
            
            # 5. Momentum
            momentum_result = self._validate_momentum(signal_dict)
            filter_results.append(momentum_result)
            
            # Calculate weighted average score
            total_weighted_score = 0
            total_weight = 0
            passing_filters = 0
            
            for result in filter_results:
                weighted_score = result.score * result.weight
                total_weighted_score += weighted_score
                total_weight += result.weight
                
                if result.passed:
                    passing_filters += 1
            
            final_score = total_weighted_score / total_weight if total_weight > 0 else 0
            
            # Determine if signal passes overall
            score_passes = final_score >= self.min_total_score
            confluence_passes = passing_filters >= self.min_confluence_count
            overall_pass = score_passes and confluence_passes
            
            # Determine reject reason if failed
            reject_reason = None
            if not overall_pass:
                if not score_passes:
                    reject_reason = f"Total score {final_score:.2f} below minimum {self.min_total_score}"
                elif not confluence_passes:
                    reject_reason = f"Only {passing_filters} filters passed, need {self.min_confluence_count}"
            
            # Charter compliance (RR already checked above)
            charter_compliant = rr_result.passed
            
            # Create result
            result = SignalValidation(
                passed=overall_pass,
                score=final_score,
                reject_reason=reject_reason,
                filter_scores=filter_results,
                risk_reward_ratio=rr_result.details.get("calculated_rr", 0) if rr_result.details else 0,
                confluence_count=passing_filters,
                validation_timestamp=datetime.now(timezone.utc).isoformat(),
                charter_compliant=charter_compliant
            )
            
            # Log completion
            validation_time = (datetime.now() - start_time).total_seconds()
            self.tracker.log_event(
                EventType.PHASE_COMPLETE,
                "smart_logic",
                f"Signal validation completed: {'PASSED' if overall_pass else 'REJECTED'} ({final_score:.2f})",
                {
                    "passed": overall_pass,
                    "score": final_score,
                    "confluence_count": passing_filters,
                    "validation_time_ms": int(validation_time * 1000),
                    "reject_reason": reject_reason
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Signal validation failed: {e}")
            self.tracker.log_event(
                EventType.SYSTEM_ERROR,
                "smart_logic",
                f"Validation error: {str(e)}"
            )
            
            # Return safe fallback
            return SignalValidation(
                passed=False,
                score=0.0,
                reject_reason=f"Validation system error: {str(e)}",
                filter_scores=[],
                risk_reward_ratio=0,
                confluence_count=0,
                validation_timestamp=datetime.now(timezone.utc).isoformat(),
                charter_compliant=False
            )
    
    def get_filter_summary(self, validation: SignalValidation) -> Dict[str, Any]:
        """Get human-readable validation summary"""
        return {
            "overall_result": "PASSED" if validation.passed else "REJECTED",
            "total_score": f"{validation.score:.1%}",
            "confluence_count": f"{validation.confluence_count}/{len(validation.filter_scores)}",
            "risk_reward_ratio": f"{validation.risk_reward_ratio:.2f}",
            "charter_compliant": validation.charter_compliant,
            "reject_reason": validation.reject_reason,
            "filter_breakdown": [
                {
                    "filter": fs.filter_name,
                    "passed": "✅" if fs.passed else "❌",
                    "score": f"{fs.score:.1%}",
                    "weight": f"{fs.weight:.1%}",
                    "reason": fs.reason
                }
                for fs in validation.filter_scores
            ]
        }

# Global filter instance
_global_filter = None

def get_smart_filter(pin: int = None) -> SmartLogicFilter:
    """Get global smart logic filter instance"""
    global _global_filter
    if _global_filter is None:
        _global_filter = SmartLogicFilter(pin)
    return _global_filter

def validate_trading_signal(signal_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for signal validation"""
    filter_system = get_smart_filter()
    validation = filter_system.validate_signal(signal_dict)
    
    return {
        "passed": validation.passed,
        "score": validation.score,
        "reject_reason": validation.reject_reason
    }

if __name__ == "__main__":
    # Self-test with sample signals
    print("SmartLogicFilter self-test starting...")
    
    # Create smart filter
    smart_filter = SmartLogicFilter(pin=841921)
    
    # Test signal that should PASS (good RR, confluence)
    passing_signal = {
        "symbol": "EURUSD",
        "direction": "buy",
        "entry_price": 1.0850,
        "target_price": 1.0950,  # +100 pips
        "stop_loss": 1.0820,     # -30 pips, RR = 100/30 = 3.33
        "swing_high": 1.0900,
        "swing_low": 1.0800,
        "recent_highs": [1.0860, 1.0870, 1.0855, 1.0865],
        "recent_lows": [1.0840, 1.0830, 1.0835, 1.0845],
        "recent_closes": [1.0850, 1.0845, 1.0855, 1.0860] + [1.0850 + i*0.001 for i in range(10)],
        "recent_volumes": [1000, 1200, 800, 1500] + [1100 + i*50 for i in range(10)]
    }
    
    # Test signal that should FAIL (bad RR)
    failing_signal = {
        "symbol": "GBPUSD", 
        "direction": "sell",
        "entry_price": 1.2500,
        "target_price": 1.2480,  # +20 pips
        "stop_loss": 1.2510,     # -10 pips, RR = 20/10 = 2.0 (below 3.0 minimum)
        "swing_high": 1.2550,
        "swing_low": 1.2450,
        "recent_highs": [1.2510, 1.2505, 1.2515, 1.2500],
        "recent_lows": [1.2490, 1.2485, 1.2495, 1.2480],
        "recent_closes": [1.2500] * 15,
        "recent_volumes": [900] * 15
    }
    
    test_cases = [
        ("PASSING Signal", passing_signal),
        ("FAILING Signal", failing_signal)
    ]
    
    print("\nSignal Validation Results:")
    print("=" * 60)
    
    all_tests_passed = True
    
    for name, signal in test_cases:
        print(f"\n{name}:")
        
        validation = smart_filter.validate_signal(signal)
        summary = smart_filter.get_filter_summary(validation)
        
        print(f"  Result: {summary['overall_result']}")
        print(f"  Score: {summary['total_score']}")
        print(f"  RR Ratio: {summary['risk_reward_ratio']}")
        print(f"  Confluence: {summary['confluence_count']}")
        
        if validation.reject_reason:
            print(f"  Reject Reason: {validation.reject_reason}")
        
        print("  Filter Breakdown:")
        for filter_detail in summary['filter_breakdown']:
            print(f"    {filter_detail['passed']} {filter_detail['filter']}: {filter_detail['score']} - {filter_detail['reason']}")
        
        # Validate expected results
        if name == "PASSING Signal" and not validation.passed:
            print("  ❌ Expected PASS but got FAIL")
            all_tests_passed = False
        elif name == "FAILING Signal" and validation.passed:
            print("  ❌ Expected FAIL but got PASS")  
            all_tests_passed = False
        elif name == "FAILING Signal" and validation.reject_reason and "RR" in validation.reject_reason:
            print("  ✅ Correctly rejected for RR < 3.0")
        else:
            print("  ✅ Result as expected")
    
    # Test convenience function
    print("\nTesting convenience function:")
    conv_result = validate_trading_signal(passing_signal)
    print(f"Convenience function result: {conv_result}")
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("✅ Signal rejected if RR < 3.0")
        print("✅ Weighted scoring shows confluence reasons")
        print("✅ All smart logic filter tests PASSED")
        print("\nSmartLogicFilter self-test completed successfully! 🔐")
    else:
        print("❌ Some tests FAILED")
        exit(1)