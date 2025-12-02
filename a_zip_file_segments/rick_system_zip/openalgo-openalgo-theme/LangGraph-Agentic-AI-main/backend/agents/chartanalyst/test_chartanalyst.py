#!/usr/bin/env python3
"""
Test script for ChartAnalyst
Run individual tests or comprehensive analysis
"""

import asyncio
import json
import os
import sys
from typing import List, Dict
import pandas as pd
from datetime import datetime

# Add the parent directory to path if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chartanalyst_main import ChartAnalyst, TechnicalSignal, PatternDetector, MarketDataProvider

class ChartAnalystTester:
    """Test suite for ChartAnalyst functionality"""
    
    def __init__(self):
        self.analyst = ChartAnalyst()
        self.pattern_detector = PatternDetector()
        self.data_provider = MarketDataProvider()
        
    def test_data_fetching(self, symbols: List[str]) -> Dict[str, bool]:
        """Test data fetching from different sources"""
        results = {}
        print("\n?? Testing Data Fetching...")
        
        for symbol in symbols:
            try:
                print(f"  Testing {symbol}...")
                df = self.data_provider.get_market_data(symbol, "1h")
                
                if not df.empty:
                    print(f"    ✅ {symbol}: {len(df)} candles fetched")
                    print(f"    ?? Latest close: {df['close'].iloc[-1]:.2f}")
                    results[symbol] = True
                else:
                    print(f"    ❌ {symbol}: No data received")
                    results[symbol] = False
                    
            except Exception as e:
                print(f"    ❌ {symbol}: Error - {e}")
                results[symbol] = False
        
        return results
    
    def test_pattern_detection(self, symbol: str = "BTCUSDT") -> bool:
        """Test pattern detection algorithms"""
        print(f"\n?? Testing Pattern Detection for {symbol}...")
        
        try:
            df = self.data_provider.get_market_data(symbol, "1h")
            if df.empty:
                print("  ❌ No data available for pattern testing")
                return False
            
            # Test candlestick patterns
            candlestick_patterns = self.pattern_detector.detect_candlestick_patterns(df)
            print(f"  ?? Detected {len(candlestick_patterns)} candlestick patterns")
            for pattern, signal in candlestick_patterns.items():
                print(f"    {pattern}: {signal}")
            
            # Test support/resistance
            support, resistance = self.pattern_detector.detect_support_resistance(df)
            print(f"  ?? Support levels: {support}")
            print(f"  ?? Resistance levels: {resistance}")
            
            # Test chart patterns
            chart_patterns = self.pattern_detector.detect_chart_patterns(df)
            print(f"  ?? Chart patterns: {chart_patterns}")
            
            # Test trend detection
            trend = self.pattern_detector.determine_trend(df)
            print(f"  ?? Current trend: {trend}")
            
            # Test volatility
            volatility = self.pattern_detector.calculate_volatility(df)
            print(f"  ?? Volatility regime: {volatility}")
            
            print("  ✅ Pattern detection tests completed successfully")
            return True
            
        except Exception as e:
            print(f"  ❌ Pattern detection failed: {e}")
            return False
    
    def test_signal_generation(self, symbols: List[str]) -> Dict[str, TechnicalSignal]:
        """Test complete signal generation"""
        print("\n?? Testing Signal Generation...")
        signals = {}
        
        for symbol in symbols:
            try:
                print(f"  Generating signal for {symbol}...")
                signal = self.analyst.analyze_symbol(symbol, "1h")
                
                if signal:
                    print(f"    ✅ Signal generated: {signal.pattern} ({signal.confidence}%)")
                    print(f"    ?? Trend: {signal.trend}, Volatility: {signal.volatility}")
                    signals[symbol] = signal
                else:
                    print(f"    ❌ No signal generated for {symbol}")
                    
            except Exception as e:
                print(f"    ❌ Signal generation failed for {symbol}: {e}")
        
        return signals
    
    def test_redis_connection(self) -> bool:
        """Test Redis connection and publishing"""
        print("\n?? Testing Redis Connection...")
        
        if not self.analyst.redis_client:
            print("  ⚠️  Redis client not available (this is optional)")
            return False
        
        try:
            # Test connection
            self.analyst.redis_client.ping()
            print("  ✅ Redis connection successful")
            
            # Test publishing
            test_signal = TechnicalSignal(
                agent="chartanalyst",
                timestamp=datetime.utcnow().isoformat(),
                symbol="TEST",
                timeframe="1h",
                pattern="Test Pattern",
                confidence=75,
                support_zone=[100.0, 105.0],
                resistance_zone=[110.0, 115.0],
                trend="Bull",
                volatility="Medium"
            )
            
            self.analyst.publish_signal(test_signal)
            print("  ✅ Signal publishing successful")
            return True
            
        except Exception as e:
            print(f"  ❌ Redis test failed: {e}")
            return False
    
    def generate_test_report(self, signals: Dict[str, TechnicalSignal]):
        """Generate a comprehensive test report"""
        print("\n?? CHARTANALYST TEST REPORT")
        print("=" * 50)
        
        if not signals:
            print("No signals generated to report on.")
            return
        
        print(f"?? Total signals generated: {len(signals)}")
        print(f"⏰ Report time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Confidence distribution
        confidences = [signal.confidence for signal in signals.values()]
        avg_confidence = sum(confidences) / len(confidences)
        print(f"?? Average confidence: {avg_confidence:.
