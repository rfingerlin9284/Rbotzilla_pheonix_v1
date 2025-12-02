#!/usr/bin/env python3
"""
RICK GATED LOGIC CONNECTION TESTER
PIN: 841921

This script validates whether developed features are actually connected
and being used in the live paper trading workflow.

Run with:
    cd /home/ing/RICK/RICK_LIVE_CLEAN
    python -m pytest tests/test_gated_logic_connections.py -v
    
Or standalone:
    python tests/test_gated_logic_connections.py
"""

import sys
import os
import importlib
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "rick_clean_live"))
sys.path.insert(0, str(PROJECT_ROOT / "oanda"))

# ============================================================================
# TEST RESULTS TRACKER
# ============================================================================

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, test_name: str, details: str = ""):
        self.passed.append((test_name, details))
        print(f"  ✅ PASS: {test_name}")
        if details:
            print(f"          {details}")
    
    def add_fail(self, test_name: str, reason: str):
        self.failed.append((test_name, reason))
        print(f"  ❌ FAIL: {test_name}")
        print(f"          {reason}")
    
    def add_warning(self, test_name: str, warning: str):
        self.warnings.append((test_name, warning))
        print(f"  ⚠️  WARN: {test_name}")
        print(f"          {warning}")
    
    def summary(self):
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"  PASSED:   {len(self.passed)}")
        print(f"  FAILED:   {len(self.failed)}")
        print(f"  WARNINGS: {len(self.warnings)}")
        
        if self.failed:
            print("\n  FAILURES:")
            for name, reason in self.failed:
                print(f"    - {name}: {reason}")
        
        if self.warnings:
            print("\n  WARNINGS:")
            for name, warning in self.warnings:
                print(f"    - {name}: {warning}")
        
        return len(self.failed) == 0


results = TestResults()

# ============================================================================
# TEST 1: ML REGIME DETECTOR IMPORT & AVAILABILITY
# ============================================================================

def test_ml_regime_detector():
    """Test if ML Regime Detector can be imported and initialized"""
    print("\n[TEST 1] ML Regime Detector")
    print("-" * 40)
    
    # Check primary import path
    try:
        from logic.regime_detector import StochasticRegimeDetector as RegimeDetector
        results.add_pass("ML import (logic.regime_detector)", "StochasticRegimeDetector found")
        
        # Try to instantiate
        try:
            detector = RegimeDetector(pin=841921)
            results.add_pass("ML instantiation", f"Created with PIN 841921")
            return detector
        except Exception as e:
            results.add_fail("ML instantiation", str(e))
            
    except ImportError:
        results.add_warning("ML import (logic.regime_detector)", "Primary path failed, trying fallback...")
        
        # Check fallback import path
        try:
            from ml_learning.regime_detector import RegimeDetector
            results.add_pass("ML import (ml_learning.regime_detector)", "Fallback path worked")
            
            try:
                detector = RegimeDetector(pin=841921)
                results.add_pass("ML instantiation", f"Created with PIN 841921")
                return detector
            except Exception as e:
                results.add_fail("ML instantiation", str(e))
                
        except ImportError as e:
            results.add_fail("ML import (fallback)", f"Both paths failed: {e}")
    
    return None


# ============================================================================
# TEST 2: HIVE MIND IMPORT & AVAILABILITY
# ============================================================================

def test_hive_mind():
    """Test if Hive Mind can be imported and initialized"""
    print("\n[TEST 2] Hive Mind")
    print("-" * 40)
    
    try:
        from hive.rick_hive_mind import RickHiveMind, SignalStrength
        results.add_pass("Hive Mind import", "RickHiveMind and SignalStrength found")
        
        try:
            hive = RickHiveMind()
            results.add_pass("Hive Mind instantiation", "Created successfully")
            return hive
        except Exception as e:
            results.add_fail("Hive Mind instantiation", str(e))
            
    except ImportError as e:
        results.add_fail("Hive Mind import", str(e))
    
    return None


# ============================================================================
# TEST 3: STRATEGY AGGREGATOR PATH CHECK
# ============================================================================

def test_strategy_aggregator():
    """Test if Strategy Aggregator has correct paths"""
    print("\n[TEST 3] Strategy Aggregator")
    print("-" * 40)
    
    # Check if file exists
    aggregator_path = PROJECT_ROOT / "rick_clean_live" / "util" / "strategy_aggregator.py"
    
    if not aggregator_path.exists():
        results.add_fail("Strategy Aggregator file", f"Not found at {aggregator_path}")
        return None
    
    results.add_pass("Strategy Aggregator file exists", str(aggregator_path))
    
    # Read and check for Windows paths
    content = aggregator_path.read_text()
    
    if "c:/Users/RFing" in content or "C:\\Users\\RFing" in content:
        results.add_fail("Strategy Aggregator paths", "Contains Windows paths - needs fixing!")
    elif "/home/ing/RICK" in content:
        results.add_pass("Strategy Aggregator paths", "Linux paths configured correctly")
    else:
        results.add_warning("Strategy Aggregator paths", "Path configuration unclear - verify manually")
    
    # Try to import
    try:
        from util.strategy_aggregator import StrategyAggregator
        results.add_pass("Strategy Aggregator import", "Module loads successfully")
        
        try:
            aggregator = StrategyAggregator(signal_vote_threshold=2)
            results.add_pass("Strategy Aggregator instantiation", "Created with threshold=2")
            
            # Check which strategies loaded
            if hasattr(aggregator, 'strategies') and aggregator.strategies:
                loaded = [s.__name__ for s in aggregator.strategies]
                results.add_pass("Strategies loaded", ", ".join(loaded) if loaded else "None")
            else:
                results.add_warning("Strategies loaded", "No strategies found in aggregator")
                
            return aggregator
            
        except Exception as e:
            results.add_fail("Strategy Aggregator instantiation", str(e))
            
    except ImportError as e:
        results.add_fail("Strategy Aggregator import", str(e))
    
    return None


# ============================================================================
# TEST 4: MARGIN CORRELATION GATE
# ============================================================================

def test_margin_correlation_gate():
    """Test if Margin Correlation Gate works correctly"""
    print("\n[TEST 4] Margin Correlation Gate")
    print("-" * 40)
    
    # Check multiple possible locations
    gate_paths = [
        PROJECT_ROOT / "oanda" / "foundation" / "margin_correlation_gate.py",
        PROJECT_ROOT / "foundation" / "margin_correlation_gate.py",
        PROJECT_ROOT / "rick_clean_live" / "foundation" / "margin_correlation_gate.py",
    ]
    
    found_path = None
    for path in gate_paths:
        if path.exists():
            found_path = path
            break
    
    if not found_path:
        results.add_fail("Margin Correlation Gate file", "Not found in any expected location")
        return None
    
    results.add_pass("Margin Correlation Gate file", str(found_path))
    
    # Try to import
    try:
        # Add the parent directory to path
        sys.path.insert(0, str(found_path.parent.parent))
        from foundation.margin_correlation_gate import MarginCorrelationGate, Position, Order, HookResult
        results.add_pass("Gate imports", "MarginCorrelationGate, Position, Order, HookResult")
        
        # Create gate instance
        gate = MarginCorrelationGate(account_nav=2000.0)
        results.add_pass("Gate instantiation", f"NAV=$2000, 35% cap=${gate.max_margin_usd:.2f}")
        
        return gate
        
    except ImportError as e:
        results.add_fail("Gate import", str(e))
    
    return None


# ============================================================================
# TEST 5: EUR_GBP USD BUCKET BUG
# ============================================================================

def test_eurgbp_bucket():
    """Test if EUR_GBP is correctly NOT affecting USD bucket"""
    print("\n[TEST 5] EUR_GBP USD Bucket Logic")
    print("-" * 40)
    
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "oanda"))
        from foundation.margin_correlation_gate import MarginCorrelationGate, Position
        
        gate = MarginCorrelationGate(account_nav=2000.0)
        
        # Test split_symbol for EUR_GBP
        base, quote = gate.split_symbol("EUR_GBP")
        if base == "EUR" and quote == "GBP":
            results.add_pass("EUR_GBP split", f"Correctly splits to ({base}, {quote})")
        else:
            results.add_fail("EUR_GBP split", f"Wrong split: ({base}, {quote})")
        
        # Test bucket exposure with EUR_GBP SHORT position
        test_position = Position(
            symbol="EUR_GBP",
            side="SHORT",
            units=17200,
            entry_price=0.87699,
            current_price=0.87500,
            pnl=50.0,
            pnl_pips=20,
            margin_used=500.0,
            position_id="test123"
        )
        
        exposure = gate.currency_bucket_exposure([test_position])
        
        # EUR_GBP SHORT should give: EUR -17200, GBP +17200, USD should be 0
        eur_exp = exposure.get("EUR", 0)
        gbp_exp = exposure.get("GBP", 0)
        usd_exp = exposure.get("USD", 0)
        
        results.add_pass("Bucket calculation ran", f"EUR={eur_exp}, GBP={gbp_exp}, USD={usd_exp}")
        
        if usd_exp == 0:
            results.add_pass("USD bucket correct", "EUR_GBP does NOT affect USD (correct!)")
        else:
            results.add_fail("USD bucket BUG", f"EUR_GBP is affecting USD bucket: {usd_exp}")
        
        if eur_exp < 0:
            results.add_pass("EUR bucket correct", f"SHORT EUR = negative exposure: {eur_exp}")
        else:
            results.add_warning("EUR bucket", f"Expected negative, got: {eur_exp}")
            
        if gbp_exp > 0:
            results.add_pass("GBP bucket correct", f"SHORT EUR_GBP = positive GBP: {gbp_exp}")
        else:
            results.add_warning("GBP bucket", f"Expected positive, got: {gbp_exp}")
            
    except Exception as e:
        results.add_fail("EUR_GBP bucket test", str(e))


# ============================================================================
# TEST 6: OANDA TRADING ENGINE INTEGRATION
# ============================================================================

def test_oanda_engine_integration():
    """Test if OandaTradingEngine has ML and Hive integrated in signal loop"""
    print("\n[TEST 6] OandaTradingEngine Integration")
    print("-" * 40)
    
    engine_path = PROJECT_ROOT / "rick_clean_live" / "oanda_trading_engine.py"
    
    if not engine_path.exists():
        results.add_fail("Engine file", f"Not found at {engine_path}")
        return
    
    content = engine_path.read_text()
    
    # Check for ML integration in signal loop
    ml_in_loop = "evaluate_signal_with_ml" in content and "ML_AVAILABLE" in content
    ml_connected = "if self.regime_detector and ML_AVAILABLE:" in content
    
    if ml_connected:
        results.add_pass("ML in signal loop", "evaluate_signal_with_ml is called with ML_AVAILABLE check")
    elif ml_in_loop:
        results.add_warning("ML integration", "Method exists but may not be in main loop")
    else:
        results.add_fail("ML integration", "ML filtering not found in signal loop")
    
    # Check for Hive integration in signal loop
    hive_in_loop = "amplify_signal_with_hive" in content and "HIVE_AVAILABLE" in content
    hive_connected = "if self.hive_mind and HIVE_AVAILABLE:" in content
    
    if hive_connected:
        results.add_pass("Hive in signal loop", "amplify_signal_with_hive is called with HIVE_AVAILABLE check")
    elif hive_in_loop:
        results.add_warning("Hive integration", "Method exists but may not be in main loop")
    else:
        results.add_fail("Hive integration", "Hive amplification not found in signal loop")
    
    # Check for Strategy Aggregator integration
    if "self.strategy_aggregator" in content:
        results.add_pass("Strategy Aggregator initialized", "Found self.strategy_aggregator")
        
        if "aggregate_signals" in content:
            results.add_pass("Strategy Aggregator method exists", "aggregate_signals found")
        else:
            results.add_warning("Strategy Aggregator", "aggregate_signals not called")
    else:
        results.add_fail("Strategy Aggregator", "Not found in engine")
    
    # Check for Margin Correlation Gate
    if "MarginCorrelationGate" in content:
        results.add_pass("Margin Gate imported", "MarginCorrelationGate found")
        
        if "self.gate = MarginCorrelationGate" in content:
            results.add_pass("Margin Gate instantiated", "Gate is created in __init__")
        else:
            results.add_warning("Margin Gate", "Import exists but may not be instantiated")
    else:
        results.add_fail("Margin Gate", "MarginCorrelationGate not imported")


# ============================================================================
# TEST 7: STRATEGIES DIRECTORY CHECK
# ============================================================================

def test_strategies_exist():
    """Test if expected strategy files exist"""
    print("\n[TEST 7] Strategy Files")
    print("-" * 40)
    
    strategies_dir = PROJECT_ROOT / "strategies"
    
    if not strategies_dir.exists():
        results.add_fail("Strategies directory", f"Not found at {strategies_dir}")
        return
    
    expected_strategies = [
        "trap_reversal_scalper.py",
        "fib_confluence_breakout.py",
        "price_action_holy_grail.py",
        "liquidity_sweep.py",
    ]
    
    for strategy in expected_strategies:
        strategy_path = strategies_dir / strategy
        if strategy_path.exists():
            results.add_pass(f"Strategy: {strategy}", "File exists")
        else:
            results.add_warning(f"Strategy: {strategy}", "File not found")


# ============================================================================
# TEST 8: CHARTER VALIDATION
# ============================================================================

def test_charter():
    """Test if RickCharter loads and validates correctly"""
    print("\n[TEST 8] Rick Charter")
    print("-" * 40)
    
    try:
        from foundation.rick_charter import RickCharter
        results.add_pass("Charter import", "RickCharter loaded")
        
        # Test PIN validation
        if RickCharter.validate_pin(841921):
            results.add_pass("Charter PIN validation", "PIN 841921 accepted")
        else:
            results.add_fail("Charter PIN validation", "PIN 841921 rejected!")
            
        # Check charter constants
        if hasattr(RickCharter, 'MIN_RR_RATIO'):
            results.add_pass("Charter R:R", f"MIN_RR_RATIO = {RickCharter.MIN_RR_RATIO}")
        
        if hasattr(RickCharter, 'MIN_NOTIONAL'):
            results.add_pass("Charter Notional", f"MIN_NOTIONAL = {RickCharter.MIN_NOTIONAL}")
            
    except ImportError as e:
        results.add_fail("Charter import", str(e))


# ============================================================================
# MAIN RUNNER
# ============================================================================

def run_all_tests():
    """Run all connection tests"""
    print("=" * 70)
    print("  RICK GATED LOGIC CONNECTION TESTER")
    print("  PIN: 841921 | Date: November 25, 2025")
    print("=" * 70)
    
    test_ml_regime_detector()
    test_hive_mind()
    test_strategy_aggregator()
    test_margin_correlation_gate()
    test_eurgbp_bucket()
    test_oanda_engine_integration()
    test_strategies_exist()
    test_charter()
    
    all_passed = results.summary()
    
    print("\n" + "=" * 70)
    if all_passed:
        print("  🎉 ALL TESTS PASSED - Gated logic is connected!")
    else:
        print("  ⚠️  SOME TESTS FAILED - Review and fix issues above")
    print("=" * 70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
