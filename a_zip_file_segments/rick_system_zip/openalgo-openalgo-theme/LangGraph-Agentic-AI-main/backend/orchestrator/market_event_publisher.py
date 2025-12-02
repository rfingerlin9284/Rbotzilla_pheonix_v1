# backend/event_producers/market_event_publisher.py

import os
import asyncio
import json
from datetime import datetime
import requests
import redis
from dotenv import load_dotenv

load_dotenv()

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.Redis.from_url(REDIS_URL)

# API Keys
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Target pairs
SYMBOLS = ["XAUUSD", "XAGUSD", "EURUSD", "USDZAR", "GBPUSD"]

# === Step 1: Get live price from Alpha Vantage ===
def fetch_price(symbol: str):
    if len(symbol) != 6:
        return None
    from_currency = symbol[:3]
    to_currency = symbol[3:]
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": from_currency,
        "to_currency": to_currency,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        rate = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
        return rate
    except Exception as e:
        print(f"⚠️ Error fetching {symbol}: {e}")
        return None

# === Step 2: Search for news with Tavily ===
def fetch_news_alert(symbol: str):
    url = "https://api.tavily.com/search"
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    payload = {
        "query": f"latest news on {symbol}",
        "search_depth": "basic",
        "include_answer": True,
        "include_sources": False,
        "max_results": 1
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        if res.ok:
            return res.json().get("answer", "No news found.")
    except Exception as e:
        print(f"❌ Tavily error for {symbol}: {e}")
    return None

# === Step 3: Publish to Redis Event Bus ===
def publish_market_event(symbol, price, news):
    event = {
        "type": "market_event",
        "symbol": symbol,
        "price": price,
        "timestamp": datetime.utcnow().isoformat(),
        "news": news,
        "source": "event_publisher"
    }
    redis_client.publish("events", json.dumps(event))
    print(f"📤 Published: {symbol} @ {price:.4f} | 🗞️ {news[:80]}...")

# --- Gemini reasoning ---
def analyze_with_gemini(symbol, price, news):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""You're a financial analyst. Analyze the following market data:

- Symbol: {symbol}
- Price: {price}
- News: {news}

Give a 1-line insight or alert for day traders."""
                        }
                    ]
                }
            ]
        }

        params = {"key": api_key}
        response = requests.post(url, headers=headers, params=params, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"🧠 Gemini error: {e}")
        return "AI analysis unavailable"


# === Step 4: Loop ===
async def main_loop():
    while True:
        for symbol in SYMBOLS:
            price = fetch_price(symbol)
            if price:
                news = fetch_news_alert(symbol)
                publish_market_event(symbol, price, news or "No major news.")
        await asyncio.sleep(15)  # adjust frequency

if __name__ == "__main__":
    asyncio.run(main_loop())
