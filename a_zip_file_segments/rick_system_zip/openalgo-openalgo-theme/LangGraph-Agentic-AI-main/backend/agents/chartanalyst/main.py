#!/usr/bin/env python3
"""
ChartAnalyst - Technical Pattern Detection Agent
Analyzes market data and detects tradeable technical patterns
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
import talib
import yfinance as yf
import redis
from binance.client import Client as BinanceClient
from binance import ThreadedWebSocketManager
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ChartAnalyst')

@dataclass
class TechnicalSignal:
    """Standardized technical signal output"""
    agent: str
    timestamp: str
    symbol: str
    timeframe: str
    pattern: str
    confidence: int
    support_zone: List[float]
    resistance_zone: List[float]
    trend: str
    volatility: str
    additional_data: Dict[str, Any] = None

class PatternDetector:
    """Core pattern detection logic using TA-Lib and custom algorithms"""
    
    def __init__(self):
        self.candlestick_patterns = [
            'CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE',
            'CDL3OUTSIDE', 'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS', 'CDLABANDONEDBABY',
            'CDLADVANCEBLOCK', 'CDLBELTHOLD', 'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU',
            'CDLCONCEALBABYSWALL', 'CDLCOUNTERATTACK', 'CDLDARKCLOUDCOVER', 'CDLDOJI',
            'CDLDOJISTAR', 'CDLDRAGONFLYDOJI', 'CDLENGULFING', 'CDLEVENINGDOJISTAR',
            'CDLEVENINGSTAR', 'CDLGAPSIDESIDEWHITE', 'CDLGRAVESTONEDOJI', 'CDLHAMMER',
            'CDLHANGINGMAN', 'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE',
            'CDLHIKKAKE', 'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON', 'CDLIDENTICAL3CROWS',
            'CDLINNECK', 'CDLINVERTEDHAMMER', 'CDLKICKING', 'CDLKICKINGBYLENGTH',
            'CDLLADDERBOTTOM', 'CDLLONGLEGGEDDOJI', 'CDLLONGLINE', 'CDLMARUBOZU',
            'CDLMATCHINGLOW', 'CDLMATHOLD', 'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR',
            'CDLONNECK', 'CDLPIERCING', 'CDLRICKSHAWMAN', 'CDLRISEFALL3METHODS',
            'CDLSEPARATINGLINES', 'CDLSHOOTINGSTAR', 'CDLSHORTLINE', 'CDLSPINNINGTOP',
            'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 'CDLTAKURI', 'CDLTASUKIGAP',
            'CDLTHRUSTING', 'CDLTRISTAR', 'CDLUNIQUE3RIVER', 'CDLUPSIDEGAP2CROWS',
            'CDLXSIDEGAP3METHODS'
        ]
    
    def detect_candlestick_patterns(self, df: pd.DataFrame) -> Dict[str, int]:
        """Detect candlestick patterns using TA-Lib"""
        patterns = {}
        open_prices = df['open'].values
        high_prices = df['high'].values
        low_prices = df['low'].values
        close_prices = df['close'].values
        
        for pattern in self.candlestick_patterns:
            try:
                pattern_func = getattr(talib, pattern)
                result = pattern_func(open_prices, high_prices, low_prices, close_prices)
                # Get the latest signal (non-zero values indicate pattern)
                latest_signal = result[-1] if len(result) > 0 else 0
                if latest_signal != 0:
                    patterns[pattern] = int(latest_signal)
            except Exception as e:
                logger.debug(f"Error detecting pattern {pattern}: {e}")
        
        return patterns
    
    def detect_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Tuple[List[float], List[float]]:
        """Detect support and resistance zones"""
        highs = df['high'].rolling(window=window).max()
        lows = df['low'].rolling(window=window).min()
        
        # Find recent pivot points
        recent_highs = highs.tail(10).unique()
        recent_lows = lows.tail(10).unique()
        
        # Filter and sort
        resistance_levels = sorted([h for h in recent_highs if not np.isnan(h)], reverse=True)[:3]
        support_levels = sorted([l for l in recent_lows if not np.isnan(l)])[:3]
        
        return support_levels, resistance_levels
    
    def detect_chart_patterns(self, df: pd.DataFrame) -> List[str]:
        """Detect geometric chart patterns"""
        patterns = []
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        
        # Simple trend detection
        if len(closes) >= 20:
            recent_closes = closes[-20:]
            slope = np.polyfit(range(len(recent_closes)), recent_closes, 1)[0]
            
            if slope > 0.01:
                patterns.append("Ascending Trend")
            elif slope < -0.01:
                patterns.append("Descending Trend")
            else:
                patterns.append("Sideways Movement")
        
        # Triangle pattern detection (simplified)
        if len(closes) >= 10:
            recent_highs = highs[-10:]
            recent_lows = lows[-10:]
            
            high_slope = np.polyfit(range(len(recent_highs)), recent_highs, 1)[0]
            low_slope = np.polyfit(range(len(recent_lows)), recent_lows, 1)[0]
            
            if abs(high_slope) < 0.005 and abs(low_slope) < 0.005:
                patterns.append("Symmetrical Triangle")
            elif high_slope < -0.01 and low_slope > 0.01:
                patterns.append("Ascending Triangle")
            elif high_slope > 0.01 and low_slope < -0.01:
                patterns.append("Descending Triangle")
        
        return patterns if patterns else ["No Clear Pattern"]
    
    def calculate_volatility(self, df: pd.DataFrame) -> str:
        """Calculate and classify volatility regime"""
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * 100  # Convert to percentage
        
        if volatility > 3.0:
            return "High"
        elif volatility > 1.5:
            return "Medium"
        else:
            return "Low"
    
    def determine_trend(self, df: pd.DataFrame) -> str:
        """Determine overall trend direction"""
        # Use multiple EMAs for trend detection
        ema_9 = talib.EMA(df['close'].values, timeperiod=9)
        ema_21 = talib.EMA(df['close'].values, timeperiod=21)
        ema_50 = talib.EMA(df['close'].values, timeperiod=50)
        
        current_price = df['close'].iloc[-1]
        current_ema9 = ema_9[-1]
        current_ema21 = ema_21[-1]
        current_ema50 = ema_50[-1]
        
        # Bull trend: price > EMA9 > EMA21 > EMA50
        if current_price > current_ema9 > current_ema21 > current_ema50:
            return "Bull"
        # Bear trend: price < EMA9 < EMA21 < EMA50
        elif current_price < current_ema9 < current_ema21 < current_ema50:
            return "Bear"
        else:
            return "Sideways"

class MarketDataProvider:
    """Handles data fetching from multiple sources"""
    
    def __init__(self):
        self.binance_client = None
        if os.getenv('BINANCE_API_KEY'):
            try:
                self.binance_client = BinanceClient(
                    api_key=os.getenv('BINANCE_API_KEY'),
                    api_secret=os.getenv('BINANCE_API_SECRET')
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Binance client: {e}")
    
    def get_crypto_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """Fetch crypto data from Binance"""
        if not self.binance_client:
            logger.error("Binance client not initialized")
            return pd.DataFrame()
        
        try:
            interval_map = {
                '1m': Client.KLINE_INTERVAL_1MINUTE,
                '5m': Client.KLINE_INTERVAL_5MINUTE,
                '15m': Client.KLINE_INTERVAL_15MINUTE,
                '1h': Client.KLINE_INTERVAL_1HOUR,
                '4h': Client.KLINE_INTERVAL_4HOUR,
                '1d': Client.KLINE_INTERVAL_1DAY
            }
            
            interval = interval_map.get(timeframe, Client.KLINE_INTERVAL_1HOUR)
            klines = self.binance_client.get_historical_klines(symbol, interval, f"{limit} hours ago UTC")
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert to proper data types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"Error fetching crypto data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_stock_data(self, symbol: str, period: str = '1d', interval: str = '1h') -> pd.DataFrame:
        """Fetch stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            # Standardize column names
            df.columns = [col.lower() for col in df.columns]
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_market_data(self, symbol: str, timeframe: str = '1h') -> pd.DataFrame:
        """Get market data from appropriate source based on symbol"""
        # Determine if it's crypto or stock
        if any(crypto in symbol.upper() for crypto in ['BTC', 'ETH', 'USDT', 'USD', 'EUR']):
            return self.get_crypto_data(symbol, timeframe)
        else:
            # Convert timeframe to Yahoo Finance format
            period_map = {
                '1h': ('1d', '1h'),
                '4h': ('5d', '1h'),
                '1d': ('1mo', '1d')
            }
            period, interval = period_map.get(timeframe, ('1d', '1h'))
            return self.get_stock_data(symbol, period, interval)

class ChartAnalyst:
    """Main ChartAnalyst agent class"""
    
    def __init__(self):
        self.pattern_detector = PatternDetector()
        self.data_provider = MarketDataProvider()
        self.redis_client = None
        
        # Initialize Redis if available
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")
    
    def analyze_symbol(self, symbol: str, timeframe: str = '1h') -> Optional[TechnicalSignal]:
        """Main analysis function that processes a symbol and returns signals"""
        try:
            logger.info(f"Analyzing {symbol} on {timeframe} timeframe")
            
            # Get market data
            df = self.data_provider.get_market_data(symbol, timeframe)
            if df.empty:
                logger.error(f"No data available for {symbol}")
                return None
            
            # Detect patterns
            candlestick_patterns = self.pattern_detector.detect_candlestick_patterns(df)
            chart_patterns = self.pattern_detector.detect_chart_patterns(df)
            support_levels, resistance_levels = self.pattern_detector.detect_support_resistance(df)
            
            # Determine trend and volatility
            trend = self.pattern_detector.determine_trend(df)
            volatility = self.pattern_detector.calculate_volatility(df)
            
            # Determine primary pattern and confidence
            primary_pattern = self._determine_primary_pattern(candlestick_patterns, chart_patterns)
            confidence = self._calculate_confidence(df, candlestick_patterns, chart_patterns, trend)
            
            # Create signal
            signal = TechnicalSignal(
                agent="chartanalyst",
                timestamp=datetime.now(timezone.utc).isoformat(),
                symbol=symbol,
                timeframe=timeframe,
                pattern=primary_pattern,
                confidence=confidence,
                support_zone=support_levels[:2] if support_levels else [0, 0],
                resistance_zone=resistance_levels[:2] if resistance_levels else [0, 0],
                trend=trend,
                volatility=volatility,
                additional_data={
                    "candlestick_patterns": candlestick_patterns,
                    "chart_patterns": chart_patterns,
                    "current_price": float(df['close'].iloc[-1]),
                    "volume": float(df['volume'].iloc[-1])
                }
            )
            
            logger.info(f"Generated signal: {primary_pattern} with {confidence}% confidence")
            return signal
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def _determine_primary_pattern(self, candlestick_patterns: Dict, chart_patterns: List[str]) -> str:
        """Determine the most significant pattern"""
        # Priority to bullish/bearish engulfing patterns
        if 'CDLENGULFING' in candlestick_patterns:
            if candlestick_patterns['CDLENGULFING'] > 0:
                return "Bullish Engulfing"
            else:
                return "Bearish Engulfing"
        
        # Check for doji patterns
        if 'CDLDOJI' in candlestick_patterns:
            return "Doji"
        
        # Check for hammer patterns
        if 'CDLHAMMER' in candlestick_patterns and candlestick_patterns['CDLHAMMER'] != 0:
            return "Hammer"
        
        # Check for shooting star
        if 'CDLSHOOTINGSTAR' in candlestick_patterns and candlestick_patterns['CDLSHOOTINGSTAR'] != 0:
            return "Shooting Star"
        
        # Fall back to chart patterns
        if chart_patterns:
            return chart_patterns[0]
        
        return "No Significant Pattern"
    
    def _calculate_confidence(self, df: pd.DataFrame, candlestick_patterns: Dict, 
                            chart_patterns: List[str], trend: str) -> int:
        """Calculate confidence score based on multiple factors"""
        confidence = 50  # Base confidence
        
        # Boost confidence for strong candlestick patterns
        strong_patterns = ['CDLENGULFING', 'CDLHAMMER', 'CDLSHOOTINGSTAR', 'CDLDOJI']
        for pattern in strong_patterns:
            if pattern in candlestick_patterns:
                confidence += 15
        
        # Volume confirmation
        recent_volume = df['volume'].tail(5).mean()
        avg_volume = df['volume'].mean()
        if recent_volume > avg_volume * 1.2:
            confidence += 10
        
        # Trend alignment
        if trend != "Sideways":
            confidence += 10
        
        # Multiple pattern confirmation
        if len(candlestick_patterns) > 1:
            confidence += 5
        
        # Cap confidence
        confidence = min(confidence, 95)
        confidence = max(confidence, 10)
        
        return confidence
    
    def publish_signal(self, signal: TechnicalSignal):
        """Publish signal to Redis event bus"""
        if not self.redis_client:
            logger.warning("Redis not available, cannot publish signal")
            return
        
        try:
            signal_json = json.dumps(asdict(signal), default=str)
            self.redis_client.publish("chartanalyst_out", signal_json)
            logger.info(f"Published signal for {signal.symbol}")
        except Exception as e:
            logger.error(f"Error publishing signal: {e}")
    
    def run_analysis(self, symbol: str, timeframe: str = '1h') -> Optional[TechnicalSignal]:
        """Run complete analysis and optionally publish"""
        signal = self.analyze_symbol(symbol, timeframe)
        if signal:
            self.publish_signal(signal)
            # Also print to console for testing
            print(f"\n=== ChartAnalyst Signal ===")
            print(f"Symbol: {signal.symbol}")
            print(f"Pattern: {signal.pattern}")
            print(f"Confidence: {signal.confidence}%")
            print(f"Trend: {signal.trend}")
            print(f"Volatility: {signal.volatility}")
            print(f"Support: {signal.support_zone}")
            print(f"Resistance: {signal.resistance_zone}")
            print(f"Timestamp: {signal.timestamp}")
            print("=" * 30)
        return signal

async def main():
    """Main function for testing ChartAnalyst"""
    analyst = ChartAnalyst()
    
    # Test symbols
    test_symbols = ["BTCUSDT", "ETHUSDT", "AAPL", "TSLA", "XAUUSD"]
    
    for symbol in test_symbols:
        print(f"\nAnalyzing {symbol}...")
        signal = analyst.run_analysis(symbol, "1h")
        if signal:
            print("✅ Analysis completed successfully")
        else:
            print("❌ Analysis failed")
        
        # Small delay between analyses
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
