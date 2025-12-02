"""
USD Notional Converter for OANDA Pairs
Handles all pair types: XXX_USD, USD_XXX, and XXX_YYY crosses
PIN: 841921
"""

def get_usd_notional(units: float, instrument: str, entry_price: float, oanda_connector=None) -> float:
    """
    Calculate TRUE USD notional for any OANDA pair.
    """
    base, quote = instrument.split("_")
    units_abs = abs(float(units))
    price = float(entry_price)
    if quote == "USD":
        return units_abs * price
    if base == "USD":
        return units_abs
    notional_in_quote = units_abs * price
    quote_to_usd_rate = None
    if oanda_connector:
        try:
            quote_usd_pair = f"{quote}_USD"
            price_data = oanda_connector.get_current_price(quote_usd_pair)
            if price_data and 'mid' in price_data:
                quote_to_usd_rate = float(price_data['mid'])
        except Exception:
            pass
        if not quote_to_usd_rate:
            try:
                usd_quote_pair = f"USD_{quote}"
                price_data = oanda_connector.get_current_price(usd_quote_pair)
                if price_data and 'mid' in price_data:
                    quote_to_usd_rate = 1.0 / float(price_data['mid'])
            except Exception:
                pass
    if not quote_to_usd_rate:
        FALLBACK_RATES = {
            'AUD': 0.65, 'NZD': 0.60, 'CAD': 0.72, 'CHF': 1.13,
            'JPY': 0.0067, 'GBP': 1.27, 'EUR': 1.08
        }
        quote_to_usd_rate = FALLBACK_RATES.get(quote)
        if not quote_to_usd_rate:
            return None
    return notional_in_quote * quote_to_usd_rate
