import requests
import json
import os
from datetime import datetime
import redis
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Redis client setup with error handling
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()  # Test connection
    print("✅ Redis connected")
except redis.ConnectionError:
    print("⚠️ Redis not available, events will be printed only")
    redis_client = None

def publish_market_event(symbol, price, news):
    """Publish market event to Redis and console"""
    event = {
        "type": "market_event",
        "symbol": symbol,
        "price": price,
        "timestamp": datetime.utcnow().isoformat(),
        "news": news,
        "source": "market_fetcher"
    }
    
    # Publish to Redis if available
    if redis_client:
        try:
            redis_client.publish("events", json.dumps(event))
            print(f"📤 Published to Redis: {symbol} @ ${price:.2f}")
        except Exception as e:
            print(f"❌ Redis publish error: {e}")
    
    # Always print to console
    print(f"📈 {symbol}: ${price:.2f}")
    print(f"🗞️ News: {news[:100]}...")

def fetch_gold_price():
    """Fetch current gold price from a free API"""
    try:
        # Using Metals-API (free tier available)
        response = requests.get("https://api.metalpriceapi.com/v1/latest?api_key=[API_KEY]=", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "rates" in data:
                # Convert from per ounce to per troy ounce (standard)
                return 1 / data["rates"]["XAU"]
    except Exception as e:
        print(f"⚠️ Metals API error: {e}")
    
    try:
        # Fallback: Use a different free API
        response = requests.get("https://api.fxmarketapi.com/apilive?api_key=YOUR_FX_API_KEY&currency=XAUUSD", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("price", 1947.32)
    except Exception as e:
        print(f"⚠️ FX API error: {e}")
    
    # Final fallback: return a reasonable dummy price
    print("⚠️ Using dummy gold price")
    return 1947.32

def fetch_tavily_news(query):
    """Fetch news from Tavily API"""
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY environment variable not set")
    
    try:
        response = requests.post(
            "https://api.tavily.com/search", 
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "advanced",
                "max_results": 3
            },
            timeout=15
        )
        
        response.raise_for_status()
        results = response.json()
        
        # Extract and combine news content
        news_items = results.get("results", [])
        if news_items:
            news_content = []
            for item in news_items[:2]:  # Take top 2 results
                content = item.get("content", "").strip()
                if content:
                    news_content.append(content)
            
            return " | ".join(news_content) if news_content else "No relevant news found"
        
        return "No news results returned"
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError(f"Invalid Tavily API key. Status: {e.response.status_code}")
        else:
            raise ValueError(f"Tavily API error: {e.response.status_code} - {e.response.text}")

def fetch_fallback_news():
    """Fetch news from free news APIs as fallback"""
    try:
        # Using NewsAPI (free tier)
        NEWS_API_KEY = os.getenv("NEWS_API_KEY")
        if NEWS_API_KEY:
            url = f"https://newsapi.org/v2/everything?q=gold+prices+USD&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                if articles:
                    news_content = []
                    for article in articles[:2]:
                        title = article.get("title", "")
                        description = article.get("description", "")
                        if title and description:
                            news_content.append(f"{title}: {description}")
                    
                    return " | ".join(news_content) if news_content else "No relevant news found"
    except Exception as e:
        print(f"⚠️ NewsAPI fallback error: {e}")
    
    try:
        # Final fallback: RSS feed parsing (no API key needed)
        import feedparser
        
        feed_url = "https://feeds.reuters.com/reuters/businessNews"
        feed = feedparser.parse(feed_url)
        
        gold_related = []
        for entry in feed.entries[:10]:  # Check recent entries
            title = entry.get("title", "").lower()
            summary = entry.get("summary", "").lower()
            
            if any(keyword in title or keyword in summary for keyword in ["gold", "precious metals", "dollar"]):
                gold_related.append(f"{entry.get('title', '')}: {entry.get('summary', '')}")
        
        return " | ".join(gold_related[:2]) if gold_related else "No relevant gold news found"
        
    except Exception as e:
        print(f"⚠️ RSS fallback error: {e}")
    
    return "Unable to fetch current news - all sources unavailable"

def fetch_gold_news():
    """Main function to fetch gold price and news"""
    print("🔍 Fetching gold market data...")
    
    # Fetch current gold price
    price = fetch_gold_price()
    print(f"💰 Current gold price: ${price:.2f}")
    
    # Try to fetch news from Tavily first
    news = "No news available"
    
    try:
        news = fetch_tavily_news("latest news about gold prices and USD dollar")
        print("✅ News fetched from Tavily")
        
    except ValueError as e:
        print(f"❌ Tavily error: {e}")
        print("🔄 Trying fallback news sources...")
        
        # Try fallback news sources
        news = fetch_fallback_news()
        print("✅ News fetched from fallback sources")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        news = "News fetch failed due to technical issues"
    
    # Publish the market event
    publish_market_event("XAUUSD", price, news)

def main():
    """Main execution function"""
    print("🚀 Starting market news fetcher...")
    
    # Check for required environment variables
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        print("⚠️ TAVILY_API_KEY not set - will use fallback news sources")
    
    try:
        fetch_gold_news()
        print("✅ Market data fetch completed")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
