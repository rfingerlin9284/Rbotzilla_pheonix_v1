#!/usr/bin/env python3
"""
RICK Phoenix Consolidated Strategy Package
==========================================

This package consolidates all strategy-related code from the RICK Phoenix
trading system into 5 core modules. All non-redundant logic has been preserved.

Modules:
--------
1. consolidated_core_strategies.py
   - WolfPack strategies (Momentum, MeanReversion, Breakout, Trend, Range)
   - BullishWolf, BearishWolf, SidewaysWolf
   - FibConfluenceBreakout, CryptoBreakout
   - MomentumSignals
   - StrategyAggregator (voting system)

2. consolidated_risk_management.py
   - DynamicSizing (Kelly Criterion)
   - CorrelationMonitor (USD exposure tracking)
   - SessionBreaker (-5% daily halt)
   - QuantHedgeRules (multi-condition analysis)
   - UnifiedRiskManager

3. consolidated_ml_learning.py
   - StochasticRegimeDetector (Bull/Bear/Sideways/Crash)
   - PatternLearner (similarity matching)
   - MLRewardSystem (confidence adjustment)
   - AdaptiveRick (combined ML interface)

4. consolidated_gates.py
   - GuardianGates (4 pre-trade gates)
   - CryptoEntryGate (90% consensus)
   - ExecutionGate (R:R validation)
   - UnifiedGateSystem

5. consolidated_utilities.py
   - SmartTrailingSystem (progressive trailing stops)
   - QuantHedgeEngine (correlation hedging)
   - DynamicStops (ATR-based stops)
   - SmartAggression (adaptive sizing)
   - TradingUtilities (unified interface)

PIN: 841921 | Charter Compliant
"""

__version__ = "1.0.0"
__author__ = "RICK Phoenix System"
__pin__ = 841921

# Import all main classes for easy access
from .consolidated_core_strategies import (
    TechnicalIndicators,
    WolfPackStrategies,
    BullishWolfStrategy,
    BearishWolfStrategy,
    SidewaysWolfStrategy,
    BreakoutVolumeExpansion,
    FibConfluenceBreakout,
    CryptoBreakoutStrategy,
    MomentumSignals,
    StrategyAggregator,
    StrategySignal,
)

from .consolidated_risk_management import (
    DynamicSizing,
    CorrelationMonitor,
    SessionBreaker,
    QuantHedgeRules,
    UnifiedRiskManager,
    PositionSizeResult,
    HedgeAction,
)

from .consolidated_ml_learning import (
    StochasticRegimeDetector,
    PatternLearner,
    MLRewardSystem,
    AdaptiveRick,
    MarketRegime,
    RegimeData,
    TradePattern,
    detect_market_regime,
)

from .consolidated_gates import (
    GuardianGates,
    CryptoEntryGate,
    ExecutionGate,
    UnifiedGateSystem,
    GateResult,
    ExecutionDecision,
    RickCharter,
)

from .consolidated_utilities import (
    SmartTrailingSystem,
    MomentumDetector,
    QuantHedgeEngine,
    DynamicStops,
    SmartAggression,
    TradingUtilities,
    TrailingStopResult,
    HedgeRecommendation,
    StopTakeResult,
)

__all__ = [
    # Core Strategies
    'TechnicalIndicators',
    'WolfPackStrategies',
    'BullishWolfStrategy',
    'BearishWolfStrategy',
    'SidewaysWolfStrategy',
    'BreakoutVolumeExpansion',
    'FibConfluenceBreakout',
    'CryptoBreakoutStrategy',
    'MomentumSignals',
    'StrategyAggregator',
    'StrategySignal',
    
    # Risk Management
    'DynamicSizing',
    'CorrelationMonitor',
    'SessionBreaker',
    'QuantHedgeRules',
    'UnifiedRiskManager',
    'PositionSizeResult',
    'HedgeAction',
    
    # ML Learning
    'StochasticRegimeDetector',
    'PatternLearner',
    'MLRewardSystem',
    'AdaptiveRick',
    'MarketRegime',
    'RegimeData',
    'TradePattern',
    'detect_market_regime',
    
    # Gates
    'GuardianGates',
    'CryptoEntryGate',
    'ExecutionGate',
    'UnifiedGateSystem',
    'GateResult',
    'ExecutionDecision',
    'RickCharter',
    
    # Utilities
    'SmartTrailingSystem',
    'MomentumDetector',
    'QuantHedgeEngine',
    'DynamicStops',
    'SmartAggression',
    'TradingUtilities',
    'TrailingStopResult',
    'HedgeRecommendation',
    'StopTakeResult',
]
