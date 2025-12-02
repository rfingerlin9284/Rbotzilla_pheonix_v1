# OANDA Integration Assimilation - From RICK_LIVE_CLEAN

## Extracted Configuration

### OANDA Credentials (.env)
```
OANDA_PRACTICE_ACCOUNT_ID=101-001-31210531-002
OANDA_PRACTICE_TOKEN=1a45b898c57f609f329a0af8f2800e7e-6fcc25eef7c3f94ad79acff6d5f6bfaf
OANDA_PRACTICE_BASE_URL=https://api-fxpractice.oanda.com/v3
OANDA_ENV=practice
```

### Live System Architecture
- **Class**: `OandaConnector` (environment-agnostic)
- **Endpoints**: 
  - Practice: `https://api-fxpractice.oanda.com/v3`
  - Live: `https://api-fxtrade.oanda.com/v3`
- **Authentication**: Bearer token in Authorization header
- **Latency Target**: < 300ms execution tracking

### Key Methods from oanda_connector.py
1. **_load_credentials()** - Reads .env file for API token and account ID
2. **_validate_connection()** - Checks credentials are configured
3. **place_oco_order()** - Places One-Cancels-Other bracket orders
4. **get_account()** - Retrieves account balance and positions
5. **get_pricing()** - Real-time pricing for instruments

### Extracted Integration Points
- Charter PIN: 841921 (validated before operations)
- Environment switching: practice/live via OANDA_ENV
- Narration logging: All trades logged to JSONL with timestamps
- OCO support: 3:1 R:R minimum with bracket orders
- Timeout: 5 seconds for API calls
- Thread safety: Lock-protected for concurrent access

## Implementation Strategy for Prototype

### Step 1: Copy Configuration
- Extract .env from RICK_LIVE_CLEAN
- Set OANDA_ENV=practice for paper trading

### Step 2: Implement _update_prices() Replacement
Replace the simulated price generator with:
```python
def _update_prices(self):
    """Fetch real market prices from OANDA API"""
    if not self.oanda_token:
        # Fallback to simulated if not configured
        self._update_prices_simulated()
        return
    
    try:
        params = {
            "instruments": ",".join(self.pairs)
        }
        response = requests.get(
            f"{self.oanda_base}/accounts/{self.oanda_account}/pricing",
            headers={
                "Authorization": f"Bearer {self.oanda_token}",
                "Accept-Datetime-Format": "RFC3339"
            },
            params=params,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            for price in data.get("prices", []):
                pair = price["instrument"]
                self.prices[pair] = {
                    "bid": float(price["bids"][0]["price"]),
                    "ask": float(price["asks"][0]["price"]),
                    "timestamp": price["time"]
                }
    except Exception as e:
        self.logger.warning(f"OANDA price fetch failed: {e}")
```

### Step 3: Charter Enforcement Integration
- PIN 841921 validation before trading
- Audit trail logging with timestamps
- Maximum 6-hour position TTL enforcement
- Minimum 15,000 unit notional validation

### Step 4: Testing Strategy
1. Verify OANDA credentials load correctly
2. Fetch pricing for 5 currency pairs
3. Run enforcement loop with real prices
4. Verify all 10 autopilot rules fire correctly
5. Validate compliance logging

## Files to Modify

### In Prototype:
- `trading_manager/integrated_swarm_manager.py` 
  - Method: `_update_prices()` → Replace with OANDA API call
  - Add: `_load_oanda_credentials()` 
  - Add: Error handling for API failures with fallback to simulated

### To Copy from Live System:
- OANDA connector pattern from `oanda_connector.py`
- Credential loading pattern from `_load_credentials()`
- Environment switching pattern from `mode_manager`

## Next Steps

1. Update `.env` in prototype with OANDA credentials
2. Implement OANDA pricing fetcher
3. Run quick test: `make test` with real prices
4. Verify enforcement loop fires with market volatility
5. Run 1-2 hour extended test with real OANDA data
