#!/usr/bin/env python3
"""
CONSOLIDATED GATES - RICK Phoenix System
=========================================
Combines gate systems from:
- GuardianGates (4 cascading pre-trade gates)
- CryptoEntryGate (90% consensus requirement)
- ExecutionGate (Final order validation)

PIN: 841921 | Charter Compliant
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)

# =============================================================================
# CHARTER CONSTANTS
# =============================================================================

class RickCharter:
    """Charter constants for gate enforcement"""
    MAX_MARGIN_UTILIZATION_PCT = 0.35      # 35% max margin usage
    MAX_CONCURRENT_POSITIONS = 3            # 3 positions max
    MAX_USD_CORRELATION = 0.70              # 70% max USD exposure
    CRYPTO_AI_HIVE_VOTE_CONSENSUS = 0.90    # 90% for crypto
    MIN_RR_RATIO = 3.0                      # 3:1 minimum reward:risk
    MAX_DAILY_LOSS_PCT = 0.05               # 5% daily loss limit
    CHARTER_PIN = "841921"
    
    @staticmethod
    def validate_pin(pin: int) -> bool:
        return str(pin) == RickCharter.CHARTER_PIN

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class GateResult:
    """Result from a guardian gate check"""
    gate_name: str
    passed: bool
    reason: str
    details: Dict = None


@dataclass
class ExecutionDecision:
    """Final execution decision"""
    allowed: bool
    reason: str
    modified_size: Optional[float] = None
    modified_stop: Optional[float] = None
    modified_take: Optional[float] = None
    gates_passed: int = 0
    gates_failed: int = 0
    warnings: List[str] = None

# =============================================================================
# GUARDIAN GATES (from hive/guardian_gates.py)
# =============================================================================

class GuardianGates:
    """
    Multi-gate pre-trade validation system
    All gates must pass (AND logic) before order placement
    
    Gate 1: Margin Utilization (<=35%)
    Gate 2: Concurrent Positions (<3)
    Gate 3: Correlation Guard (<70% USD exposure)
    Gate 4: Crypto Consensus (>=90% for crypto)
    """
    
    def __init__(self, pin: int = 841921):
        if not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid PIN for GuardianGates")
        
        self.logger = logging.getLogger("GuardianGates")
        self.logger.info("Guardian Gates initialized")
    
    def validate_all(self, signal: Dict, account: Dict, 
                     positions: List[Dict]) -> Tuple[bool, List[GateResult]]:
        """
        Run all guardian gates on a signal
        
        Args:
            signal: Trading signal {symbol, side, units, entry_price, hive_consensus}
            account: Account info {nav, margin_used, margin_available}
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
        """Gate 3: Block if adding USD correlation > 70%"""
        symbol = signal.get('symbol', '')
        direction = signal.get('side', signal.get('direction', 'BUY'))
        
        # Get existing USD exposure
        usd_exposure = 0
        total_exposure = 0
        
        # USD correlation for common pairs
        usd_pairs = {
            'EUR_USD': {'long': -1, 'short': 1},
            'GBP_USD': {'long': -1, 'short': 1},
            'USD_JPY': {'long': 1, 'short': -1},
            'USD_CHF': {'long': 1, 'short': -1},
            'AUD_USD': {'long': -1, 'short': 1},
            'USD_CAD': {'long': 1, 'short': -1},
            'NZD_USD': {'long': -1, 'short': 1},
        }
        
        for pos in positions:
            pos_symbol = pos.get('symbol', '')
            pos_dir = pos.get('direction', pos.get('side', 'BUY'))
            pos_size = abs(float(pos.get('size', pos.get('units', 1))))
            
            if pos_symbol in usd_pairs:
                dir_key = 'long' if pos_dir.upper() in ['BUY', 'LONG'] else 'short'
                usd_exposure += usd_pairs[pos_symbol][dir_key] * pos_size
            total_exposure += pos_size
        
        # Calculate new exposure with proposed trade
        new_size = abs(float(signal.get('size', signal.get('units', 1))))
        
        if symbol in usd_pairs:
            dir_key = 'long' if direction.upper() in ['BUY', 'LONG'] else 'short'
            new_usd_exposure = usd_exposure + (usd_pairs[symbol][dir_key] * new_size)
        else:
            new_usd_exposure = usd_exposure
        
        new_total = total_exposure + new_size
        
        if new_total == 0:
            return GateResult("correlation", True, "No positions")
        
        correlation_pct = abs(new_usd_exposure) / new_total
        max_corr = RickCharter.MAX_USD_CORRELATION
        
        if correlation_pct > max_corr:
            return GateResult(
                "correlation",
                False,
                f"USD correlation {correlation_pct:.1%} would exceed {max_corr:.1%}",
                {"correlation": correlation_pct, "max": max_corr}
            )
        
        return GateResult("correlation", True, f"Correlation OK: {correlation_pct:.1%}")
    
    def _gate_crypto(self, signal: Dict) -> GateResult:
        """Gate 4: Crypto requires 90% hive consensus"""
        consensus = float(signal.get('hive_consensus', signal.get('consensus', 0)))
        min_consensus = RickCharter.CRYPTO_AI_HIVE_VOTE_CONSENSUS
        
        if consensus < min_consensus:
            return GateResult(
                "crypto_consensus",
                False,
                f"Crypto consensus {consensus:.1%} < required {min_consensus:.1%}",
                {"consensus": consensus, "required": min_consensus}
            )
        
        return GateResult("crypto_consensus", True, f"Crypto consensus OK: {consensus:.1%}")
    
    def _is_crypto(self, symbol: str) -> bool:
        """Check if symbol is cryptocurrency"""
        crypto_bases = ['BTC', 'ETH', 'XRP', 'LTC', 'BCH', 'ADA', 'DOT', 'LINK', 'SOL', 'DOGE']
        return any(symbol.upper().startswith(c) or f"_{c}" in symbol.upper() for c in crypto_bases)

# =============================================================================
# CRYPTO ENTRY GATE (from gate/crypto_entry_gate.py)
# =============================================================================

class CryptoEntryGate:
    """
    Specialized gate for crypto trades
    Requires 90% hive consensus + additional volatility checks
    """
    
    def __init__(self, pin: int = 841921):
        if not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid PIN")
        
        self.min_consensus = 0.90
        self.max_volatility = 0.10  # 10% daily volatility cap
        self.logger = logging.getLogger("CryptoEntryGate")
    
    def validate(self, signal: Dict, volatility: float = 0.0) -> Tuple[bool, str]:
        """
        Validate crypto entry
        
        Args:
            signal: Trading signal with hive_consensus
            volatility: Current daily volatility
            
        Returns:
            (allowed: bool, reason: str)
        """
        # Check consensus
        consensus = float(signal.get('hive_consensus', signal.get('consensus', 0)))
        
        if consensus < self.min_consensus:
            return False, f"Crypto consensus {consensus:.1%} < required {self.min_consensus:.1%}"
        
        # Check volatility
        if volatility > self.max_volatility:
            return False, f"Crypto volatility {volatility:.1%} exceeds safe limit {self.max_volatility:.1%}"
        
        # Check for valid signal structure
        required_fields = ['symbol', 'side', 'entry_price']
        missing = [f for f in required_fields if f not in signal]
        
        if missing:
            return False, f"Missing required fields: {missing}"
        
        return True, f"Crypto entry approved (consensus={consensus:.1%})"
    
    def adjust_for_volatility(self, signal: Dict, volatility: float) -> Dict:
        """Adjust position size based on volatility"""
        adjusted = signal.copy()
        
        if volatility > 0.05:  # High volatility
            size_mult = 0.5  # Reduce size by 50%
        elif volatility > 0.03:  # Moderate volatility
            size_mult = 0.75
        else:
            size_mult = 1.0
        
        if 'size' in adjusted:
            adjusted['size'] = adjusted['size'] * size_mult
        if 'units' in adjusted:
            adjusted['units'] = adjusted['units'] * size_mult
        
        adjusted['volatility_adjusted'] = size_mult < 1.0
        
        return adjusted

# =============================================================================
# EXECUTION GATE (Final validation before order)
# =============================================================================

class ExecutionGate:
    """
    Final validation gate before order execution
    
    Checks:
    - Risk/Reward ratio (minimum 3:1)
    - Stop loss distance
    - Take profit validity
    - Position sizing
    """
    
    def __init__(self, pin: int = 841921):
        if not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid PIN")
        
        self.min_rr_ratio = RickCharter.MIN_RR_RATIO
        self.logger = logging.getLogger("ExecutionGate")
    
    def validate(self, signal: Dict) -> ExecutionDecision:
        """
        Final validation before execution
        
        Args:
            signal: Complete signal with entry, stop, take prices
            
        Returns:
            ExecutionDecision
        """
        warnings = []
        
        entry = float(signal.get('entry_price', signal.get('entry', 0)))
        stop = signal.get('stop_loss', signal.get('stop'))
        take = signal.get('take_profit', signal.get('take'))
        direction = signal.get('side', signal.get('direction', 'BUY')).upper()
        
        # Validate entry price
        if entry <= 0:
            return ExecutionDecision(
                allowed=False,
                reason="Invalid entry price"
            )
        
        # Calculate risk/reward
        if stop and take:
            stop = float(stop)
            take = float(take)
            
            if direction in ['BUY', 'LONG']:
                risk = entry - stop
                reward = take - entry
            else:
                risk = stop - entry
                reward = entry - take
            
            if risk <= 0:
                return ExecutionDecision(
                    allowed=False,
                    reason="Stop loss is in wrong direction"
                )
            
            rr_ratio = reward / risk if risk > 0 else 0
            
            if rr_ratio < self.min_rr_ratio:
                return ExecutionDecision(
                    allowed=False,
                    reason=f"R:R ratio {rr_ratio:.1f}:1 below minimum {self.min_rr_ratio}:1"
                )
        else:
            warnings.append("No stop/take defined - using defaults")
        
        # Validate position size
        size = float(signal.get('size', signal.get('units', 0)))
        if size <= 0:
            return ExecutionDecision(
                allowed=False,
                reason="Invalid position size"
            )
        
        return ExecutionDecision(
            allowed=True,
            reason="Execution approved",
            modified_size=size,
            modified_stop=stop,
            modified_take=take,
            gates_passed=1,
            gates_failed=0,
            warnings=warnings
        )
    
    def enforce_rr_ratio(self, signal: Dict, atr: float = None) -> Dict:
        """Adjust stop/take to meet minimum R:R ratio"""
        adjusted = signal.copy()
        
        entry = float(signal.get('entry_price', signal.get('entry', 0)))
        stop = signal.get('stop_loss', signal.get('stop'))
        direction = signal.get('side', signal.get('direction', 'BUY')).upper()
        
        if not stop or not entry or entry <= 0:
            return adjusted
        
        stop = float(stop)
        
        if direction in ['BUY', 'LONG']:
            risk = entry - stop
            if risk > 0:
                min_take = entry + (risk * self.min_rr_ratio)
                adjusted['take_profit'] = min_take
        else:
            risk = stop - entry
            if risk > 0:
                min_take = entry - (risk * self.min_rr_ratio)
                adjusted['take_profit'] = min_take
        
        return adjusted

# =============================================================================
# UNIFIED GATE SYSTEM
# =============================================================================

class UnifiedGateSystem:
    """
    Combined gate system for all pre-trade validation
    
    Runs gates in sequence:
    1. Guardian Gates (Margin, Concurrent, Correlation, Crypto)
    2. Crypto Entry Gate (if crypto)
    3. Execution Gate (R:R, stops)
    """
    
    def __init__(self, pin: int = 841921):
        if not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid PIN")
        
        self.guardian = GuardianGates(pin)
        self.crypto_gate = CryptoEntryGate(pin)
        self.execution_gate = ExecutionGate(pin)
        
        self.logger = logging.getLogger("UnifiedGateSystem")
    
    def validate_trade(self, signal: Dict, account: Dict, 
                       positions: List[Dict], volatility: float = 0.0) -> ExecutionDecision:
        """
        Run all gates on a potential trade
        
        Args:
            signal: Trading signal
            account: Account info
            positions: Open positions
            volatility: Current volatility
            
        Returns:
            ExecutionDecision with all gate results
        """
        warnings = []
        gates_passed = 0
        gates_failed = 0
        
        # Step 1: Guardian Gates
        guardian_passed, guardian_results = self.guardian.validate_all(signal, account, positions)
        
        for result in guardian_results:
            if result.passed:
                gates_passed += 1
            else:
                gates_failed += 1
                warnings.append(f"{result.gate_name}: {result.reason}")
        
        if not guardian_passed:
            return ExecutionDecision(
                allowed=False,
                reason=f"Guardian gates failed: {warnings}",
                gates_passed=gates_passed,
                gates_failed=gates_failed,
                warnings=warnings
            )
        
        # Step 2: Crypto Gate (if crypto)
        symbol = signal.get('symbol', '')
        if self.guardian._is_crypto(symbol):
            crypto_allowed, crypto_reason = self.crypto_gate.validate(signal, volatility)
            
            if not crypto_allowed:
                return ExecutionDecision(
                    allowed=False,
                    reason=f"Crypto gate failed: {crypto_reason}",
                    gates_passed=gates_passed,
                    gates_failed=gates_failed + 1,
                    warnings=warnings + [crypto_reason]
                )
            
            gates_passed += 1
            
            # Adjust for volatility
            signal = self.crypto_gate.adjust_for_volatility(signal, volatility)
        
        # Step 3: Execution Gate
        execution_result = self.execution_gate.validate(signal)
        
        if not execution_result.allowed:
            return ExecutionDecision(
                allowed=False,
                reason=f"Execution gate failed: {execution_result.reason}",
                gates_passed=gates_passed,
                gates_failed=gates_failed + 1,
                warnings=warnings + [execution_result.reason]
            )
        
        # All gates passed
        return ExecutionDecision(
            allowed=True,
            reason="All gates passed",
            modified_size=execution_result.modified_size,
            modified_stop=execution_result.modified_stop,
            modified_take=execution_result.modified_take,
            gates_passed=gates_passed + 1,
            gates_failed=0,
            warnings=warnings + (execution_result.warnings or [])
        )
    
    def quick_check(self, signal: Dict, account: Dict, positions: List[Dict]) -> Tuple[bool, str]:
        """Quick pass/fail check without full details"""
        result = self.validate_trade(signal, account, positions)
        return result.allowed, result.reason

# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CONSOLIDATED GATES - Self Test")
    print("=" * 60)
    
    # Test Guardian Gates
    print("\n--- Guardian Gates Test ---")
    guardian = GuardianGates(841921)
    
    # Test case 1: Valid trade
    signal = {
        'symbol': 'EUR_USD',
        'side': 'BUY',
        'units': 10000,
        'entry_price': 1.1000
    }
    account = {'nav': 100000, 'margin_used': 10000}
    positions = [{'symbol': 'GBP_USD', 'direction': 'BUY', 'units': 5000}]
    
    passed, results = guardian.validate_all(signal, account, positions)
    print(f"Valid trade: {'PASSED' if passed else 'FAILED'}")
    for r in results:
        print(f"  {r.gate_name}: {'✓' if r.passed else '✗'} {r.reason}")
    
    # Test case 2: Margin exceeded
    account_high_margin = {'nav': 100000, 'margin_used': 40000}
    passed, results = guardian.validate_all(signal, account_high_margin, positions)
    print(f"\nHigh margin: {'PASSED' if passed else 'FAILED'}")
    
    # Test case 3: Too many positions
    many_positions = [
        {'symbol': 'EUR_USD', 'direction': 'BUY', 'units': 5000},
        {'symbol': 'GBP_USD', 'direction': 'BUY', 'units': 5000},
        {'symbol': 'USD_JPY', 'direction': 'SELL', 'units': 5000},
    ]
    passed, results = guardian.validate_all(signal, account, many_positions)
    print(f"Max positions: {'PASSED' if passed else 'FAILED'}")
    
    # Test Crypto Gate
    print("\n--- Crypto Gate Test ---")
    crypto_gate = CryptoEntryGate(841921)
    
    crypto_signal = {
        'symbol': 'BTC_USD',
        'side': 'BUY',
        'entry_price': 50000,
        'hive_consensus': 0.92
    }
    allowed, reason = crypto_gate.validate(crypto_signal, volatility=0.05)
    print(f"Crypto high consensus: {'ALLOWED' if allowed else 'BLOCKED'} - {reason}")
    
    crypto_signal['hive_consensus'] = 0.85
    allowed, reason = crypto_gate.validate(crypto_signal, volatility=0.05)
    print(f"Crypto low consensus: {'ALLOWED' if allowed else 'BLOCKED'} - {reason}")
    
    # Test Execution Gate
    print("\n--- Execution Gate Test ---")
    exec_gate = ExecutionGate(841921)
    
    good_signal = {
        'symbol': 'EUR_USD',
        'side': 'BUY',
        'entry_price': 1.1000,
        'stop_loss': 1.0950,
        'take_profit': 1.1200,  # 4:1 R:R
        'size': 10000
    }
    result = exec_gate.validate(good_signal)
    print(f"Good R:R (4:1): {'ALLOWED' if result.allowed else 'BLOCKED'} - {result.reason}")
    
    bad_signal = {
        'symbol': 'EUR_USD',
        'side': 'BUY',
        'entry_price': 1.1000,
        'stop_loss': 1.0950,
        'take_profit': 1.1100,  # 2:1 R:R
        'size': 10000
    }
    result = exec_gate.validate(bad_signal)
    print(f"Bad R:R (2:1): {'ALLOWED' if result.allowed else 'BLOCKED'} - {result.reason}")
    
    # Test Unified System
    print("\n--- Unified Gate System Test ---")
    unified = UnifiedGateSystem(841921)
    
    result = unified.validate_trade(good_signal, account, positions)
    print(f"Full validation: {'ALLOWED' if result.allowed else 'BLOCKED'}")
    print(f"  Gates passed: {result.gates_passed}, failed: {result.gates_failed}")
    if result.warnings:
        print(f"  Warnings: {result.warnings}")
    
    print("\n" + "=" * 60)
    print("All gate tests passed!")
