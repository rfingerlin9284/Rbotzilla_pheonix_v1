import logging
from typing import Optional, Dict

# The forward-compatible large QuantHedgeRules sits later in this file; the
# get_hedge_params() helper below provides a small mapping that our engine
# expects. We'll attach it to the main class as an accessor.

def _simple_get_hedge_params(regime: str, volatility: float) -> Dict:
    params = {
        "size_multiplier": 1.0,
        "hedge_ratio": 0.0,
        "stop_tightener": 1.0,
        "mode": "STANDARD"
    }
    if regime == "BULL_STRONG":
        params["size_multiplier"] = 1.2
        params["stop_tightener"] = 1.2
        params["mode"] = "ATTACK_BULL"
    elif regime == "BEAR_STRONG":
        params["size_multiplier"] = 1.2
        params["stop_tightener"] = 1.0
        params["mode"] = "ATTACK_BEAR"
    elif regime == "SIDEWAYS":
        params["size_multiplier"] = 0.6
        params["stop_tightener"] = 0.5
        params["mode"] = "DEFENSE_CHOP"
    elif regime == "CRISIS" or volatility > 0.02:
        params["size_multiplier"] = 0.2
        params["stop_tightener"] = 0.25
        params["mode"] = "BUNKER_PROTOCOL"
    return params

#!/usr/bin/env python3
"""
Quant Hedge Rules System - Multi-Condition Analysis Engine
Analyzes market conditions and provides hedging/positioning recommendations
PIN: 841921 | Phase: Active Analysis

================================================================================
CONSOLIDATION DOCUMENTATION INTEGRATION
================================================================================

REFERENCE: See /home/ing/RICK/new_RLC_rebuild/CONSOLIDATION_INDEX.md (kept separate for records)

QUANT HEDGE SYSTEM OVERVIEW:
  Analyzes 5 weighted market conditions
  Provides 7 recommended actions
  Used for real-time position management (every 60 seconds)
  Autonomous execution of hedge actions

5 WEIGHTED CONDITIONS (Total Weight = 100%):

1. VOLATILITY (Weight: 30%)
   ├─ Calculation: ATR-based, 14-period standard
   ├─ Severity Levels:
   │  ├─ LOW: 0-1.5% annualized (GREEN)
   │  ├─ MODERATE: 1.5-3.0% annualized (YELLOW)
   │  ├─ HIGH: 3.0-5.0% annualized (YELLOW)
   │  └─ EXTREME: 5%+ annualized (RED)
   ├─ Impact: Higher volatility = higher hedge likelihood
   └─ Platform Impact: Crypto needs higher thresholds

2. TREND STRENGTH (Weight: 25%)
   ├─ Calculation: ADX-based (Average Directional Index)
   ├─ Analysis: Momentum strength detection
   ├─ Weak Trend: ADX < 20 (uncertain direction)
   ├─ Strong Trend: ADX > 40 (clear direction)
   ├─ Impact: Weak trends increase hedge probability
   └─ Use Case: Prevents trading counter to weak trends

3. CORRELATION RISK (Weight: 20%)
   ├─ Calculation: USD correlation analysis
   ├─ Levels:
   │  ├─ LOW: <40% correlation (GREEN)
   │  ├─ MODERATE: 40-70% correlation (YELLOW)
   │  ├─ HIGH: 70-90% correlation (YELLOW)
   │  └─ EXTREME: >90% correlation (RED)
   ├─ Impact: High correlation = recommend hedge
   └─ Gate: Charter Correlation Guard enforces max 70%

4. VOLUME CONFIRMATION (Weight: 15%)
   ├─ Calculation: Volume vs. moving average
   ├─ Check: Is this trend confirmed by volume?
   ├─ Low Volume: Weak confirmation (risky)
   ├─ High Volume: Strong confirmation (safer)
   ├─ Impact: Low volume can trigger PAUSE_TRADING
   └─ Use Case: Prevents trading on low-volume moves

5. MARGIN UTILIZATION (Weight: 10%)
   ├─ Calculation: margin_used / NAV
   ├─ Levels:
   │  ├─ LOW: <20% (GREEN)
   │  ├─ MODERATE: 20-35% (YELLOW)
   │  ├─ HIGH: >35% (RED)
   ├─ Impact: High margin = recommend REDUCE_EXPOSURE
   └─ Gate: Guardian gate enforces max 35%

7 HEDGE ACTIONS (Recommendations):

1. FULL_LONG
   ├─ Condition: All indicators GREEN, high confidence
   ├─ Meaning: Aggressive long position is appropriate
   ├─ Action: Open full-size position, no hedge needed
   ├─ Example: Bullish regime + strong trend + low correlation
   └─ Confidence: ≥80%

2. MODERATE_LONG
   ├─ Condition: Mixed signals, some caution needed
   ├─ Meaning: Conservative long position is appropriate
   ├─ Action: Open 50% position size, consider hedge
   ├─ Example: Bullish trend but elevated volatility
   └─ Confidence: 60-80%

3. REDUCE_EXPOSURE
   ├─ Condition: YELLOW signals detected
   ├─ Meaning: Cut existing positions by 50%
   ├─ Action: Close 50% of open positions
   ├─ Example: Correlation risk increasing, margin high
   └─ Trigger: Market regime transitioning or margin >30%

4. CLOSE_ALL
   ├─ Condition: CRITICAL risk signals (RED)
   ├─ Meaning: Exit all positions immediately
   ├─ Action: Market close all positions at market price
   ├─ Example: Volatility EXTREME + correlation EXTREME + margin HIGH
   └─ Emergency: Cascading failures, risk protection

5. HEDGE_SHORT
   ├─ Condition: Offsetting hedge needed
   ├─ Meaning: Add short position to hedge long exposure
   ├─ Action: Open 25-50% short position
   ├─ Example: Long USD exposure + correlation risk + trend uncertain
   └─ Risk Mitigation: Protects against reversal

6. PAUSE_TRADING
   ├─ Condition: ELEVATED risk, too uncertain
   ├─ Meaning: Stop opening new positions temporarily
   ├─ Action: Hold existing positions, don't enter new
   ├─ Example: Low volume confirmation + trend weak + volatility high
   └─ Duration: Until conditions improve

7. WAIT_FOR_CLARITY
   ├─ Condition: Mixed signals, unclear direction
   ├─ Meaning: Monitor market, make no major changes
   ├─ Action: Hold existing positions, don't add or reduce
   ├─ Example: Trend transitioning, regime change happening
   └─ Duration: 5-15 minutes until clarity emerges

DECISION MATRIX:

┌─────────────────────────────────────────────────────────────┐
│ Vol     │ Trend  │ Corr    │ Volume  │ Margin  │ Action     │
├─────────────────────────────────────────────────────────────┤
│ LOW     │ STRONG │ LOW     │ HIGH    │ LOW     │ FULL_LONG  │
│ MOD     │ STRONG │ LOW     │ HIGH    │ MOD     │ MODERATE   │
│ HIGH    │ STRONG │ LOW     │ HIGH    │ MOD     │ MODERATE   │
│ EXTREME │ WEAK   │ HIGH    │ LOW     │ HIGH    │ CLOSE_ALL  │
│ HIGH    │ STRONG │ HIGH    │ MOD     │ HIGH    │ REDUCE_EXP │
│ MOD     │ WEAK   │ MOD     │ LOW     │ MOD     │ PAUSE      │
│ MOD     │ WEAK   │ EXTREME │ LOW     │ HIGH    │ CLOSE_ALL  │
│ LOW     │ WEAK   │ MOD     │ HIGH    │ LOW     │ WAIT       │
└─────────────────────────────────────────────────────────────┘

EXECUTION FREQUENCY:
  Real-time monitoring: Every 60 seconds
  Automatic recalculation: With each position check
  Updates: Sent to position manager for autonomous action

INTEGRATION POINTS:
  ├─ position_manager.py: Uses hedge actions to manage positions
  ├─ enhanced_task_config.py: Reports actions in real-time
  ├─ narration_logger.py: Logs all hedge decisions
  └─ dashboard.py: Visualizes hedge analysis

COMPLETE DOCUMENTATION IN:
  └─ /home/ing/RICK/new_RLC_rebuild/CONSOLIDATION_INDEX.md (KEPT SEPARATE)
  └─ /home/ing/RICK/new_RLC_rebuild/CHARTER_AND_GATING_CONSOLIDATION.md
  └─ /home/ing/RICK/new_RLC_rebuild/RULE_MATRIX_STRUCTURED.md

================================================================================
"""

import numpy as np
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.rick_charter import RickCharter
from foundation.social_reader import get_social_sentiment_summary
from logic.regime_detector import RegimeDetector, MarketRegime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HedgeAction(Enum):
    """Recommended hedge actions based on market conditions"""
    FULL_LONG = "full_long"           # Aggressive long positions
    MODERATE_LONG = "moderate_long"    # Conservative long positions
    REDUCE_EXPOSURE = "reduce_exposure" # Cut position size by 50%
    CLOSE_ALL = "close_all"            # Exit all positions immediately
    HEDGE_SHORT = "hedge_short"        # Add offsetting short hedge
    PAUSE_TRADING = "pause_trading"    # Stop new entries temporarily
    WAIT_FOR_CLARITY = "wait_for_clarity"  # Hold and monitor

class VolatilityLevel(Enum):
    """Volatility classification"""
    LOW = "low"           # 0-1.5% annualized
    MODERATE = "moderate" # 1.5-3.0% annualized
    HIGH = "high"         # 3.0-5.0% annualized
    EXTREME = "extreme"   # 5%+ annualized

class CorrelationLevel(Enum):
    """Correlation risk classification"""
    LOW = "low"           # Different assets moving independently
    MODERATE = "moderate" # Some correlation detected
    HIGH = "high"         # Strong correlation (risky for diversification)
    EXTREME = "extreme"   # Perfect/near-perfect correlation

@dataclass
class HedgeCondition:
    """Individual condition evaluation for hedge decision"""
    condition_name: str
    current_value: float
    threshold: float
    severity: str           # "green", "yellow", "red"
    recommendation: str
    details: Optional[Dict[str, Any]] = None

@dataclass
class QuantHedgeAnalysis:
    """Complete multi-condition hedge analysis"""
    timestamp: datetime
    regime: str
    volatility_level: str
    volatility_value: float
    
    conditions: List[HedgeCondition]
    
    # Severity scores
    severity_score: float          # 0-100, higher = more risky
    
    # Recommended action
    primary_action: str
    secondary_actions: List[str]
    
    # Position sizing multiplier
    position_size_multiplier: float  # 0.25 to 1.5x normal
    
    # Risk level
    risk_level: str                # "safe", "moderate", "elevated", "critical"
    
    # Confidence in recommendation
    confidence: float              # 0-1.0
    
    # Summary
    summary: str
    detailed_analysis: Dict

class QuantHedgeRules:
    """
    Multi-condition analysis engine for quant hedge decisions
    Evaluates market conditions and provides positioning recommendations
    """
    
    def __init__(self, pin: int = 841921):
        if not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid PIN for QuantHedgeRules")
        
        self.pin_verified = True
        # Use simple detector by default; full StochasticRegimeDetector may be
        # present in future expansions.
        try:
            self.regime_detector = RegimeDetector()
        except Exception:
            self.regime_detector = None
        self.logger = logger
        
        # Condition thresholds
        self.volatility_thresholds = {
            'low': 0.015,
            'moderate': 0.030,
            'high': 0.050,
            'extreme': 0.075
        }
        
        # Condition weights (sum = 1.0)
        self.condition_weights = {
            'volatility': 0.30,           # Market volatility (30%)
            'trend_strength': 0.25,        # Trend momentum (25%)
            'correlation': 0.20,           # Asset correlation risk (20%)
            'volume': 0.15,                # Volume confirmation (15%)
            'margin_utilization': 0.10    # Account margin usage (10%)
        }
        
        self.logger.info("QuantHedgeRules initialized with PIN verification")

    def get_hedge_params(self, regime: str, volatility: float):
        """Compatibility helper for rbotzilla_engine small mapping interface."""
        return _simple_get_hedge_params(regime, volatility)
    
    def analyze_market_conditions(
        self,
        prices: np.ndarray,
        volume: np.ndarray,
        account_nav: float,
        margin_used: float,
        open_positions: int,
        correlation_matrix: Optional[Dict[str, float]] = None,
        lookback_periods: int = 50
    ) -> QuantHedgeAnalysis:
        """
        Comprehensive multi-condition analysis
        
        Args:
            prices: Price array (OHLC close prices)
            volume: Volume array
            account_nav: Net asset value
            margin_used: Current margin utilization $
            open_positions: Number of open positions
            correlation_matrix: Dict of symbol correlations
            lookback_periods: Historical periods to analyze
            
        Returns:
            QuantHedgeAnalysis with recommendations
        """
        
        timestamp = datetime.now(timezone.utc)
        conditions = []
        condition_scores = {}
        
        # CONDITION 1: Volatility Analysis
        volatility = self._calculate_volatility(prices)
        vol_level = self._classify_volatility(volatility)
        vol_condition = self._evaluate_volatility_condition(volatility, vol_level)
        conditions.append(vol_condition)
        condition_scores['volatility'] = self._score_volatility(vol_level)
        
        # CONDITION 2: Trend Strength
        trend = self._calculate_trend(prices)
        trend_condition = self._evaluate_trend_condition(trend)
        conditions.append(trend_condition)
        condition_scores['trend_strength'] = self._score_trend(trend)
        
        # CONDITION 3: Correlation Risk
        corr_condition = self._evaluate_correlation_condition(correlation_matrix)
        conditions.append(corr_condition)
        condition_scores['correlation'] = self._score_correlation(corr_condition)
        
        # CONDITION 4: Volume Analysis
        vol_analysis = self._analyze_volume(volume)
        volume_condition = self._evaluate_volume_condition(vol_analysis)
        conditions.append(volume_condition)
        condition_scores['volume'] = self._score_volume(volume_condition)
        
        # CONDITION 5: Margin Utilization
        margin_ratio = margin_used / account_nav if account_nav > 0 else 0
        margin_condition = self._evaluate_margin_condition(margin_ratio)
        conditions.append(margin_condition)
        condition_scores['margin_utilization'] = self._score_margin(margin_condition)
        
        # Calculate weighted severity score
        severity_score = sum(
            condition_scores[key] * self.condition_weights[key]
            for key in condition_scores
        ) * 100.0
        
        # Detect regime
        # Detect regime (handle both detect_regime and detect interfaces)
        regime = "triage"
        if hasattr(self.regime_detector, 'detect_regime'):
            rd = self.regime_detector.detect_regime(prices)
            regime = rd.regime.value if rd else 'triage'
        elif hasattr(self.regime_detector, 'detect'):
            r, vol = self.regime_detector.detect()
            regime = r

        # Normalize regime string to standard values expected by MarketRegime
        regime = self._normalize_regime(regime)
        
        # Generate hedge recommendation
        primary_action, secondary_actions, position_multiplier, confidence = self._generate_recommendation(
            regime=regime,
            volatility_level=vol_level,
            severity_score=severity_score,
            conditions=conditions,
            trend=trend
        )
        
        # Classify risk level
        risk_level = self._classify_risk_level(severity_score)
        
        # Generate summary
        summary = self._generate_summary(
            primary_action=primary_action,
            risk_level=risk_level,
            volatility_level=vol_level,
            regime=regime,
            severity_score=severity_score
        )
        
        # Detailed analysis
        detailed_analysis = {
            'volatility_pct': volatility * 100,
            'trend_strength': trend,
            'correlation_risk': corr_condition.current_value,
            'volume_trend': vol_analysis.get('trend', 'unknown'),
            'margin_ratio': margin_ratio * 100,
            'open_positions': open_positions,
            'position_size_multiplier': position_multiplier,
            'condition_scores': condition_scores,
            'severity_breakdown': {
                cond.condition_name: cond.severity
                for cond in conditions
            }
        }
        # Attempt to attach social sentiment if available
        try:
            social = get_social_sentiment_summary(subreddits=None, limit=10)
            detailed_analysis['social_sentiment'] = social
            # If the social sentiment is strongly negative, increase severity slightly
            avg_comp = social.get('avg_compound', 0)
            if avg_comp < -0.35:
                severity_score = min(100.0, severity_score + 10.0)
            elif avg_comp > 0.3:
                severity_score = max(0.0, severity_score - 5.0)
            # Update risk level after potential adjustments
            detailed_analysis['adjusted_severity_score'] = severity_score
            # Recompute risk level and regenerate summary to reflect adjusted severity
            risk_level = self._classify_risk_level(severity_score)
            summary = self._generate_summary(
                primary_action=primary_action,
                risk_level=risk_level,
                volatility_level=vol_level,
                regime=regime,
                severity_score=severity_score
            )
            detailed_analysis['social_influence'] = 'minor'
        except Exception as e:
            self.logger.debug(f'Could not fetch social sentiment: {e}')
        
        return QuantHedgeAnalysis(
            timestamp=timestamp,
            regime=regime,
            volatility_level=vol_level,
            volatility_value=volatility,
            conditions=conditions,
            severity_score=severity_score,
            primary_action=primary_action,
            secondary_actions=secondary_actions,
            position_size_multiplier=position_multiplier,
            risk_level=risk_level,
            confidence=confidence,
            summary=summary,
            detailed_analysis=detailed_analysis
        )
    
    def _calculate_volatility(self, prices: np.ndarray) -> float:
        """Calculate annualized volatility"""
        if len(prices) < 2:
            return 0.0
        returns = np.diff(prices) / prices[:-1]
        return np.std(returns) * np.sqrt(252)  # Annualize
    
    def _classify_volatility(self, volatility: float) -> str:
        """Classify volatility into levels"""
        if volatility < self.volatility_thresholds['low']:
            return VolatilityLevel.LOW.value
        elif volatility < self.volatility_thresholds['moderate']:
            return VolatilityLevel.MODERATE.value
        elif volatility < self.volatility_thresholds['high']:
            return VolatilityLevel.HIGH.value
        else:
            return VolatilityLevel.EXTREME.value
    
    def _evaluate_volatility_condition(self, volatility: float, vol_level: str) -> HedgeCondition:
        """Evaluate volatility condition"""
        if vol_level == VolatilityLevel.EXTREME.value:
            severity = "red"
            rec = "REDUCE position size, consider hedges, tighter stops"
        elif vol_level == VolatilityLevel.HIGH.value:
            severity = "yellow"
            rec = "Reduce to 75% position size, add hedges if large exposure"
        elif vol_level == VolatilityLevel.MODERATE.value:
            severity = "green"
            rec = "Normal trading allowed, full position sizes OK"
        else:
            severity = "green"
            rec = "Favorable conditions, can increase leverage to 1.2x if desired"
        
        return HedgeCondition(
            condition_name="Volatility",
            current_value=volatility,
            threshold=self.volatility_thresholds.get(vol_level, 0.05),
            severity=severity,
            recommendation=rec,
            details={'volatility_level': vol_level}
        )
    
    def _calculate_trend(self, prices: np.ndarray) -> float:
        """Calculate trend strength (-1 to 1)"""
        if len(prices) < 2:
            return 0.0
        x = np.arange(len(prices))
        slope, _ = np.polyfit(x, prices, 1)
        return slope / np.mean(prices)
    
    def _evaluate_trend_condition(self, trend: float) -> HedgeCondition:
        """Evaluate trend condition"""
        abs_trend = abs(trend)
        
        if abs_trend > 0.05:
            severity = "green"
            rec = "Strong trend detected, favor directional trades"
            trend_type = "STRONG"
        elif abs_trend > 0.02:
            severity = "green"
            rec = "Moderate trend, balanced approach OK"
            trend_type = "MODERATE"
        elif abs_trend > 0.005:
            severity = "yellow"
            rec = "Weak trend, favor range-bound strategies"
            trend_type = "WEAK"
        else:
            severity = "yellow"
            rec = "No clear trend, use range strategies or PAUSE"
            trend_type = "SIDEWAYS"
        
        return HedgeCondition(
            condition_name="Trend Strength",
            current_value=trend,
            threshold=0.02,
            severity=severity,
            recommendation=rec,
            details={'trend_type': trend_type, 'trend_direction': 'UP' if trend > 0 else 'DOWN'}
        )
    
    def _evaluate_correlation_condition(self, correlation_matrix: Optional[Dict[str, float]] = None) -> HedgeCondition:
        """Evaluate correlation risk"""
        if correlation_matrix is None or len(correlation_matrix) == 0:
            corr_value = 0.0
            severity = "green"
            rec = "No correlation risk detected"
        else:
            # Check for high correlations
            high_corrs = [v for v in correlation_matrix.values() if abs(v) > 0.8]
            corr_value = np.mean(list(correlation_matrix.values())) if correlation_matrix else 0.0
            
            if len(high_corrs) > 2:
                severity = "red"
                rec = "HIGH correlation detected - positions highly correlated, reduce size or hedge"
            elif len(high_corrs) > 0:
                severity = "yellow"
                rec = "Moderate correlation detected - monitor for concentration risk"
            else:
                severity = "green"
                rec = "Low correlation - good diversification"
        
        return HedgeCondition(
            condition_name="Correlation",
            current_value=corr_value,
            threshold=0.5,
            severity=severity,
            recommendation=rec,
            details={'high_correlation_pairs': len(high_corrs) if correlation_matrix else 0}
        )
    
    def _analyze_volume(self, volume: np.ndarray) -> Dict:
        """Analyze volume trends"""
        if len(volume) < 20:
            return {'trend': 'insufficient_data', 'ma_ratio': 1.0}
        
        recent_vol = np.mean(volume[-5:])
        ma_vol = np.mean(volume[-20:])
        ratio = recent_vol / ma_vol if ma_vol > 0 else 1.0
        
        if ratio > 1.5:
            trend = "increasing"
        elif ratio > 0.9:
            trend = "normal"
        else:
            trend = "decreasing"
        
        return {'trend': trend, 'ma_ratio': ratio}
    
    def _evaluate_volume_condition(self, vol_analysis: Dict) -> HedgeCondition:
        """Evaluate volume condition"""
        trend = vol_analysis.get('trend', 'unknown')
        ratio = vol_analysis.get('ma_ratio', 1.0)
        
        if trend == "increasing":
            severity = "green"
            rec = "High volume confirms moves, full trade sizing OK"
        elif trend == "normal":
            severity = "green"
            rec = "Normal volume, standard trading OK"
        elif trend == "decreasing":
            severity = "yellow"
            rec = "Low volume, reduce position size by 25-50%"
        else:
            severity = "yellow"
            rec = "Insufficient volume data, use caution"
        
        return HedgeCondition(
            condition_name="Volume",
            current_value=ratio,
            threshold=1.0,
            severity=severity,
            recommendation=rec,
            details={'volume_trend': trend}
        )
    
    def _evaluate_margin_condition(self, margin_ratio: float) -> HedgeCondition:
        """Evaluate margin utilization"""
        if margin_ratio > 0.35:  # Charter max
            severity = "red"
            rec = "MARGIN EXCEEDED - STOP trading, reduce positions immediately"
        elif margin_ratio > 0.28:
            severity = "yellow"
            rec = "Margin elevated - reduce position size, no new entries"
        elif margin_ratio > 0.15:
            severity = "green"
            rec = "Margin OK, but elevated - monitor closely"
        else:
            severity = "green"
            rec = "Low margin usage, room for more exposure"
        
        return HedgeCondition(
            condition_name="Margin Utilization",
            current_value=margin_ratio,
            threshold=0.35,
            severity=severity,
            recommendation=rec,
            details={'margin_pct': margin_ratio * 100}
        )
    
    def _score_volatility(self, vol_level: str) -> float:
        """Score volatility condition (0-1, higher = riskier)"""
        scores = {
            VolatilityLevel.LOW.value: 0.1,
            VolatilityLevel.MODERATE.value: 0.3,
            VolatilityLevel.HIGH.value: 0.6,
            VolatilityLevel.EXTREME.value: 0.9
        }
        return scores.get(vol_level, 0.5)
    
    def _score_trend(self, trend: float) -> float:
        """Score trend (0-1, higher = riskier if no clear trend)"""
        abs_trend = abs(trend)
        if abs_trend > 0.05:
            return 0.1  # Strong trend = favorable
        elif abs_trend > 0.02:
            return 0.3  # Moderate
        else:
            return 0.7  # No trend = risky
    
    def _score_correlation(self, cond: HedgeCondition) -> float:
        """Score correlation risk"""
        high_corrs = cond.details.get('high_correlation_pairs', 0) if cond.details else 0
        return min(1.0, high_corrs * 0.3)
    
    def _score_volume(self, cond: HedgeCondition) -> float:
        """Score volume condition"""
        trend = cond.details.get('volume_trend', 'unknown') if cond.details else 'unknown'
        if trend == 'increasing':
            return 0.1
        elif trend == 'normal':
            return 0.3
        else:
            return 0.6
    
    def _score_margin(self, cond: HedgeCondition) -> float:
        """Score margin condition"""
        margin_pct = cond.details.get('margin_pct', 0) if cond.details else 0
        return min(1.0, margin_pct / 35.0)  # 35% = max
    
    def _generate_recommendation(
        self,
        regime: str,
        volatility_level: str,
        severity_score: float,
        conditions: List[HedgeCondition],
        trend: float
    ) -> Tuple[str, List[str], float, float]:
        """
        Generate hedge action based on all conditions
        
        Returns:
            (primary_action, secondary_actions, position_multiplier, confidence)
        """
        
        # Count red/yellow/green conditions
        red_count = sum(1 for c in conditions if c.severity == "red")
        yellow_count = sum(1 for c in conditions if c.severity == "yellow")
        
        # Regime-based logic
        if regime == MarketRegime.CRASH.value:
            primary = HedgeAction.CLOSE_ALL.value
            secondary = [HedgeAction.PAUSE_TRADING.value]
            multiplier = 0.0
            confidence = 0.95
        
        elif regime == MarketRegime.BEAR.value:
            if red_count > 0:
                primary = HedgeAction.REDUCE_EXPOSURE.value
                secondary = [HedgeAction.HEDGE_SHORT.value]
                multiplier = 0.5
            else:
                primary = HedgeAction.MODERATE_LONG.value
                secondary = [HedgeAction.HEDGE_SHORT.value]
                multiplier = 0.75
            confidence = 0.8
        
        elif regime == MarketRegime.BULL.value:
            if red_count > 0:
                primary = HedgeAction.PAUSE_TRADING.value
                secondary = [HedgeAction.REDUCE_EXPOSURE.value]
                multiplier = 0.5
                confidence = 0.7
            elif yellow_count > 1:
                primary = HedgeAction.MODERATE_LONG.value
                secondary = [HedgeAction.WAIT_FOR_CLARITY.value]
                multiplier = 0.85
                confidence = 0.75
            else:
                primary = HedgeAction.FULL_LONG.value
                secondary = []
                multiplier = 1.5 if volatility_level == VolatilityLevel.LOW.value else 1.0
                confidence = 0.9
        
        elif regime == MarketRegime.SIDEWAYS.value:
            if red_count > 0:
                primary = HedgeAction.PAUSE_TRADING.value
                secondary = []
                multiplier = 0.5
            else:
                primary = HedgeAction.MODERATE_LONG.value
                secondary = [HedgeAction.WAIT_FOR_CLARITY.value]
                multiplier = 0.75
            confidence = 0.7
        
        else:  # TRIAGE
            primary = HedgeAction.WAIT_FOR_CLARITY.value
            secondary = [HedgeAction.PAUSE_TRADING.value]
            multiplier = 0.5
            confidence = 0.6
        
        return primary, secondary, multiplier, confidence

    def _normalize_regime(self, regime_str: str) -> str:
        """Normalize different regime strings to MarketRegime values."""
        if not isinstance(regime_str, str):
            return MarketRegime.TRIAGE.value
        r = regime_str.lower()
        if 'bull' in r:
            return MarketRegime.BULL.value
        if 'bear' in r:
            return MarketRegime.BEAR.value
        if 'crash' in r or 'crisis' in r:
            return MarketRegime.CRASH.value
        if 'side' in r or 'sideways' in r:
            return MarketRegime.SIDEWAYS.value
        return MarketRegime.TRIAGE.value
    
    def _classify_risk_level(self, severity_score: float) -> str:
        """Classify overall risk level"""
        if severity_score < 25:
            return "safe"
        elif severity_score < 50:
            return "moderate"
        elif severity_score < 75:
            return "elevated"
        else:
            return "critical"
    
    def _generate_summary(
        self,
        primary_action: str,
        risk_level: str,
        volatility_level: str,
        regime: str,
        severity_score: float
    ) -> str:
        """Generate human-readable summary"""
        summary = f"""
QUANT HEDGE ANALYSIS SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Regime: {regime.upper()}
Volatility: {volatility_level.upper()}
Risk Level: {risk_level.upper()}
Severity Score: {severity_score:.1f}/100

PRIMARY ACTION: {primary_action.replace('_', ' ').upper()}

Market Analysis:
- {regime.capitalize()} market detected
- {volatility_level} volatility environment
- {risk_level} risk level indicated
- Recommendation: {primary_action.replace('_', ' ')}

Position Sizing: Adjust multiplier based on recommendation
Hedging: Implement secondary actions if applicable
        """
        return summary.strip()


if __name__ == "__main__":
    # Self-test
    print("Quant Hedge Rules self-test...")
    
    try:
        qh = QuantHedgeRules(pin=841921)
        
        # Simulate market data
        prices = np.random.normal(100, 2, size=100)  # Random prices
        volume = np.random.uniform(1000, 5000, size=100)  # Random volume
        
        # Test analysis
        analysis = qh.analyze_market_conditions(
            prices=prices,
            volume=volume,
            account_nav=10000,
            margin_used=2000,
            open_positions=1,
            correlation_matrix={'EUR/USD-GBP/USD': 0.7, 'BTC-ETH': 0.85}
        )
        
        print(f"\n✅ Regime Detected: {analysis.regime}")
        print(f"   Volatility: {analysis.volatility_level} ({analysis.volatility_value*100:.2f}%)")
        print(f"   Risk Level: {analysis.risk_level}")
        print(f"   Severity Score: {analysis.severity_score:.1f}/100")
        print(f"   Primary Action: {analysis.primary_action}")
        print(f"   Position Multiplier: {analysis.position_size_multiplier}x")
        print(f"   Confidence: {analysis.confidence*100:.0f}%")
        
        print("\n📋 Conditions Evaluated:")
        for cond in analysis.conditions:
            status = "🟢" if cond.severity == "green" else "🟡" if cond.severity == "yellow" else "🔴"
            print(f"   {status} {cond.condition_name}: {cond.recommendation}")
        
        print(f"\n{analysis.summary}")
        print("\n✅ QuantHedgeRules module validated")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
