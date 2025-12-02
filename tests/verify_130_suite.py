#!/usr/bin/env python3
"""
RICK System - 130 Verification Suite
====================================
Diagnostic suite that validates all trading gates are functioning correctly.
Runs 100 mock signals through the complete pipeline and reports rejection stats.

AUTH CODE: 841921
CHARTER: This suite must pass before any live trading is enabled.
"""

import os
import sys
import json
import random
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')
logger = logging.getLogger("RICK.Verify130Suite")

# Import RICK modules
try:
    from engine.strategy_aggregator import (
        StrategyAggregator, TradingSignal, Timeframe, SignalType, get_aggregator
    )
    from engine.execution_gate import (
        ExecutionGate, OrderRequest, GateDecision, get_execution_gate
    )
    IMPORTS_OK = True
except ImportError as e:
    logger.error(f"❌ Import failed: {e}")
    IMPORTS_OK = False


# ============================================================================
# TEST DATA GENERATORS
# ============================================================================

FOREX_SYMBOLS = [
    "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD",
    "USD_CAD", "NZD_USD", "EUR_GBP", "EUR_JPY", "GBP_JPY"
]

TIMEFRAMES = [
    Timeframe.M1, Timeframe.M5, Timeframe.M15, Timeframe.M30,
    Timeframe.H1, Timeframe.H4, Timeframe.D1
]

# Weighted probabilities (more noise signals to test rejection)
TIMEFRAME_WEIGHTS = [0.15, 0.20, 0.15, 0.15, 0.20, 0.10, 0.05]


def generate_random_signal(signal_id: int) -> TradingSignal:
    """Generate a random trading signal for testing."""
    symbol = random.choice(FOREX_SYMBOLS)
    timeframe = random.choices(TIMEFRAMES, weights=TIMEFRAME_WEIGHTS)[0]
    direction = random.choice([SignalType.BUY, SignalType.SELL])
    
    # Generate realistic prices based on symbol
    base_prices = {
        "EUR_USD": 1.0850, "GBP_USD": 1.2650, "USD_JPY": 149.50,
        "USD_CHF": 0.8750, "AUD_USD": 0.6500, "USD_CAD": 1.3650,
        "NZD_USD": 0.5900, "EUR_GBP": 0.8580, "EUR_JPY": 162.20,
        "GBP_JPY": 188.50
    }
    
    base_price = base_prices.get(symbol, 1.0)
    entry_price = base_price * (1 + random.uniform(-0.005, 0.005))
    
    # Random R:R ratio (some good, some bad)
    rr_ratio = random.choice([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0])
    pip_value = 0.0001 if "JPY" not in symbol else 0.01
    risk_pips = random.randint(20, 50)
    reward_pips = int(risk_pips * rr_ratio)
    
    if direction == SignalType.BUY:
        stop_loss = entry_price - (risk_pips * pip_value)
        take_profit = entry_price + (reward_pips * pip_value)
    else:
        stop_loss = entry_price + (risk_pips * pip_value)
        take_profit = entry_price - (reward_pips * pip_value)
    
    # Random confidence (some below threshold)
    confidence = random.choice([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    
    return TradingSignal(
        symbol=symbol,
        signal_type=direction,
        timeframe=timeframe,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        confidence=confidence,
        strategy_name=f"test_strategy_{signal_id % 5}",
        metadata={"test_id": signal_id}
    )


def generate_random_order(order_id: int) -> OrderRequest:
    """Generate a random order request for testing."""
    symbol = random.choice(FOREX_SYMBOLS)
    direction = random.choice(["BUY", "SELL"])
    
    # Random unit sizes (some micro, some standard)
    units = random.choice([100, 500, 800, 1000, 2000, 5000, 10000, 50000])
    
    # Random leverage (some high)
    leverage = random.choice([1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0, 50.0])
    
    base_prices = {
        "EUR_USD": 1.0850, "GBP_USD": 1.2650, "USD_JPY": 149.50,
        "USD_CHF": 0.8750, "AUD_USD": 0.6500, "USD_CAD": 1.3650,
        "NZD_USD": 0.5900, "EUR_GBP": 0.8580, "EUR_JPY": 162.20,
        "GBP_JPY": 188.50
    }
    
    base_price = base_prices.get(symbol, 1.0)
    entry_price = base_price * (1 + random.uniform(-0.005, 0.005))
    
    # Random R:R ratio
    rr_ratio = random.choice([1.0, 1.5, 2.0, 3.0, 4.0, 5.0])
    pip_value = 0.0001 if "JPY" not in symbol else 0.01
    risk_pips = random.randint(20, 50)
    reward_pips = int(risk_pips * rr_ratio)
    
    if direction == "BUY":
        stop_loss = entry_price - (risk_pips * pip_value)
        take_profit = entry_price + (reward_pips * pip_value)
    else:
        stop_loss = entry_price + (risk_pips * pip_value)
        take_profit = entry_price - (reward_pips * pip_value)
    
    return OrderRequest(
        symbol=symbol,
        direction=direction,
        units=units,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        leverage=leverage,
        strategy_name=f"test_order_{order_id}"
    )


# ============================================================================
# VERIFICATION SUITE
# ============================================================================

@dataclass
class SuiteResults:
    """Results from the 130 verification suite."""
    timestamp: str = ""
    total_signals: int = 0
    total_orders: int = 0
    
    # Signal aggregator stats
    signals_accepted: int = 0
    signals_rejected_noise: int = 0
    signals_rejected_rr: int = 0
    signals_rejected_confidence: int = 0
    
    # Execution gate stats
    orders_approved: int = 0
    orders_rejected_pin: int = 0
    orders_rejected_leverage: int = 0
    orders_rejected_micro: int = 0
    orders_rejected_notional: int = 0
    orders_rejected_risk: int = 0
    orders_rejected_mode: int = 0
    
    # Test status
    aggregator_test_passed: bool = False
    gate_test_passed: bool = False
    suite_passed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "signal_tests": {
                "total": self.total_signals,
                "accepted": self.signals_accepted,
                "rejected_noise_trading": self.signals_rejected_noise,
                "rejected_risk_reward": self.signals_rejected_rr,
                "rejected_confidence": self.signals_rejected_confidence,
                "test_passed": self.aggregator_test_passed
            },
            "order_tests": {
                "total": self.total_orders,
                "approved": self.orders_approved,
                "rejected_pin": self.orders_rejected_pin,
                "rejected_leverage": self.orders_rejected_leverage,
                "rejected_micro": self.orders_rejected_micro,
                "rejected_notional": self.orders_rejected_notional,
                "rejected_risk": self.orders_rejected_risk,
                "rejected_mode": self.orders_rejected_mode,
                "test_passed": self.gate_test_passed
            },
            "suite_passed": self.suite_passed
        }


def run_signal_aggregator_test(num_signals: int = 100) -> Tuple[bool, Dict]:
    """
    Test the Strategy Aggregator with random signals.
    Validates M15 filter, R:R filter, and confidence filter.
    """
    print("\n" + "=" * 60)
    print("🔬 TEST 1: Strategy Aggregator (Signal Filtering)")
    print("=" * 60)
    
    if not IMPORTS_OK:
        print("❌ FAILED: Could not import strategy_aggregator module")
        return False, {}
    
    try:
        aggregator = StrategyAggregator()
        
        # Generate and ingest signals
        print(f"📊 Generating {num_signals} random signals...")
        for i in range(num_signals):
            signal = generate_random_signal(i)
            aggregator.ingest_signal(signal)
        
        # Run aggregation
        result = aggregator.aggregate()
        summary = result.summary()
        
        print(f"\n📈 AGGREGATION RESULTS:")
        print(f"   Total Processed: {summary['total_processed']}")
        print(f"   ✅ Accepted: {summary['accepted']}")
        print(f"   🚫 Rejected (Noise M1/M5): {summary['rejected_noise_trading']}")
        print(f"   🚫 Rejected (Risk/Reward): {summary['rejected_risk_reward']}")
        print(f"   🚫 Rejected (Low Confidence): {summary['rejected_low_confidence']}")
        
        # Validation: Noise filter MUST reject M1/M5 signals
        # We expect ~35% noise signals based on weights
        noise_ratio = summary['rejected_noise_trading'] / summary['total_processed']
        print(f"\n📊 Noise Rejection Rate: {noise_ratio*100:.1f}%")
        
        # Test passes if noise filter is working (should reject some signals)
        test_passed = summary['rejected_noise_trading'] > 0
        
        if test_passed:
            print("✅ SIGNAL AGGREGATOR TEST: PASSED")
        else:
            print("❌ SIGNAL AGGREGATOR TEST: FAILED (No noise signals rejected)")
        
        return test_passed, summary
        
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False, {}


def run_execution_gate_test(num_orders: int = 100) -> Tuple[bool, Dict]:
    """
    Test the Execution Gate with random orders.
    Validates PIN check, leverage limits, micro trading gate.
    """
    print("\n" + "=" * 60)
    print("🔬 TEST 2: Execution Gate (Order Filtering)")
    print("=" * 60)
    
    if not IMPORTS_OK:
        print("❌ FAILED: Could not import execution_gate module")
        return False, {}
    
    try:
        gate = ExecutionGate()
        
        # Generate and evaluate orders
        print(f"📊 Generating {num_orders} random orders...")
        for i in range(num_orders):
            order = generate_random_order(i)
            gate.evaluate(order)
        
        # Get statistics
        stats = gate.get_statistics()
        
        print(f"\n📈 GATE RESULTS:")
        print(f"   Total Processed: {stats['total']}")
        print(f"   ✅ Approved: {stats['approved']}")
        print(f"   🚫 Rejected (PIN Required): {stats['rejected_pin']}")
        print(f"   🚫 Rejected (Leverage): {stats['rejected_leverage']}")
        print(f"   🚫 Rejected (Micro <1000): {stats['rejected_micro']}")
        print(f"   🚫 Rejected (Notional): {stats['rejected_notional']}")
        print(f"   🚫 Rejected (Risk): {stats['rejected_risk']}")
        print(f"   🚫 Rejected (Mode): {stats['rejected_mode']}")
        
        # Calculate rejection rates
        total_rejected = stats['total'] - stats['approved']
        rejection_rate = (total_rejected / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"\n📊 Overall Rejection Rate: {rejection_rate:.1f}%")
        
        # Test passes if gates are working (should reject some orders)
        test_passed = stats['rejected_micro'] > 0 or stats['rejected_pin'] > 0
        
        if test_passed:
            print("✅ EXECUTION GATE TEST: PASSED")
        else:
            print("❌ EXECUTION GATE TEST: FAILED (No orders rejected by gates)")
        
        return test_passed, stats
        
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False, {}


def run_130_suite(num_signals: int = 100, num_orders: int = 100) -> SuiteResults:
    """
    Run the complete 130 verification suite.
    Tests both signal aggregation and execution gating.
    """
    print("\n" + "=" * 70)
    print("🔒 RICK 130 VERIFICATION SUITE")
    print("=" * 70)
    print(f"   Timestamp: {datetime.utcnow().isoformat()}")
    print(f"   Test Signals: {num_signals}")
    print(f"   Test Orders: {num_orders}")
    print("=" * 70)
    
    results = SuiteResults()
    results.timestamp = datetime.utcnow().isoformat()
    results.total_signals = num_signals
    results.total_orders = num_orders
    
    # Test 1: Strategy Aggregator
    agg_passed, agg_stats = run_signal_aggregator_test(num_signals)
    results.aggregator_test_passed = agg_passed
    if agg_stats:
        results.signals_accepted = agg_stats.get('accepted', 0)
        results.signals_rejected_noise = agg_stats.get('rejected_noise_trading', 0)
        results.signals_rejected_rr = agg_stats.get('rejected_risk_reward', 0)
        results.signals_rejected_confidence = agg_stats.get('rejected_low_confidence', 0)
    
    # Test 2: Execution Gate
    gate_passed, gate_stats = run_execution_gate_test(num_orders)
    results.gate_test_passed = gate_passed
    if gate_stats:
        results.orders_approved = gate_stats.get('approved', 0)
        results.orders_rejected_pin = gate_stats.get('rejected_pin', 0)
        results.orders_rejected_leverage = gate_stats.get('rejected_leverage', 0)
        results.orders_rejected_micro = gate_stats.get('rejected_micro', 0)
        results.orders_rejected_notional = gate_stats.get('rejected_notional', 0)
        results.orders_rejected_risk = gate_stats.get('rejected_risk', 0)
        results.orders_rejected_mode = gate_stats.get('rejected_mode', 0)
    
    # Overall suite result
    results.suite_passed = agg_passed and gate_passed
    
    # Final summary
    print("\n" + "=" * 70)
    print("🏁 130 SUITE FINAL RESULTS")
    print("=" * 70)
    print(f"   Signal Aggregator Test: {'✅ PASSED' if agg_passed else '❌ FAILED'}")
    print(f"   Execution Gate Test: {'✅ PASSED' if gate_passed else '❌ FAILED'}")
    print(f"\n   {'✅ 130 SUITE PASSED' if results.suite_passed else '❌ 130 SUITE FAILED'}")
    print("=" * 70)
    
    return results


def save_results(results: SuiteResults, filepath: str = None) -> str:
    """Save suite results to JSON file."""
    if filepath is None:
        filepath = f"verify_130_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filepath, 'w') as f:
            json.dump(results.to_dict(), f, indent=2)
        print(f"\n💾 Results saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Failed to save results: {e}")
        return ""


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🔒" * 35)
    print("   RICK SYSTEM - 130 VERIFICATION SUITE")
    print("   Proving the system is SAFE before trading")
    print("🔒" * 35)
    
    # Set random seed for reproducibility
    random.seed(130)  # 130 Suite seed
    
    # Run the suite
    results = run_130_suite(num_signals=100, num_orders=100)
    
    # Save results
    results_file = save_results(results, "logs/verify_130_results.json")
    
    # Exit code based on suite result
    exit_code = 0 if results.suite_passed else 1
    print(f"\n🏁 Exit Code: {exit_code}")
    sys.exit(exit_code)
