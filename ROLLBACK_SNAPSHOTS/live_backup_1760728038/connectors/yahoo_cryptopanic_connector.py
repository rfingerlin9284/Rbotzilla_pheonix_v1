#!/usr/bin/env python3
"""
Yahoo Finance API Connector for Rick
Free real-time market data for stocks, forex, crypto
Perfect for Rick's paper trading with real market signals
"""
import yfinance as yf
import requests
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooFinanceConnector:
    """
    Free Yahoo Finance API connector for Rick's market data
    Provides real-time prices for forex, stocks, crypto
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests (be nice to Yahoo)
        
    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current price data from Yahoo Finance
        
        Args:
            symbol: Yahoo format symbol (e.g., 'EURUSD=X', 'BTC-USD', 'AAPL')
        
        Returns:
            {
                'symbol': str,
                'price': float,
                'bid': float,
                'ask': float,
                'volume': int,
                'change': float,
                'change_percent': float,
                'timestamp': str
            }
        """
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        
        try:
            # Convert symbol to Yahoo format if needed
            yahoo_symbol = self._convert_to_yahoo_symbol(symbol)
            
            # Get ticker data
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            
            # Get current price
            current_price = info.get('regularMarketPrice', 0)
            if current_price == 0:
                current_price = info.get('ask', info.get('bid', 0))
            
            result = {
                'symbol': symbol,
                'yahoo_symbol': yahoo_symbol,
                'price': float(current_price) if current_price else 0.0,
                'bid': float(info.get('bid', 0)) if info.get('bid') else 0.0,
                'ask': float(info.get('ask', 0)) if info.get('ask') else 0.0,
                'volume': int(info.get('regularMarketVolume', 0)),
                'change': float(info.get('regularMarketChange', 0)) if info.get('regularMarketChange') else 0.0,
                'change_percent': float(info.get('regularMarketChangePercent', 0)) if info.get('regularMarketChangePercent') else 0.0,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'source': 'yahoo_finance'
            }
            
            self.last_request_time = time.time()
            logger.debug(f"📊 {symbol}: ${result['price']:.5f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Yahoo Finance error for {symbol}: {e}")
            return {
                'symbol': symbol,
                'price': 0.0,
                'bid': 0.0,
                'ask': 0.0,
                'volume': 0,
                'change': 0.0,
                'change_percent': 0.0,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'source': 'yahoo_finance',
                'error': str(e)
            }
    
    def _convert_to_yahoo_symbol(self, symbol: str) -> str:
        """Convert Rick's symbol format to Yahoo Finance format"""
        symbol = symbol.upper()
        
        # Forex pairs
        forex_map = {
            'EUR.USD': 'EURUSD=X',
            'EURUSD': 'EURUSD=X',
            'EUR/USD': 'EURUSD=X',
            'GBP.USD': 'GBPUSD=X',
            'GBPUSD': 'GBPUSD=X',
            'GBP/USD': 'GBPUSD=X',
            'USD.JPY': 'USDJPY=X',
            'USDJPY': 'USDJPY=X',
            'USD/JPY': 'USDJPY=X',
            'USD.CHF': 'USDCHF=X',
            'USDCHF': 'USDCHF=X',
            'USD/CHF': 'USDCHF=X',
            'AUD.USD': 'AUDUSD=X',
            'AUDUSD': 'AUDUSD=X',
            'AUD/USD': 'AUDUSD=X',
            'USD.CAD': 'USDCAD=X',
            'USDCAD': 'USDCAD=X',
            'USD/CAD': 'USDCAD=X'
        }
        
        # Crypto
        crypto_map = {
            'BTC.USD': 'BTC-USD',
            'BTCUSD': 'BTC-USD',
            'BTC/USD': 'BTC-USD',
            'ETH.USD': 'ETH-USD',
            'ETHUSD': 'ETH-USD',
            'ETH/USD': 'ETH-USD',
            'ADA.USD': 'ADA-USD',
            'ADAUSD': 'ADA-USD',
            'ADA/USD': 'ADA-USD',
            'SOL.USD': 'SOL-USD',
            'SOLUSD': 'SOL-USD',
            'SOL/USD': 'SOL-USD'
        }
        
        # Check forex first
        if symbol in forex_map:
            return forex_map[symbol]
        
        # Check crypto
        if symbol in crypto_map:
            return crypto_map[symbol]
        
        # Default to stock symbol (AAPL, MSFT, etc.)
        return symbol

class CryptoPanicConnector:
    """
    CryptoPanic API connector for crypto news and sentiment
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://cryptopanic.com/api/v1"
        self.session = requests.Session()
        
    def get_crypto_news(self, currencies: List[str] = None, limit: int = 10) -> List[Dict]:
        """
        Get latest crypto news and sentiment
        
        Args:
            currencies: List of crypto symbols (e.g., ['BTC', 'ETH'])
            limit: Number of news items to return
            
        Returns:
            List of news items with sentiment analysis
        """
        try:
            params = {
                'auth_token': self.api_key,
                'public': 'true',
                'kind': 'news',
                'limit': limit
            }
            
            if currencies:
                params['currencies'] = ','.join(currencies)
            
            response = self.session.get(f"{self.base_url}/posts/", params=params)
            response.raise_for_status()
            
            data = response.json()
            news_items = []
            
            for item in data.get('results', []):
                news_items.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'published_at': item.get('published_at', ''),
                    'kind': item.get('kind', ''),
                    'currencies': item.get('currencies', []),
                    'votes': item.get('votes', {}),
                    'sentiment': self._analyze_sentiment(item)
                })
            
            return news_items
            
        except Exception as e:
            logger.error(f"❌ CryptoPanic API error: {e}")
            return []
    
    def _analyze_sentiment(self, news_item: Dict) -> str:
        """Simple sentiment analysis based on votes"""
        votes = news_item.get('votes', {})
        positive = votes.get('positive', 0)
        negative = votes.get('negative', 0)
        
        if positive > negative:
            return 'positive'
        elif negative > positive:
            return 'negative'
        else:
            return 'neutral'

# Example usage and testing
if __name__ == "__main__":
    print("🌍 Yahoo Finance + CryptoPanic Test")
    print("=" * 50)
    print("📊 Free real-time market data for Rick")
    print("🎯 Perfect for paper trading with real signals")
    print()
    
    # Test Yahoo Finance
    print("📈 Testing Yahoo Finance API:")
    print("-" * 30)
    
    yahoo = YahooFinanceConnector()
    
    test_symbols = [
        ('EUR.USD', 'Euro/Dollar'),
        ('BTC.USD', 'Bitcoin'),
        ('AAPL', 'Apple Stock'),
        ('SPY', 'S&P 500 ETF')
    ]
    
    for symbol, description in test_symbols:
        data = yahoo.get_current_price(symbol)
        if 'error' not in data and data['price'] > 0:
            print(f"✅ {symbol:8} ({description:12}) | ${data['price']:8.4f} | Change: {data['change_percent']:+6.2f}%")
        else:
            print(f"❌ {symbol:8} ({description:12}) | No data")
        time.sleep(0.2)
    
    print()
    print("📰 Testing CryptoPanic API:")
    print("-" * 28)
    
    # Load CryptoPanic key from environment
    import os
    import sys
    sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN')
    try:
        from load_env import load_env_file
        load_env_file('env_new2.env')
        cryptopanic_key = os.getenv('CRYPTOPANIC_API_KEY')
        
        if cryptopanic_key:
            crypto_news = CryptoPanicConnector(cryptopanic_key)
            news = crypto_news.get_crypto_news(['BTC', 'ETH'], limit=5)
            
            if news:
                print(f"✅ Got {len(news)} news items")
                for item in news[:3]:
                    print(f"   📰 {item['title'][:50]}... ({item['sentiment']})")
            else:
                print("❌ No news data received")
        else:
            print("❌ CRYPTOPANIC_API_KEY not found")
            
    except Exception as e:
        print(f"❌ CryptoPanic test error: {e}")
    
    print()
    print("✅ Free market data sources ready for Rick!")
    print("🎯 Next: Integrate with OANDA/Coinbase paper trading")