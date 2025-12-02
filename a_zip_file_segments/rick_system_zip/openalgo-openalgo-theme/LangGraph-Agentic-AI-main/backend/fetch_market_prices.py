import requests
import time
import json
import redis
from datetime import datetime, timedelta
from websocket import create_connection, WebSocketTimeoutException
import threading

# ===== CONFIGURATION =====
POLYGON_API_KEY = "IRgkq3A5wOwqsBY_4rKqVJE9pBkKYSdJ"
ALPHA_VANTAGE_API_KEY = "055UJYJSLJ8A1PKU"
MARKETSTACK_API_KEY = "ca851905b625c73e2b7cc532940f49a2"

SYMBOLS = {
    "XAUUSD": {"polygon": "XAUUSD", "alpha_vantage": "XAU/USD", "marketstack": "GLD"},
    "XAGUSD": {"polygon": "XAGUSD", "alpha_vantage": "XAG/USD", "marketstack": "SLV"},
    "USDINDEX": {"polygon": "USD", "alpha_vantage": "DXY", "marketstack": "UUP"}
}

# ===== GLOBAL STATE =====
class APIState:
    def __init__(self):
        self.last_called = {
            "polygon": datetime.min,
            "alpha_vantage": datetime.min,
            "marketstack": datetime.min
        }
        self.usage_counts = {
            "polygon": 0,
            "alpha_vantage": 0,
            "marketstack": 0
        }
        self.cache = {}
        self.ws_connected = False

api_state = APIState()

# Initialize Redis with error handling
try:
    redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    redis_client.ping()  # Test connection
    print("✅ Redis connected")
except redis.ConnectionError:
    print("⚠️ Redis not available, events will be printed only")
    redis_client = None

# ===== CACHING LAYER =====
def get_cached_price(symbol: str) -> float:
    """Check cache for recent price (valid for 30 seconds)"""
    if symbol in api_state.cache:
        cached_time, price = api_state.cache[symbol]
        if datetime.now() - cached_time < timedelta(seconds=30):
            return price
    return None

def update_cache(symbol: str, price: float):
    """Update cache with new price"""
    api_state.cache[symbol] = (datetime.now(), price)

# ===== API CLIENT WITH RATE LIMITING =====
def can_call_api(provider: str) -> bool:
    """Check if API can be called based on rate limits"""
    now = datetime.now()
    
    # Reset usage count every minute
    if now - api_state.last_called[provider] > timedelta(minutes=1):
        api_state.usage_counts[provider] = 0
    
    # Check rate limits
    if provider == "polygon":
        return (now - api_state.last_called[provider] >= timedelta(seconds=12) and 
                api_state.usage_counts[provider] < 5)
    elif provider == "alpha_vantage":
        return (now - api_state.last_called[provider] >= timedelta(seconds=12) and 
                api_state.usage_counts[provider] < 5)
    elif provider == "marketstack":
        return (now - api_state.last_called[provider] >= timedelta(seconds=1) and 
                api_state.usage_counts[provider] < 100)
    
    return False

def call_api(provider: str, url: str) -> dict:
    """Generic API caller with rate limiting"""
    if not can_call_api(provider):
        print(f"⏳ Rate limit hit for {provider}")
        return None
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        api_state.last_called[provider] = datetime.now()
        api_state.usage_counts[provider] += 1
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed for {provider}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error for {provider}: {e}")
        return None

# ===== PRICE FETCHERS =====
def fetch_polygon_price(symbol: str) -> float:
    """Fetch price from Polygon API"""
    if symbol == "USD":
        return 1.0
    
    # Use correct Polygon forex endpoint
    if symbol in ["XAUUSD", "XAGUSD"]:
        url = f"https://api.polygon.io/v2/aggs/ticker/C:{symbol}/prev?adjusted=true&apikey={POLYGON_API_KEY}"
    else:
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={POLYGON_API_KEY}"
    
    data = call_api("polygon", url)
    
    if data and data.get("results") and len(data["results"]) > 0:
        return float(data["results"][0]["c"])
    return None

def fetch_alpha_vantage_price(symbol: str) -> float:
    """Fetch price from Alpha Vantage API"""
    if symbol == "DXY":
        # DXY is not directly available, use UUP ETF as proxy
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=UUP&apikey={ALPHA_VANTAGE_API_KEY}"
        data = call_api("alpha_vantage", url)
        if data and "Global Quote" in data:
            return float(data["Global Quote"]["05. price"])
    else:
        # For forex pairs like XAU/USD
        from_curr, to_curr = symbol.split('/')
        url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_curr}&to_currency={to_curr}&apikey={ALPHA_VANTAGE_API_KEY}"
        data = call_api("alpha_vantage", url)
        if data and "Realtime Currency Exchange Rate" in data:
            return float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
    
    return None

def fetch_marketstack_price(symbol: str) -> float:
    """Fetch price from Marketstack API"""
    url = f"http://api.marketstack.com/v1/tickers/{symbol}/eod/latest?access_key={MARKETSTACK_API_KEY}"
    data = call_api("marketstack", url)
    
    if data and "close" in data:
        return float(data["close"])
    return None

# ===== WEBSOCKET MANAGER =====
def start_websocket_listener():
    """Connect to Polygon WebSocket for real-time updates with reconnection logic"""
    if not POLYGON_API_KEY:
        print("⚠️ No Polygon API key, skipping WebSocket")
        return
    
    ws_url = "wss://socket.polygon.io/forex"
    max_retries = 5
    retry_delay = 5
    
    while api_state.ws_connected and max_retries > 0:
        ws = None
        try:
            print(f"🔌 Attempting WebSocket connection... (retries left: {max_retries})")
            ws = create_connection(ws_url, timeout=10)
            
            # Authenticate
            auth_msg = {"action": "auth", "params": POLYGON_API_KEY}
            ws.send(json.dumps(auth_msg))
            
            # Wait for auth response
            auth_response = ws.recv()
            print(f"Auth response: {auth_response}")
            
            # Subscribe to forex pairs
            subscribe_msg = {"action": "subscribe", "params": "C.C:XAUUSD,C.C:XAGUSD"}
            ws.send(json.dumps(subscribe_msg))
            
            print("✅ WebSocket connected and subscribed")
            
            # Reset retry counter on successful connection
            max_retries = 5
            
            # Message loop
            while api_state.ws_connected:
                try:
                    message = ws.recv()
                    if not message:
                        break
                        
                    data = json.loads(message)
                    
                    # Handle different message types
                    if isinstance(data, list):
                        for event in data:
                            if event.get("ev") == "C" and "p" in event:  # Currency quote
                                symbol = event.get("pair", "").replace("C:", "")
                                price = float(event["p"])
                                update_cache(symbol, price)
                                publish_market_event(symbol, price, "polygon_ws")
                    elif isinstance(data, dict):
                        # Handle single events or status messages
                        if data.get("status") == "connected":
                            print("✅ WebSocket authenticated successfully")
                        elif data.get("status") == "auth_timeout":
                            print("❌ WebSocket authentication timeout")
                            break
                            
                except WebSocketTimeoutException:
                    # Timeout is normal, continue listening
                    continue
                except Exception as e:
                    if "socket is already closed" in str(e).lower():
                        print("🔌 WebSocket connection closed by server")
                        break
                    else:
                        print(f"WebSocket message error: {e}")
                        break
                        
        except Exception as e:
            print(f"WebSocket connection error: {e}")
            max_retries -= 1
            
        finally:
            # Clean up connection
            if ws:
                try:
                    ws.close()
                except:
                    pass
            
            # Wait before retrying (if we're going to retry)
            if api_state.ws_connected and max_retries > 0:
                print(f"⏳ Waiting {retry_delay}s before WebSocket reconnection...")
                time.sleep(retry_delay)
    
    print("❌ WebSocket listener stopped")
    api_state.ws_connected = False

# ===== MAIN LOGIC =====
def get_price(symbol_config: dict, symbol_name: str) -> float:
    """Get price from cache or APIs"""
    # Check cache first
    cached_price = get_cached_price(symbol_name)
    if cached_price:
        return cached_price
    
    price = None
    
    # Try Polygon first
    if "polygon" in symbol_config:
        price = fetch_polygon_price(symbol_config["polygon"])
    
    # Fall back to Alpha Vantage
    if not price and "alpha_vantage" in symbol_config:
        price = fetch_alpha_vantage_price(symbol_config["alpha_vantage"])
    
    # Fall back to Marketstack
    if not price and "marketstack" in symbol_config:
        price = fetch_marketstack_price(symbol_config["marketstack"])
    
    if price:
        update_cache(symbol_name, price)
    
    return price

def publish_market_event(symbol: str, price: float, source: str):
    """Publish market event to Redis and console"""
    event = {
        "type": "market_event",
        "symbol": symbol,
        "price": price,
        "timestamp": datetime.utcnow().isoformat(),
        "source": source
    }
    
    # Publish to Redis if available
    if redis_client:
        try:
            redis_client.publish("market_events", json.dumps(event))
        except Exception as e:
            print(f"Redis publish error: {e}")
    
    # Always print to console
    print(f"📈 {symbol}: ${price:.4f} (via {source})")

def main():
    """Main application loop"""
    print("🚀 Starting hybrid market data fetcher...")
    print("Press Ctrl+C to stop")
    
    # Start WebSocket in background thread
    api_state.ws_connected = True  # Set this before starting thread
    ws_thread = threading.Thread(target=start_websocket_listener, daemon=True)
    ws_thread.start()
    
    try:
        while True:
            for symbol_name, config in SYMBOLS.items():
                price = get_price(config, symbol_name)
                if price:
                    publish_market_event(symbol_name, price, "api_poll")
                else:
                    print(f"⚠️ Failed to fetch price for {symbol_name}")
                
                # Small delay between symbols to avoid overwhelming APIs
                time.sleep(1)
            
            # Wait before next polling cycle
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        
        # Stop WebSocket connection
        api_state.ws_connected = False
        
        # Give WebSocket thread time to close gracefully
        if ws_thread.is_alive():
            print("⏳ Waiting for WebSocket to close...")
            ws_thread.join(timeout=5)
        
        print("✅ Stopped gracefully")

if __name__ == "__main__":
    main()
