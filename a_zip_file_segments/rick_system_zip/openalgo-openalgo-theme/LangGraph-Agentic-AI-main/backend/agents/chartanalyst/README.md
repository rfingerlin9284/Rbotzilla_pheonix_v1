# ?? ChartAnalyst - AI-Powered Technical Analysis Agent

**ChartAnalyst** is a specialized AI agent designed for real-time technical pattern detection and market analysis. It processes raw market data (OHLCV) to identify tradeable technical patterns and publishes precise technical signals for downstream systems.

## ?? Mission

ChartAnalyst's sole purpose is to:
- **Analyze** raw market data from multiple sources
- **Detect** trade-worthy technical patterns  
- **Score** patterns with confidence metrics
- **Publish** standardized technical signals to event bus

This agent doesn't execute trades or provide investment advice - it's a pure pattern recognition system that feeds technical intelligence to other trading system components.

## ✨ Key Features

### ?? Pattern Detection
- **60+ Candlestick Patterns**: Using TA-Lib for professional-grade pattern recognition
- **Chart Patterns**: Triangles, flags, head & shoulders, wedges
- **Support/Resistance Zones**: Dynamic S/R level detection
- **Trend Classification**: Bull, Bear, Sideways market regimes
- **Volume Analysis**: Spike detection and volume confirmation
- **Volatility Regimes**: Low, Medium, High volatility classification

### ?? Data Sources
- **Binance WebSocket**: Real-time crypto data
- **Yahoo Finance**: Stock and forex data
- **Extensible Architecture**: Easy to add more providers

### ?? Signal Output
```json
{
  "agent": "chartanalyst",
  "timestamp": "2025-08-12T12:34:56Z",
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "pattern": "Bullish Engulfing",
  "confidence": 87,
  "support_zone": [29200, 29500],
  "resistance_zone": [31000, 31250],
  "trend": "Bull",
  "volatility": "Medium"
}
```

## ??️ Architecture

```
Market Data → Pattern Detection → Signal Scoring → Event Bus Publication
     ↓              ↓                    ↓                ↓
[Binance/Yahoo] → [TA-Lib + Custom] → [ML Scoring] → [Redis Pub/Sub]
```

### Core Components

1. **MarketDataProvider**: Multi-source data fetching
2. **PatternDetector**: TA-Lib + custom pattern algorithms  
3. **ChartAnalyst**: Main analysis engine and signal generator
4. **Redis Event Bus**: Signal publication system

## ?? Quick Start

### Prerequisites
- Python 3.8+
- TA-Lib (technical analysis library)
- Redis (optional, for event bus)

### Installation

#### Option 1: Automated Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd chartanalyst

# Run automated setup
python setup.py
```

#### Option 2: Manual Installation
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install build-essential wget python3-dev

# Install TA-Lib from source
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr/local
make && sudo make install
cd .. && rm -rf ta-lib*

# Install Python dependencies
pip install -r requirements.txt
```

### Configuration

1. **Copy environment template:**
```bash
cp .env.example .env
```

2. **Edit .env with your API keys:**
```bash
# Binance API (for crypto data)
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_secret_here

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Analysis settings
DEFAULT_TIMEFRAME=1h
CONFIDENCE_THRESHOLD=50
```

## ?? Usage

### Basic Analysis
```bash
# Analyze a single symbol
python test_chartanalyst.py single BTCUSDT 1h

# Run comprehensive test suite
python test_chartanalyst.py comprehensive

# Show pattern detection capabilities
python test_chartanalyst.py patterns
```

### Programmatic Usage
```python
from chartanalyst_main import ChartAnalyst

# Initialize analyzer
analyst = ChartAnalyst()

# Analyze a symbol
signal = analyst.analyze_symbol("BTCUSDT", "1h")

if signal:
    print(f"Pattern: {signal.pattern}")
    print(f"Confidence: {signal.confidence}%")
    print(f"Trend: {signal.trend}")
    
# Run analysis with event bus publishing
signal = analyst.run_analysis("ETHUSDT", "4h")
```

### Continuous Analysis
```python
import asyncio
from chartanalyst_main import ChartAnalyst

async def continuous_analysis():
    analyst = ChartAnalyst()
    symbols = ["BTCUSDT", "ETHUSDT", "AAPL", "TSLA"]
    
    while True:
        for symbol in symbols:
            signal = analyst.run_analysis(symbol, "1h")
            if signal and signal.confidence > 70:
                print(f"?? High confidence signal: {signal.pattern} for {symbol}")
        
        await asyncio.sleep(600)  # Analyze every 10 minutes

asyncio.run(continuous_analysis())
```

## ?? Testing

### Run Test Suite
```bash
# Complete test suite
python test_chartanalyst.py comprehensive

# Test specific functionality  
python test_chartanalyst.py single BTCUSDT
python test_chartanalyst.py patterns

# Test with different symbols and timeframes
python test_chartanalyst.py single AAPL 1d
python test_chartanalyst.py single ETHUSDT 4h
```

### Expected Output
```
?? Starting ChartAnalyst Comprehensive Test Suite
============================================================

?? Testing Data Fetching...
  Testing BTCUSDT...
    ✅ BTCUSDT: 100 candles fetched
    ?? Latest close: 43250.50

?? Testing Pattern Detection for BTCUSDT...
  ?? Detected 3 candlestick patterns
    CDLENGULFING: 100
    CDLDOJI: 0
  ?? Support levels: [42800.0, 43000.0]
  ?? Resistance levels: [43500.0, 43800.0]
  ?? Chart patterns: ['Ascending Trend']
  ?? Current trend: Bull
  ?? Volatility regime: Medium

?? Testing Signal Generation...
  Generating signal for BTCUSDT...
    ✅ Signal generated: Bullish Engulfing (87%)
    ?? Trend: Bull, Volatility: Medium

?? TEST SUMMARY
------------------------------
✅ Data fetching: 5/5 symbols
✅ Pattern detection: PASS
✅ Signal generation: 3/3 signals
✅ Redis connection: OPTIONAL - NOT CONFIGURED
```

## ?? Docker Deployment

### Build and Run
```bash
# Build Docker image
docker build -t chartanalyst:latest .

# Run with environment variables
docker run -d \
  --name chartanalyst \
  -e BINANCE_API_KEY=your_key \
  -e REDIS_URL=redis://host.docker.internal:6379 \
  chartanalyst:latest

# Run with custom configuration
docker run -d \
  --name chartanalyst \
  -v $(pwd)/.env:/app/.env \
  chartanalyst:latest
```

### Docker Compose
```yaml
version: '3.8'
services:
  chartanalyst:
    build: .
    environment:
      - BINANCE_API_KEY=${BINANCE_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

## ?? Supported Patterns

### Candlestick Patterns (60+)
- **Reversal**: Engulfing, Hammer, Shooting Star, Doji
- **Continuation**: Marubozu, Spinning Top, Three Methods
- **Indecision**: Doji, Harami, High Wave

### Chart Patterns
- **Trend**: Ascending, Descending, Sideways
- **Triangles**: Symmetrical, Ascending, Descending
- **Support/Resistance**: Dynamic zone detection

### Market Regimes
- **Trend**: Bull, Bear, Sideways
- **Volatility**: Low (<1.5%), Medium (1.5-3%), High (>3%)

## ⚙️ Configuration Options

### Analysis Parameters
```bash
# Timeframes
DEFAULT_TIMEFRAME=1h  # 1m, 5m, 15m, 1h, 4h, 1d

# Pattern Detection
CONFIDENCE_THRESHOLD=50
VOLUME_SPIKE_THRESHOLD=1.2
VOLATILITY_HIGH_THRESHOLD=3.0

# Technical Indicators
RSI_PERIOD=14
EMA_FAST_PERIOD=9
EMA_MEDIUM_PERIOD=21
EMA_SLOW_PERIOD=50

# Support/Resistance  
SR_WINDOW_SIZE=20
SR_MIN_TOUCHES=2
SR_TOLERANCE_PERCENTAGE=0.01
```

### Data Source Priority
```bash
# Crypto data sources (in priority order)
DATA_SOURCES_CRYPTO=binance,ccxt

# Stock data sources
DATA_SOURCES_STOCKS=yfinance

# Forex data sources  
DATA_SOURCES_FOREX=yfinance
```

## ?? Troubleshooting

### Common Issues

**TA-Lib Installation Failed**
```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev
# Then reinstall TA-Lib from source

# macOS  
brew install ta-lib

# Windows
# Download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib‑0.4.XX‑cp39‑cp39‑win_amd64.whl
```

**No Data Retrieved**
```bash
# Check API keys in .env
BINANCE_API_KEY=your_actual_key_here

# Test data connection
python -c "from chartanalyst_main import MarketDataProvider; print(MarketDataProvider().get_market_data('BTCUSDT'))"
```

**Redis Connection Failed**
```bash
# Redis is optional - ChartAnalyst works without it
# To use Redis:
docker run -d -p 6379:6379 redis:alpine
# or
sudo apt-get install redis-server
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from chartanalyst_main import ChartAnalyst
analyst = ChartAnalyst()
signal = analyst.run_analysis("BTCUSDT", "1h")
```

## ?? Contributing

### Development Setup
```bash
# Clone repository
git clone <repo-url>
cd chartanalyst

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8

# Run tests
pytest test_chartanalyst.py -v
```

### Adding New Patterns
```python
class PatternDetector:
    def detect_custom_pattern(self, df: pd.DataFrame) -> bool:
        """Add your custom pattern detection logic"""
        # Your pattern detection code here
        return pattern_detected
        
    def _determine_primary_pattern(self, candlestick_patterns, chart_patterns):
        # Add your custom pattern to the priority list
        if 'YOUR_CUSTOM_PATTERN' in candlestick_patterns:
            return "Your Custom Pattern"
        # ... existing logic
```

## ?? Performance

### Benchmarks
- **Pattern Detection**: ~50ms per symbol (100 candles)
- **Data Fetching**: ~200ms per symbol (network dependent)  
- **Memory Usage**: ~50MB per ChartAnalyst instance
- **Throughput**: ~100 symbols/minute (single thread)

### Optimization Tips
```python
# Batch analysis for better performance
symbols = ["BTCUSDT", "ETHUSDT", "AAPL", "TSLA"]
signals = []

for symbol in symbols:
    signal = analyst.analyze_symbol(symbol, "1h")
    if signal:
        signals.append(signal)

# Use async for concurrent analysis
import asyncio

async def analyze_concurrent(symbols):
    tasks = [analyst.run_analysis(symbol, "1h") for symbol in symbols]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r]
```

## ?? License

This project is licensed under the MIT License - see the LICENSE file for details.

## ?? Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: This README + inline code comments
- **Examples**: See `test_chartanalyst.py` for usage examples

## ?? Roadmap

- [ ] **Machine Learning Enhancement**: Pattern success rate learning
- [ ] **More Data Sources**: Alpha Vantage, IEX Cloud, Quandl
- [ ] **Advanced Patterns**: Elliott Wave, Fibonacci retracements
- [ ] **Performance Monitoring**: Pattern success rate tracking
- [ ] **WebSocket Streaming**: Real-time pattern detection
- [ ] **Alert System**: Discord/Slack/Email notifications
- [ ] **Web Dashboard**: Real-time pattern visualization

---

**Built with ❤️ for algorithmic traders and technical analysts**

For questions, feature requests, or contributions, please open an issue or submit a pull request!
