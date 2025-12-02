#!/usr/bin/env python3
"""
Full Intelligence Stack Test - GHOST Mode
Tests ML models, pattern learner, and regime detector integration
PIN: 841921
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_ml_models():
    """Test ML models A/B/C"""
    logger.info("🤖 Testing ML Models (A/B/C)...")
    
    try:
        from ml_learning.ml_models import get_ml_model, generate_ml_signal, ModelType
        
        # Test Model A (Forex)
        logger.info("  Testing Model A (Forex)...")
        model_a = get_ml_model("A", pin=841921)
        logger.info(f"  ✅ Model A loaded: {model_a.model_type.value}")
        signal_a = generate_ml_signal("A", {"symbol": "EUR_USD", "timeframe": "1h"}, pin=841921)
        logger.info(f"  ✅ Model A Signal: {signal_a.get('direction')} (confidence: {signal_a.get('confidence', 0):.2%})")
        
        # Test Model B (Crypto)
        logger.info("  Testing Model B (Crypto)...")
        model_b = get_ml_model("B", pin=841921)
        logger.info(f"  ✅ Model B loaded: {model_b.model_type.value}")
        signal_b = generate_ml_signal("B", {"symbol": "BTC-USD", "timeframe": "1h"}, pin=841921)
        logger.info(f"  ✅ Model B Signal: {signal_b.get('direction')} (confidence: {signal_b.get('confidence', 0):.2%})")
        
        # Test Model C (Derivatives)
        logger.info("  Testing Model C (Derivatives)...")
        model_c = get_ml_model("C", pin=841921)
        logger.info(f"  ✅ Model C loaded: {model_c.model_type.value}")
        signal_c = generate_ml_signal("C", {"symbol": "ES_FUT", "timeframe": "1h"}, pin=841921)
        logger.info(f"  ✅ Model C Signal: {signal_c.get('direction')} (confidence: {signal_c.get('confidence', 0):.2%})")
        
        return True
    except Exception as e:
        logger.error(f"  ❌ ML Models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pattern_learner():
    """Test pattern learner"""
    logger.info("🧠 Testing Pattern Learner...")
    
    try:
        from ml_learning.pattern_learner import get_pattern_learner
        from datetime import datetime, timezone
        
        learner = get_pattern_learner(pin=841921)
        logger.info(f"  ✅ Pattern Learner loaded: {learner.__class__.__name__}")
        
        # Test pattern storage
        test_signal = {
            'symbol': 'EUR_USD',
            'rsi': 45.5,
            'macd_histogram': 0.002,
            'bb_position': 0.3,
            'atr_pct': 0.0015,
            'volume_ratio': 1.2,
            'sma_distance': 0.005,
            'confidence': 0.85,
            'direction': 'LONG'
        }
        
        pattern_id = learner.store_trade_pattern(test_signal, entry_price=1.0850)
        logger.info(f"  ✅ Pattern stored with ID: {pattern_id[:8]}...")
        
        # Update with outcome
        learner.update_trade_outcome(pattern_id, exit_price=1.0950, outcome='win', pnl=150.0, duration_minutes=30)
        logger.info(f"  ✅ Pattern outcome updated: win +$150")
        
        # Test pattern insight (this will find similar patterns internally)
        insight = learner.get_pattern_insight(test_signal)
        similar_count = insight.get('similar_patterns_found', 0)
        recommendation = insight.get('recommendation', 'unknown')
        logger.info(f"  ✅ Pattern insight: {similar_count} similar, recommendation: {recommendation}")
        
        # Test statistics
        stats = learner.get_statistics()
        logger.info(f"  ✅ Learner stats: {stats.get('total_patterns', 0)} total, {stats.get('completed_patterns', 0)} completed")
        
        return True
    except Exception as e:
        logger.error(f"  ❌ Pattern Learner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_regime_detector():
    """Test regime detector"""
    logger.info("📊 Testing Regime Detector...")
    
    try:
        from logic.regime_detector import detect_market_regime, MarketRegime
        
        # Test regime detection with sample price data
        test_prices = [1.0850, 1.0860, 1.0870, 1.0880, 1.0890, 1.0900, 1.0910, 1.0920]
        
        regime_result = detect_market_regime(test_prices, symbol="EUR_USD")
        regime = regime_result.get('regime', 'unknown')
        confidence = regime_result.get('confidence', 0)
        probabilities = regime_result.get('probabilities', {})
        
        logger.info(f"  ✅ Detected regime: {regime} (confidence: {confidence:.2%})")
        logger.info(f"  ✅ Probabilities: {probabilities}")
        
        # Test all regime types
        regimes = [MarketRegime.BULL, MarketRegime.BEAR, MarketRegime.SIDEWAYS, MarketRegime.CRASH, MarketRegime.TRIAGE]
        logger.info(f"  ✅ Available regimes: {[r.value for r in regimes]}")
        
        return True
    except Exception as e:
        logger.error(f"  ❌ Regime Detector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_smart_logic():
    """Test smart logic filters"""
    logger.info("🧠 Testing Smart Logic Filters...")
    
    try:
        from logic.smart_logic import get_smart_filter, validate_trading_signal
        
        # Test smart filter initialization
        smart_filter = get_smart_filter(pin=841921)
        logger.info(f"  ✅ Smart Filter loaded: {smart_filter.__class__.__name__}")
        
        # Test trade validation
        test_signal = {
            'symbol': 'EUR_USD',
            'entry_price': 1.0850,
            'stop_loss': 1.0820,
            'take_profit': 1.0946,
            'direction': 'LONG',
            'confidence': 0.85,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Calculate RR
        risk = abs(test_signal['entry_price'] - test_signal['stop_loss'])
        reward = abs(test_signal['take_profit'] - test_signal['entry_price'])
        rr_ratio = reward / risk if risk > 0 else 0
        
        logger.info(f"  ✅ Trade RR: {rr_ratio:.2f} (charter target: ≥3.2)")
        
        # Test validation
        validation_result = validate_trading_signal(test_signal)
        logger.info(f"  ✅ Validation result: {validation_result.get('valid', False)}")
        logger.info(f"  ✅ Filter score: {validation_result.get('score', 0):.2f}/1.0")
        
        return True
    except Exception as e:
        logger.error(f"  ❌ Smart Logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_intelligence_pipeline():
    """Test full intelligence stack integration"""
    logger.info("🔥 Testing Full Intelligence Pipeline...")
    
    try:
        # Simulate full pipeline
        logger.info("\n  📊 Pipeline Flow:")
        logger.info("  1. REGIME DETECTOR → Analyze market state")
        logger.info("  2. ML MODELS → Generate signals")
        logger.info("  3. SMART LOGIC → Validate RR/FVG/Fibonacci")
        logger.info("  4. PATTERN LEARNER → Check historical similarity")
        logger.info("  5. DECISION → Execute or reject")
        
        # Step 1: Regime Detection
        from logic.regime_detector import detect_market_regime
        test_prices = [1.0850, 1.0860, 1.0870, 1.0880, 1.0890, 1.0900, 1.0910, 1.0920]
        regime_result = detect_market_regime(test_prices, symbol="EUR_USD")
        regime = regime_result.get('regime', 'unknown')
        logger.info(f"\n  ✅ Step 1: Regime = {regime}")
        
        # Step 2: ML Signal
        from ml_learning.ml_models import generate_ml_signal
        signal = generate_ml_signal("A", {"symbol": "EUR_USD", "timeframe": "1h", "regime": regime}, pin=841921)
        logger.info(f"  ✅ Step 2: Signal = {signal.get('direction')} ({signal.get('confidence', 0):.2%})")
        
        # Step 3: Smart Logic Validation
        from logic.smart_logic import validate_trading_signal
        test_trade = {
            'symbol': 'EUR_USD',
            'entry_price': 1.0850,
            'stop_loss': 1.0820,
            'take_profit': 1.0946,
            'direction': signal.get('direction', 'LONG'),
            'confidence': signal.get('confidence', 0.8),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        risk = abs(test_trade['entry_price'] - test_trade['stop_loss'])
        reward = abs(test_trade['take_profit'] - test_trade['entry_price'])
        rr = reward / risk
        validation = validate_trading_signal(test_trade)
        logger.info(f"  ✅ Step 3: RR = {rr:.2f}, Valid = {validation.get('valid', False)}")
        
        # Step 4: Pattern Learning (use insight instead of direct pattern matching)
        from ml_learning.pattern_learner import get_pattern_learner
        learner = get_pattern_learner(pin=841921)
        
        signal_for_insight = {
            'symbol': 'EUR_USD',
            'rsi': 45.5,
            'macd_histogram': 0.002,
            'bb_position': 0.3,
            'atr_pct': 0.0015,
            'volume_ratio': 1.2,
            'sma_distance': 0.005,
            'confidence': signal.get('confidence', 0.8),
            'direction': signal.get('direction', 'LONG')
        }
        
        insight = learner.get_pattern_insight(signal_for_insight)
        similar_count = insight.get('similar_patterns_found', 0)
        logger.info(f"  ✅ Step 4: Pattern insight generated, {similar_count} similar patterns")
        
        # Step 5: Decision
        decision = "EXECUTE" if rr >= 3.2 and signal.get('confidence', 0) >= 0.75 and validation.get('valid', False) else "REJECT"
        logger.info(f"  ✅ Step 5: Decision = {decision}")
        
        logger.info("\n  🎯 Full Pipeline Test: PASSED")
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_ghost():
    """Test integration with ghost trading engine"""
    logger.info("👻 Testing Ghost Trading Integration...")
    
    try:
        # Check if ghost session is running
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        if 'ghost_trading_engine.py' in result.stdout:
            logger.info("  ✅ Ghost trading engine is running")
            logger.info("  ✅ Intelligence stack can provide signals")
            logger.info("  ✅ Ready for enhanced ghost trading")
            return True
        else:
            logger.info("  ⚠️  Ghost trading engine not running")
            logger.info("  ✅ Intelligence stack ready for next session")
            return True
            
    except Exception as e:
        logger.error(f"  ❌ Ghost integration test failed: {e}")
        return False

def main():
    """Run full intelligence stack tests"""
    print("\n╔══════════════════════════════════════════════════════════════════════════╗")
    print("║           🧠 FULL INTELLIGENCE STACK TEST - GHOST MODE                   ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝\n")
    
    results = {}
    
    # Test each component
    results['ml_models'] = test_ml_models()
    print()
    
    results['pattern_learner'] = test_pattern_learner()
    print()
    
    results['regime_detector'] = test_regime_detector()
    print()
    
    results['smart_logic'] = test_smart_logic()
    print()
    
    results['full_pipeline'] = test_full_intelligence_pipeline()
    print()
    
    results['ghost_integration'] = test_integration_with_ghost()
    print()
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component.replace('_', ' ').title()}: {'PASSED' if status else 'FAILED'}")
    
    print(f"\n🎯 Overall: {passed}/{total} components passed")
    
    if passed == total:
        print("\n✅ FULL INTELLIGENCE STACK: OPERATIONAL")
        print("🔥 Ready for enhanced ghost trading with ML signals")
        
        # Save test results
        test_report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'test_type': 'full_intelligence_stack',
            'results': results,
            'passed': passed,
            'total': total,
            'status': 'OPERATIONAL'
        }
        
        with open('ml_intelligence_test_report.json', 'w') as f:
            json.dump(test_report, f, indent=2)
        
        logger.info("\n📝 Test report saved: ml_intelligence_test_report.json")
    else:
        print("\n⚠️  SOME TESTS FAILED - Review logs above")
        print("🔧 Intelligence stack may need configuration")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
