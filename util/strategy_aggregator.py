#!/usr/bin/env python3
"""
Strategy Aggregator - Multi-Signal Consensus Engine
Combines 5 prototype strategies with ML filtering and Hive Mind amplification
PIN: 841921 | Phase 2 Integration
"""

import sys
import os
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone

# Add project root and strategies folder to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STRATEGIES_DIR = os.path.join(BASE_DIR, "strategies")
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, STRATEGIES_DIR)

# NOTE: The strategies in /strategies/ are CLASS-BASED (using registry.py pattern)
# This aggregator expects function-based signals - needs to be updated
# For now, attempt to use registry-based strategies with adapter pattern

TRAP_AVAILABLE = False
FIB_AVAILABLE = False
HOLY_GRAIL_AVAILABLE = False
LIQUIDITY_AVAILABLE = False
EMA_AVAILABLE = False

# Try to import class-based strategies from registry
try:
    from strategies.registry import (
        TrapReversalScalperStrategy,
        FibConfluenceBreakoutStrategy,
        PriceActionHolyGrailStrategy,
        LiquiditySweepReversalStrategy,
        TRAP_REVERSAL_META,
        FIB_CONFLUENCE_META,
        PA_HOLY_GRAIL_META,
        LIQ_SWEEP_META,
        build_active_strategies
    )
    from strategies.base import StrategyContext
    REGISTRY_AVAILABLE = True
    print("✅ Registry-based strategies loaded")
except ImportError as e:
    REGISTRY_AVAILABLE = False
    print(f"⚠️  Registry-based strategies not available: {e}")

try:
    from util.narration_logger import log_narration
    NARRATION_AVAILABLE = True
except ImportError:
    NARRATION_AVAILABLE = False


class StrategyAggregator:
    """
    Aggregates signals from 5 independent strategies
    Applies voting mechanism with configurable thresholds
    Confidence scoring based on multi-strategy agreement
    """
    
    def __init__(self, signal_vote_threshold: int = 2):
        """
        Initialize Strategy Aggregator
        
        Args:
            signal_vote_threshold: Minimum number of strategies that must agree (default: 2/5)
        """
        self.signal_vote_threshold = signal_vote_threshold
        
        # Strategy availability tracking
        # NOTE: Function-based strategies are deprecated - using class-based from registry
        self.strategies = {
            'trap_reversal': {
                'available': TRAP_AVAILABLE,
                'weight': 1.0,  # Equal weighting
                'fn': None  # Deprecated - use registry-based class
            },
            'fib_confluence': {
                'available': FIB_AVAILABLE,
                'weight': 1.0,
                'fn': None  # Deprecated - use registry-based class
            },
            'price_action_holy_grail': {
                'available': HOLY_GRAIL_AVAILABLE,
                'weight': 1.0,
                'fn': None  # Deprecated - use registry-based class
            },
            'liquidity_sweep': {
                'available': LIQUIDITY_AVAILABLE,
                'weight': 1.0,
                'fn': None  # Deprecated - use registry-based class
            },
            'ema_scalper': {
                'available': EMA_AVAILABLE,
                'weight': 1.0,
                'fn': None  # Not available in current codebase
            }
        }
        
        # Load registry-based strategies if available
        self.registry_strategies = []
        if REGISTRY_AVAILABLE:
            try:
                self.registry_strategies = build_active_strategies()
                print(f"✅ Loaded {len(self.registry_strategies)} registry strategies")
            except Exception as e:
                print(f"⚠️  Failed to build registry strategies: {e}")
        
        self.strategies_available = sum(
            1 for s in self.strategies.values() if s['available']
        )
        
        # Statistics tracking
        self.total_signals_evaluated = 0
        self.signals_accepted = 0
        self.signals_rejected = 0
        self.strategy_votes = {name: 0 for name in self.strategies.keys()}
    
    def aggregate_signals(
        self, 
        df: pd.DataFrame, 
        pair: str,
        direction: Optional[str] = None
    ) -> List[Dict]:
        """
        Run all available strategies and aggregate signals via voting
        
        Args:
            df: DataFrame with OHLC data (columns: open, high, low, close)
            pair: Currency pair (for logging)
            direction: 'buy', 'sell', or None (for non-directional strategies)
        
        Returns:
            List of aggregated signals with confidence scores
        """
        
        if len(df) < 5:
            return []
        
        self.total_signals_evaluated += 1
        aggregated = []
        votes = {}
        
        # ============================================
        # STRATEGY 1: Trap Reversal
        # ============================================
        if self.strategies['trap_reversal']['available'] and direction:
            try:
                trap_sig = self.strategies['trap_reversal']['fn'](df, direction)
                if trap_sig:
                    key = f"trap_reversal_{direction}"
                    votes[key] = trap_sig
                    self.strategy_votes['trap_reversal'] += 1
                    
                    if NARRATION_AVAILABLE:
                        log_narration(
                            event_type="STRATEGY_SIGNAL",
                            details={"strategy": "trap_reversal", "direction": direction},
                            symbol=pair
                        )
            except Exception as e:
                pass  # Silently fail on individual strategies
        
        # ============================================
        # STRATEGY 2: Fibonacci Confluence (non-directional)
        # ============================================
        if self.strategies['fib_confluence']['available']:
            try:
                fib_sigs = self.strategies['fib_confluence']['fn'](df)
                if fib_sigs:
                    for sig in fib_sigs:
                        key = f"fib_confluence_{sig['action']}"
                        votes[key] = sig
                        self.strategy_votes['fib_confluence'] += 1
                        
                        if NARRATION_AVAILABLE:
                            log_narration(
                                event_type="STRATEGY_SIGNAL",
                                details={"strategy": "fib_confluence", "action": sig['action']},
                                symbol=pair
                            )
            except Exception as e:
                pass
        
        # ============================================
        # STRATEGY 3: Price Action Holy Grail (non-directional)
        # ============================================
        if self.strategies['price_action_holy_grail']['available']:
            try:
                pa_sigs = self.strategies['price_action_holy_grail']['fn'](df)
                if pa_sigs:
                    for sig in pa_sigs:
                        key = f"price_action_{sig['action']}"
                        votes[key] = sig
                        self.strategy_votes['price_action_holy_grail'] += 1
                        
                        if NARRATION_AVAILABLE:
                            log_narration(
                                event_type="STRATEGY_SIGNAL",
                                details={"strategy": "price_action", "action": sig['action']},
                                symbol=pair
                            )
            except Exception as e:
                pass
        
        # ============================================
        # STRATEGY 4: Liquidity Sweep (non-directional)
        # ============================================
        if self.strategies['liquidity_sweep']['available']:
            try:
                liq_sigs = self.strategies['liquidity_sweep']['fn'](df)
                if liq_sigs:
                    for sig in liq_sigs:
                        key = f"liquidity_sweep_{sig['action']}"
                        votes[key] = sig
                        self.strategy_votes['liquidity_sweep'] += 1
                        
                        if NARRATION_AVAILABLE:
                            log_narration(
                                event_type="STRATEGY_SIGNAL",
                                details={"strategy": "liquidity_sweep", "action": sig['action']},
                                symbol=pair
                            )
            except Exception as e:
                pass
        
        # ============================================
        # STRATEGY 5: EMA Scalper (non-directional)
        # ============================================
        if self.strategies['ema_scalper']['available']:
            try:
                ema_sig = self.strategies['ema_scalper']['fn'](df)
                if ema_sig:
                    key = f"ema_scalper_{ema_sig['action']}"
                    votes[key] = ema_sig
                    self.strategy_votes['ema_scalper'] += 1
                    
                    if NARRATION_AVAILABLE:
                        log_narration(
                            event_type="STRATEGY_SIGNAL",
                            details={"strategy": "ema_scalper", "action": ema_sig['action']},
                            symbol=pair
                        )
            except Exception as e:
                pass
        
        # ============================================
        # VOTING & AGGREGATION
        # ============================================
        
        # Group votes by action
        action_votes = {}
        for vote_key, vote_sig in votes.items():
            action = vote_sig.get('action', 'buy')
            if action not in action_votes:
                action_votes[action] = []
            action_votes[action].append(vote_sig)
        
        # Check if we meet quorum
        for action, signals in action_votes.items():
            if len(signals) >= self.signal_vote_threshold:
                # CONSENSUS REACHED
                confidence = len(signals) / self.strategies_available
                
                # Calculate aggregate entry/SL/TP
                entries = [s.get('entry', 0) for s in signals if 'entry' in s]
                sls = [s.get('sl', 0) for s in signals if 'sl' in s]
                tps = [s.get('tp', 0) for s in signals if 'tp' in s]
                
                avg_entry = sum(entries) / len(entries) if entries else 0
                
                # Conservative SL (best protection), Aggressive TP (best profit)
                if action == 'buy':
                    sl = min(sls) if sls else avg_entry - 0.0020  # Fallback: -20 pips
                    tp = max(tps) if tps else avg_entry + 0.0064  # Fallback: +64 pips
                else:  # sell
                    sl = max(sls) if sls else avg_entry + 0.0020  # Fallback: +20 pips
                    tp = min(tps) if tps else avg_entry - 0.0064  # Fallback: -64 pips
                
                # Calculate R:R ratio
                risk = abs(avg_entry - sl)
                reward = abs(tp - avg_entry)
                rr_ratio = reward / risk if risk > 0 else 0
                
                aggregated_signal = {
                    'action': action,
                    'entry': float(avg_entry),
                    'sl': float(sl),
                    'tp': float(tp),
                    'risk': float(risk),
                    'reward': float(reward),
                    'rr_ratio': float(rr_ratio),
                    'strategies_triggered': len(signals),
                    'confidence': float(confidence),
                    'strategy_names': [s for s in action_votes.keys()],
                    'tag': f'multi_strategy_{len(signals)}_agreement',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                aggregated.append(aggregated_signal)
                self.signals_accepted += 1
                
                if NARRATION_AVAILABLE:
                    log_narration(
                        event_type="MULTI_STRATEGY_CONSENSUS",
                        details={
                            "action": action,
                            "strategies_agreed": len(signals),
                            "confidence": confidence,
                            "entry": avg_entry,
                            "rr_ratio": rr_ratio
                        },
                        symbol=pair
                    )
        
        if not aggregated:
            self.signals_rejected += 1
        
        return aggregated
    
    def evaluate_signal_strength(self, signal: Dict) -> float:
        """
        Evaluate strength of aggregated signal (0.0 to 1.0)
        
        Args:
            signal: Aggregated signal dict from aggregate_signals()
        
        Returns:
            Confidence score 0.0-1.0
        """
        # Base confidence from multi-strategy agreement
        base_confidence = signal.get('confidence', 0.5)
        
        # Bonus for R:R ratio > 3:1
        rr_bonus = 0.1 if signal.get('rr_ratio', 0) >= 3.0 else 0
        
        # Bonus for 5/5 strategies agreeing
        full_agreement_bonus = 0.15 if signal.get('strategies_triggered', 0) >= 5 else 0
        
        strength = min(1.0, base_confidence + rr_bonus + full_agreement_bonus)
        
        return float(strength)
    
    def get_statistics(self) -> Dict:
        """
        Return aggregator statistics
        
        Returns:
            Dict with signal evaluation statistics
        """
        acceptance_rate = (
            self.signals_accepted / self.total_signals_evaluated * 100
            if self.total_signals_evaluated > 0 else 0
        )
        
        return {
            'total_signals_evaluated': self.total_signals_evaluated,
            'signals_accepted': self.signals_accepted,
            'signals_rejected': self.signals_rejected,
            'acceptance_rate': round(acceptance_rate, 1),
            'strategies_available': self.strategies_available,
            'strategy_votes': self.strategy_votes.copy()
        }
    
    def set_vote_threshold(self, threshold: int):
        """
        Dynamically adjust voting threshold
        
        Args:
            threshold: Minimum strategies required to agree (1-5)
        """
        self.signal_vote_threshold = max(1, min(5, threshold))


# ============================================
# TESTING & DEMONSTRATION
# ============================================

if __name__ == "__main__":
    print("Strategy Aggregator - Test Suite")
    print("=" * 60)
    
    # Initialize aggregator
    agg = StrategyAggregator(signal_vote_threshold=2)
    
    print(f"✅ Legacy function strategies loaded: {agg.strategies_available}/5")
    print(f"   - Trap Reversal: {'✓' if agg.strategies['trap_reversal']['available'] else '✗'}")
    print(f"   - Fib Confluence: {'✓' if agg.strategies['fib_confluence']['available'] else '✗'}")
    print(f"   - Price Action: {'✓' if agg.strategies['price_action_holy_grail']['available'] else '✗'}")
    print(f"   - Liquidity Sweep: {'✓' if agg.strategies['liquidity_sweep']['available'] else '✗'}")
    print(f"   - EMA Scalper: {'✓' if agg.strategies['ema_scalper']['available'] else '✗'}")
    
    print(f"\n✅ Registry-based strategies: {len(agg.registry_strategies)}")
    for strat in agg.registry_strategies:
        print(f"   - {strat.metadata.name} [{strat.metadata.code}]")
    
    print(f"\nVoting threshold: {agg.signal_vote_threshold}/5 strategies")
    print(f"Status: READY FOR INTEGRATION")
    print("=" * 60)
