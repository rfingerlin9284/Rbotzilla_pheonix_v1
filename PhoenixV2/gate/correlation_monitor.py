"""
PhoenixV2 Gate Module - Correlation Monitor

Prevents opening positions that are highly correlated with existing positions.
This reduces portfolio risk by avoiding doubling down on the same market move.
"""
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger("CorrelationMonitor")

# Known correlation pairs (positive correlation > 0.7)
# When you're long one, being long the other is doubling down
POSITIVE_CORRELATIONS = {
    # Major USD pairs move together
    "EUR_USD": ["GBP_USD", "AUD_USD", "NZD_USD"],
    "GBP_USD": ["EUR_USD", "AUD_USD"],
    "AUD_USD": ["NZD_USD", "EUR_USD", "GBP_USD"],
    "NZD_USD": ["AUD_USD"],
    
    # JPY pairs (risk-off correlations)
    "USD_JPY": ["EUR_JPY", "GBP_JPY", "AUD_JPY"],
    "EUR_JPY": ["USD_JPY", "GBP_JPY"],
    "GBP_JPY": ["EUR_JPY", "USD_JPY"],
    
    # Commodity currencies
    "USD_CAD": ["USD_NOK"],  # Oil correlation
    
    # Crypto correlations
    "BTC-USD": ["ETH-USD"],
    "ETH-USD": ["BTC-USD"],
}

# Inverse correlations (negative correlation < -0.7)
# When you're long one, being short the other is also doubling down
INVERSE_CORRELATIONS = {
    "EUR_USD": ["USD_CHF"],
    "USD_CHF": ["EUR_USD"],
    "AUD_USD": ["USD_CAD"],  # Risk-on vs oil
}


class CorrelationMonitor:
    """
    Monitors portfolio for correlation risk.
    Prevents opening positions that would increase correlation exposure.
    """
    
    def __init__(self, max_correlated_positions: int = 2):
        self.max_correlated = max_correlated_positions

    def check_correlation(self, new_symbol: str, new_direction: str, 
                         current_positions: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Check if opening a new position would violate correlation limits.
        
        Args:
            new_symbol: The symbol to trade (e.g., "EUR_USD")
            new_direction: "BUY" or "SELL"
            current_positions: List of current position dicts with 'instrument' and 'currentUnits'
        
        Returns:
            Tuple of (is_allowed: bool, reason: str)
        """
        if not current_positions:
            return True, "No existing positions"
        
        # Extract current position info
        current_symbols = {}
        for pos in current_positions:
            symbol = pos.get('instrument', pos.get('symbol', ''))
            units = float(pos.get('currentUnits', pos.get('units', 0)))
            if symbol:
                current_symbols[symbol] = "LONG" if units > 0 else "SHORT"
        
        # Check for direct duplicate
        if new_symbol in current_symbols:
            existing_dir = current_symbols[new_symbol]
            if existing_dir == new_direction:
                return False, f"DUPLICATE_POSITION_{new_symbol}"
            else:
                # Opening opposite direction = closing, which is fine
                return True, "Closing existing position"
        
        # Check positive correlations
        correlated_pairs = POSITIVE_CORRELATIONS.get(new_symbol, [])
        same_direction_count = 0
        
        for corr_symbol in correlated_pairs:
            if corr_symbol in current_symbols:
                if current_symbols[corr_symbol] == new_direction:
                    same_direction_count += 1
                    logger.debug(f"Correlation found: {new_symbol} <-> {corr_symbol} (same direction)")
        
        if same_direction_count >= self.max_correlated:
            return False, f"CORRELATION_LIMIT_{same_direction_count}_SAME_DIRECTION"
        
        # Check inverse correlations
        inverse_pairs = INVERSE_CORRELATIONS.get(new_symbol, [])
        # Fix: Use BUY/SELL to match input format (was LONG/SHORT)
        inverse_direction = "SELL" if new_direction == "BUY" else "BUY"
        
        for inv_symbol in inverse_pairs:
            if inv_symbol in current_symbols:
                if current_symbols[inv_symbol] == inverse_direction:
                    same_direction_count += 1
                    logger.debug(f"Inverse correlation found: {new_symbol} <-> {inv_symbol}")
        
        if same_direction_count >= self.max_correlated:
            return False, f"INVERSE_CORRELATION_LIMIT"
        
        return True, f"ALLOWED ({same_direction_count} correlated)"

    def get_correlation_exposure(self, positions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Analyze current portfolio for correlation clusters.
        
        Returns dict mapping correlation groups to list of held symbols.
        """
        exposure = {
            "USD_LONG": [],
            "USD_SHORT": [],
            "JPY_RISK": [],
            "COMMODITY": [],
            "CRYPTO": []
        }
        
        for pos in positions:
            symbol = pos.get('instrument', pos.get('symbol', ''))
            units = float(pos.get('currentUnits', pos.get('units', 0)))
            direction = "LONG" if units > 0 else "SHORT"
            
            # Categorize
            if symbol.startswith(("EUR_USD", "GBP_USD", "AUD_USD", "NZD_USD")):
                if direction == "LONG":
                    exposure["USD_SHORT"].append(symbol)  # Long EUR/USD = Short USD
                else:
                    exposure["USD_LONG"].append(symbol)
            elif symbol.startswith("USD_"):
                if direction == "LONG":
                    exposure["USD_LONG"].append(symbol)
                else:
                    exposure["USD_SHORT"].append(symbol)
            elif "JPY" in symbol:
                exposure["JPY_RISK"].append(f"{symbol}:{direction}")
            elif "-" in symbol:  # Crypto
                exposure["CRYPTO"].append(f"{symbol}:{direction}")
        
        return exposure
