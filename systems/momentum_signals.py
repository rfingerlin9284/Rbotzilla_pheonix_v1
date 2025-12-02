"""Momentum-based signal generator for RICK system
Charter-compliant: M15 candles, trend + momentum confirmation
PIN: 841921 - No random entries allowed
"""

def _sma(seq, n):
    """Simple Moving Average"""
    return sum(seq[-n:]) / n if len(seq) >= n else sum(seq)/max(len(seq),1)

def _mom(seq, n=10):
    """Momentum (rate of change over n periods)"""
    if len(seq) <= n: 
        return 0.0
    a, b = float(seq[-n-1]), float(seq[-1])
    return (b-a)/max(abs(a),1e-9) * 100.0

def generate_signal(symbol, candles):
    """Generate BUY/SELL signal with confidence
    
    Args:
        symbol: Trading pair (e.g., "EUR_USD")
        candles: List of OANDA candle dicts with 'mid': {'c': close_price}
        
    Returns:
        (signal, confidence) where:
            signal: "BUY", "SELL", or None
            confidence: 0.0 to 1.0
    """
    # Extract closes from OANDA candle format
    closes = []
    for c in candles:
        if isinstance(c, dict):
            if 'mid' in c and 'c' in c['mid']:
                closes.append(float(c['mid']['c']))
            elif 'close' in c:
                closes.append(float(c['close']))
    
    closes = [x for x in closes if x > 0][-100:]  # Last 100 valid closes
    
    if len(closes) < 30:
        return (None, 0.0)
    
    # Calculate indicators
    s20 = _sma(closes, 20)
    s50 = _sma(closes, 50)
    m10 = _mom(closes, 10)
    
    # Trend + momentum confirmation
    if s20 > s50 and m10 > 0.15:  # Bullish trend + positive momentum
        confidence = min(abs(m10)/2, 1.0)
        return ("BUY", confidence)
    
    if s20 < s50 and m10 < -0.15:  # Bearish trend + negative momentum
        confidence = min(abs(m10)/2, 1.0)
        return ("SELL", confidence)
    
    return (None, 0.0)
