#!/usr/bin/env python3
"""
Free Market Data Connectors for Rick
Uses free APIs: Yahoo Finance (via requests) + CryptoPanic
Perfect for paper trading with real market signals
"""
import requests
import json
import time
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FreeMarketDataConnector:
    """
    Free market data using Yahoo Finance web endpoints
    No external dependencies needed - just requests
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 200ms between requests
        
    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current price from Yahoo Finance
        
        Args:
            symbol: Rick's symbol format (e.g., 'EUR.USD', 'BTC.USD', 'AAPL')
        
        Returns:
            {
                'symbol': str,
                'price': float,
                'bid': float,
                'ask': float,
                'change_percent': float,
                'timestamp': str,
                'source': 'yahoo_free'
            }
        """
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        
        try:
            yahoo_symbol = self._convert_to_yahoo_symbol(symbol)
            
            # Yahoo Finance query endpoint
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'chart' in data and data['chart']['result']:
                result_data = data['chart']['result'][0]
                meta = result_data['meta']
                
                current_price = meta.get('regularMarketPrice', 0)
                if not current_price:
                    current_price = meta.get('previousClose', 0)
                
                result = {
                    'symbol': symbol,
                    'yahoo_symbol': yahoo_symbol,
                    'price': float(current_price) if current_price else 0.0,
                    'bid': float(meta.get('bid', 0)) if meta.get('bid') else 0.0,
                    'ask': float(meta.get('ask', 0)) if meta.get('ask') else 0.0,
                    'change_percent': float(meta.get('regularMarketChangePercent', 0)) if meta.get('regularMarketChangePercent') else 0.0,
                    'volume': int(meta.get('regularMarketVolume', 0)),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source': 'yahoo_free'
                }
                
                # If no bid/ask, estimate from price
                if result['bid'] == 0 and result['ask'] == 0 and result['price'] > 0:
                    spread = result['price'] * 0.0001  # 0.01% spread estimate
                    result['bid'] = result['price'] - spread
                    result['ask'] = result['price'] + spread
                
                self.last_request_time = time.time()
                logger.debug(f"📊 {symbol}: ${result['price']:.5f}")
                
                return result
            else:
                raise Exception("No data in Yahoo response")
                
        except Exception as e:
            logger.error(f"❌ Yahoo error for {symbol}: {e}")
            return {
                'symbol': symbol,
                'price': 0.0,
                'bid': 0.0,
                'ask': 0.0,
                'change_percent': 0.0,
                'volume': 0,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'source': 'yahoo_free',
                'error': str(e)
            }
    
    def _convert_to_yahoo_symbol(self, symbol: str) -> str:
        """Convert Rick's symbol format to Yahoo Finance format"""
        symbol = symbol.upper().replace('_', '.')
        
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
            'USD/CAD': 'USDCAD=X',
            'NZD.USD': 'NZDUSD=X',
            'NZDUSD': 'NZDUSD=X',
            'NZD/USD': 'NZDUSD=X'
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
            'SOL/USD': 'SOL-USD',
            'LINK.USD': 'LINK-USD',
            'LINKUSD': 'LINK-USD',
            'LINK/USD': 'LINK-USD'
        }
        
        # Check forex first
        if symbol in forex_map:
            return forex_map[symbol]
        
        # Check crypto
        if symbol in crypto_map:
            return crypto_map[symbol]
        
        # Default to stock symbol
        return symbol

class CryptoPanicConnector:
    """
    CryptoPanic API connector for crypto news and sentiment
    Uses your existing API key
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
            
            response = self.session.get(f"{self.base_url}/posts/", params=params, timeout=10)
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

# Test the connectors
if __name__ == "__main__":
    print("🌍 Free Market Data Test for Rick")
    print("=" * 50)
    print("📊 Yahoo Finance + CryptoPanic APIs")
    print("💰 Perfect for paper trading with real signals")
    print()
    
    # Test free Yahoo Finance data
    print("📈 Testing Yahoo Finance (Free):")
    print("-" * 35)
    
    yahoo = FreeMarketDataConnector()
    
    test_symbols = [
        ('EUR.USD', 'Euro/Dollar Forex'),
        ('GBP.USD', 'Pound/Dollar Forex'),
        ('BTC.USD', 'Bitcoin Crypto'),
        ('ETH.USD', 'Ethereum Crypto'),
        ('AAPL', 'Apple Stock'),
        ('SPY', 'S&P 500 ETF')
    ]
    
    working_symbols = []
    
    for symbol, description in test_symbols:
        data = yahoo.get_current_price(symbol)
        if 'error' not in data and data['price'] > 0:
            price = data['price']
            change = data['change_percent']
            print(f"✅ {symbol:8} ({description:18}) | ${price:10.5f} | {change:+6.2f}%")
            working_symbols.append(symbol)
        else:
            print(f"❌ {symbol:8} ({description:18}) | No data")
        time.sleep(0.3)  # Be nice to Yahoo
    
    print()
    print("📰 Testing CryptoPanic API:")
    print("-" * 30)
    
    # Test CryptoPanic with your API key
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
                print(f"✅ Got {len(news)} crypto news items")
                for i, item in enumerate(news[:3], 1):
                    title = item['title'][:45] + "..." if len(item['title']) > 45 else item['title']
                    print(f"   {i}. {title} ({item['sentiment']})")
            else:
                print("❌ No crypto news received")
        else:
            print("❌ CRYPTOPANIC_API_KEY not found in env")
            
    except Exception as e:
        print(f"❌ CryptoPanic test error: {e}")
    
    print()
    print("📊 SUMMARY:")
    print("=" * 20)
    
    if working_symbols:
        print(f"✅ Found {len(working_symbols)} working data sources")
        print("🎯 Available for Rick's paper trading:")
        for symbol in working_symbols:
            print(f"   • {symbol}")
        print()
        print("🚀 Ready to integrate with OANDA/Coinbase!")
        print("💰 Real market signals + fake money = zero risk")
    else:
        print("❌ No working data sources found")
        print("🔧 Check internet connection and try again")
    
    print()
    print("🎯 Next Steps:")
    print("   1. Test OANDA practice account")
    print("   2. Test Coinbase sandbox account") 
    print("   3. Configure Rick to use these free data sources")
    print("   4. Launch paper trading with real market signals!")