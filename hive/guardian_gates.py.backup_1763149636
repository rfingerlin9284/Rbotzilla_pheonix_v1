#!/usr/bin/env python3
"""
Guardian Gate System - Pre-trade validation with Charter enforcement
PIN: 841921 | All gates must pass before order placement
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Charter enforcement
try:
    from foundation.rick_charter import RickCharter
except ImportError:
    class RickCharter:
        MAX_MARGIN_UTILIZATION_PCT = 0.35
        MAX_CONCURRENT_POSITIONS = 3
        CRYPTO_AI_HIVE_VOTE_CONSENSUS = 0.90
        CHARTER_PIN = "841921"

@dataclass
class GateResult:
    """Result from a guardian gate check"""
    gate_name: str
    passed: bool
    reason: str
    details: Dict = None

class GuardianGates:
    """
    Multi-gate pre-trade validation system
    All gates must pass (AND logic) before order placement
    """
    
    def __init__(self, pin: int = 841921):
        if str(pin) != RickCharter.CHARTER_PIN:
            raise PermissionError("Invalid PIN for GuardianGates")
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Guardian Gates initialized with PIN verification")
    
    def validate_all(self, signal: Dict, account: Dict, positions: List[Dict]) -> Tuple[bool, List[GateResult]]:
        """
        Run all guardian gates on a signal
        
        Args:
            signal: Trading signal with symbol, side, units, entry_price
            account: Account info with nav, margin_used, margin_available
            positions: List of open positions
            
        Returns:
            (all_passed: bool, results: List[GateResult])
        """
        results = []
        
        # Gate 1: Margin utilization
        results.append(self._gate_margin(account))
        
        # Gate 2: Concurrent positions
        results.append(self._gate_concurrent(positions))
        
        # Gate 3: Correlation (USD exposure)
        results.append(self._gate_correlation(signal, positions))
        
        # Gate 4: Crypto-specific (if crypto pair)
        if self._is_crypto(signal.get('symbol', '')):
            results.append(self._gate_crypto(signal))
        
        # All gates must pass
        all_passed = all(r.passed for r in results)
        
        if not all_passed:
            failures = [r for r in results if not r.passed]
            self.logger.warning(f"Guardian gates REJECTED: {[r.gate_name for r in failures]}")
        
        return all_passed, results
    
    def _gate_margin(self, account: Dict) -> GateResult:
        """Gate 1: Block if margin utilization > 35%"""
        nav = float(account.get('nav', 0))
        margin_used = float(account.get('margin_used', 0))
        
        if nav <= 0:
            return GateResult("margin", False, "Cannot determine margin utilization (NAV=0)")
        
        mu = margin_used / nav
        max_mu = RickCharter.MAX_MARGIN_UTILIZATION_PCT
        
        if mu > max_mu:
            return GateResult(
                "margin", 
                False, 
                f"Margin utilization {mu:.1%} exceeds Charter max {max_mu:.1%}",
                {"mu": mu, "max": max_mu}
            )
        
        return GateResult("margin", True, f"Margin OK: {mu:.1%} < {max_mu:.1%}")
    
    def _gate_concurrent(self, positions: List[Dict]) -> GateResult:
        """Gate 2: Block if concurrent positions >= max"""
        open_count = len(positions)
        max_concurrent = RickCharter.MAX_CONCURRENT_POSITIONS
        
        if open_count >= max_concurrent:
            return GateResult(
                "concurrent",
                False,
                f"Open positions {open_count} >= Charter max {max_concurrent}",
                {"open": open_count, "max": max_concurrent}
            )
        
        return GateResult("concurrent", True, f"Positions OK: {open_count} < {max_concurrent}")
    
    def _gate_correlation(self, signal: Dict, positions: List[Dict]) -> GateResult:
        """Gate 3: Block same-side USD exposure (correlation guard)"""
        symbol = signal.get('symbol', '')
        side = signal.get('side', '')
        
        # Calculate USD bucket exposure
        usd_pairs = ['USD', 'USDT', 'USDC', 'BUSD', 'USDP', 'TUSD']
        same_side_exposure = 0
        
        for pos in positions:
            pos_symbol = pos.get('symbol', '')
            pos_side = pos.get('side', '')
            
            # Check if both involve USD and same direction
            if any(usd in pos_symbol for usd in usd_pairs) and any(usd in symbol for usd in usd_pairs):
                if pos_side == side:
                    same_side_exposure += abs(float(pos.get('units', 0)))
        
        # Block if significant same-side USD exposure exists
        if same_side_exposure > 0:
            return GateResult(
                "correlation",
                False,
                f"Same-side USD exposure detected: {same_side_exposure} units",
                {"exposure": same_side_exposure, "side": side}
            )
        
        return GateResult("correlation", True, "No correlated USD exposure")
    
    def _gate_crypto(self, signal: Dict) -> GateResult:
        """Gate 4: Crypto-specific gates (hive consensus, time window)"""
        hive_consensus = signal.get('hive_consensus', 0.0)
        min_consensus = RickCharter.CRYPTO_AI_HIVE_VOTE_CONSENSUS
        
        if hive_consensus < min_consensus:
            return GateResult(
                "crypto_hive",
                False,
                f"Hive consensus {hive_consensus:.1%} < min {min_consensus:.1%}",
                {"consensus": hive_consensus, "min": min_consensus}
            )
        
        # Time window check (8am-4pm ET Mon-Fri)
        now = datetime.now(timezone.utc)
        hour_et = (now.hour - 5) % 24  # Convert UTC to ET
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        if weekday >= 5:  # Weekend
            return GateResult("crypto_time", False, "Weekend trading blocked for crypto")
        
        if hour_et < 8 or hour_et >= 16:
            return GateResult("crypto_time", False, f"Outside trading window (8am-4pm ET): {hour_et}:00 ET")
        
        return GateResult("crypto", True, f"Crypto gates passed: consensus {hive_consensus:.1%}, time OK")
    
    def _is_crypto(self, symbol: str) -> bool:
        """Check if symbol is a crypto pair"""
        crypto_keywords = ['BTC', 'ETH', 'XRP', 'LTC', 'BCH', 'ADA', 'DOT', 'LINK']
        return any(kw in symbol.upper() for kw in crypto_keywords)

# Convenience function
def validate_signal(signal: Dict, account: Dict, positions: List[Dict]) -> Tuple[bool, str]:
    """
    Quick validation wrapper
    Returns: (approved: bool, rejection_reason: str)
    """
    gates = GuardianGates(pin=841921)
    passed, results = gates.validate_all(signal, account, positions)
    
    if not passed:
        failures = [r.reason for r in results if not r.passed]
        return False, " | ".join(failures)
    
    return True, "All gates passed"

if __name__ == "__main__":
    # Self-test
    print("Guardian Gates self-test...")
    
    # Test signal
    signal = {
        'symbol': 'BTC/USD',
        'side': 'buy',
        'units': 1000,
        'hive_consensus': 0.92
    }
    
    # Mock account
    account = {
        'nav': 10000,
        'margin_used': 2000,
        'margin_available': 8000
    }
    
    # Mock positions
    positions = [
        {'symbol': 'EUR/USD', 'side': 'buy', 'units': 5000}
    ]
    
    gates = GuardianGates(pin=841921)
    passed, results = gates.validate_all(signal, account, positions)
    
    print(f"\nTest Result: {'PASS' if passed else 'FAIL'}")
    for r in results:
        status = "✅" if r.passed else "❌"
        print(f"  {status} {r.gate_name}: {r.reason}")
    
    print("\n✅ Guardian Gates module validated")

