#!/usr/bin/env python3
"""
RICK System - Execution Gate
============================
Final checkpoint before orders reach the broker.
Enforces PIN verification, leverage limits, micro-trading gates, and mode checks.

AUTH CODE: 841921
CHARTER: All trades must pass this gate before execution.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RICK.ExecutionGate")


class TradingMode(Enum):
    """Trading environment modes."""
    PAPER = "paper"
    LIVE = "live"
    SANDBOX = "sandbox"
    DISABLED = "disabled"


class GateDecision(Enum):
    """Execution gate decisions."""
    APPROVED = "APPROVED"
    REJECTED_PIN = "REJECTED_PIN"
    REJECTED_LEVERAGE = "REJECTED_LEVERAGE"
    REJECTED_MICRO = "REJECTED_MICRO"
    REJECTED_MODE = "REJECTED_MODE"
    REJECTED_RISK = "REJECTED_RISK"
    REJECTED_NOTIONAL = "REJECTED_NOTIONAL"
    REJECTED_DISABLED = "REJECTED_DISABLED"


@dataclass
class OrderRequest:
    """Represents an order request to be gated."""
    symbol: str
    direction: str  # "BUY" or "SELL"
    units: float
    entry_price: float
    stop_loss: float
    take_profit: float
    leverage: float = 1.0
    account_id: str = ""
    strategy_name: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def notional_value(self) -> float:
        """Calculate notional value of the order."""
        return abs(self.units * self.entry_price)
    
    @property
    def risk_reward_ratio(self) -> float:
        """Calculate R:R ratio."""
        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.take_profit - self.entry_price)
        return reward / risk if risk > 0 else 0.0


@dataclass
class GateResult:
    """Result of execution gate check."""
    decision: GateDecision
    order: OrderRequest
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    pin_verified: bool = False
    mode: TradingMode = TradingMode.PAPER
    
    @property
    def is_approved(self) -> bool:
        return self.decision == GateDecision.APPROVED
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "symbol": self.order.symbol,
            "units": self.order.units,
            "notional": self.order.notional_value,
            "leverage": self.order.leverage,
            "reason": self.reason,
            "pin_verified": self.pin_verified,
            "mode": self.mode.value,
            "timestamp": self.timestamp.isoformat()
        }


class AuthManager:
    """
    Authentication manager for trading mode and PIN verification.
    Reads from environment variables.
    """
    
    CHARTER_PIN = 841921  # Immutable
    
    def __init__(self):
        self.mode = self._detect_mode()
        self._pin_from_env = self._load_pin()
        logger.info(f"🔐 AuthManager initialized - Mode: {self.mode.value}")
    
    def _detect_mode(self) -> TradingMode:
        """Detect trading mode from environment."""
        env_mode = os.getenv("TRADING_ENVIRONMENT", "paper").lower()
        ib_mode = os.getenv("IB_TRADING_MODE", "paper").lower()
        
        # Map environment values to TradingMode
        mode_map = {
            "live": TradingMode.LIVE,
            "paper": TradingMode.PAPER,
            "sandbox": TradingMode.SANDBOX,
            "practice": TradingMode.PAPER,
            "disabled": TradingMode.DISABLED
        }
        
        detected = mode_map.get(env_mode, TradingMode.PAPER)
        
        # Cross-check with IB mode if different
        ib_detected = mode_map.get(ib_mode, TradingMode.PAPER)
        if detected == TradingMode.LIVE and ib_detected != TradingMode.LIVE:
            logger.warning("⚠️ Mode mismatch: TRADING_ENVIRONMENT=live but IB_TRADING_MODE!=live")
        
        return detected
    
    def _load_pin(self) -> int:
        """Load PIN from environment."""
        try:
            return int(os.getenv("RICK_PIN", "0"))
        except ValueError:
            return 0
    
    def verify_pin(self, pin: int) -> bool:
        """Verify PIN against Charter PIN."""
        return pin == self.CHARTER_PIN
    
    def is_live(self) -> bool:
        """Check if we're in live trading mode."""
        return self.mode == TradingMode.LIVE
    
    def is_paper(self) -> bool:
        """Check if we're in paper/practice mode."""
        return self.mode in (TradingMode.PAPER, TradingMode.SANDBOX)
    
    def get_mode(self) -> TradingMode:
        """Get current trading mode."""
        return self.mode


class ExecutionGate:
    """
    Final checkpoint before order execution.
    
    ENFORCES:
    - PIN verification for high-leverage trades (>10x)
    - PAPER vs LIVE mode restrictions
    - Micro-trading gate (minimum 1000 units unless override)
    - Minimum notional value ($1000 paper, $15000 live)
    - Maximum leverage limits
    """
    
    # CHARTER CONSTANTS - Immutable
    AUTH_PIN = 841921
    MAX_LEVERAGE_NO_PIN = 10.0
    MAX_LEVERAGE_WITH_PIN = 50.0
    MIN_UNITS_STANDARD = 1000
    MIN_NOTIONAL_PAPER = 1000.0
    MIN_NOTIONAL_LIVE = 15000.0
    MIN_RISK_REWARD = 3.0
    
    def __init__(self):
        """Initialize the execution gate."""
        self.auth_manager = AuthManager()
        self.allow_micro_trading = self._load_micro_override()
        self.gate_log: list = []
        
        # Load overrides from environment
        self.min_units = int(os.getenv("MIN_ORDER_UNITS", self.MIN_UNITS_STANDARD))
        
        logger.info(f"🚧 ExecutionGate initialized")
        logger.info(f"   - Trading Mode: {self.auth_manager.get_mode().value}")
        logger.info(f"   - Micro Trading: {'ALLOWED' if self.allow_micro_trading else 'BLOCKED'}")
        logger.info(f"   - Min Units: {self.min_units}")
        logger.info(f"   - Max Leverage (no PIN): {self.MAX_LEVERAGE_NO_PIN}x")
    
    def _load_micro_override(self) -> bool:
        """Check if micro trading is explicitly allowed."""
        override = os.getenv("ALLOW_MICRO_TRADING", "false").lower()
        return override in ("true", "1", "yes")
    
    def _get_min_notional(self) -> float:
        """Get minimum notional based on trading mode."""
        if self.auth_manager.is_live():
            return self.MIN_NOTIONAL_LIVE
        return self.MIN_NOTIONAL_PAPER
    
    def _check_pin_required(self, order: OrderRequest) -> Tuple[bool, bool]:
        """
        Check if PIN is required and if it's valid.
        Returns: (pin_required, pin_valid)
        """
        pin_required = order.leverage > self.MAX_LEVERAGE_NO_PIN
        
        if not pin_required:
            return False, True  # No PIN needed, consider valid
        
        # Check PIN from environment
        pin_valid = self.auth_manager.verify_pin(self.auth_manager._pin_from_env)
        return True, pin_valid
    
    def _check_leverage(self, order: OrderRequest, pin_verified: bool) -> Tuple[bool, str]:
        """
        Validate leverage limits.
        Returns: (is_valid, reason)
        """
        max_allowed = self.MAX_LEVERAGE_WITH_PIN if pin_verified else self.MAX_LEVERAGE_NO_PIN
        
        if order.leverage > max_allowed:
            return False, f"Leverage {order.leverage}x exceeds max {max_allowed}x"
        
        if order.leverage > self.MAX_LEVERAGE_NO_PIN and not pin_verified:
            return False, f"High leverage ({order.leverage}x) requires PIN verification"
        
        return True, "Leverage OK"
    
    def _check_micro_trading(self, order: OrderRequest) -> Tuple[bool, str]:
        """
        Validate micro trading gate.
        Returns: (is_valid, reason)
        """
        if self.allow_micro_trading:
            return True, "Micro trading override active"
        
        if abs(order.units) < self.min_units:
            return False, f"Order size {order.units} below minimum {self.min_units} units"
        
        return True, "Order size OK"
    
    def _check_notional(self, order: OrderRequest) -> Tuple[bool, str]:
        """
        Validate minimum notional value.
        Returns: (is_valid, reason)
        """
        min_notional = self._get_min_notional()
        notional = order.notional_value
        
        if notional < min_notional:
            return False, f"Notional ${notional:.2f} below minimum ${min_notional:.2f}"
        
        return True, f"Notional OK (${notional:.2f})"
    
    def _check_risk_reward(self, order: OrderRequest) -> Tuple[bool, str]:
        """
        Validate risk/reward ratio.
        Returns: (is_valid, reason)
        """
        rr = order.risk_reward_ratio
        if rr < self.MIN_RISK_REWARD:
            return False, f"R:R {rr:.2f} below minimum {self.MIN_RISK_REWARD}"
        return True, f"R:R OK ({rr:.2f})"
    
    def _check_mode_restrictions(self, order: OrderRequest) -> Tuple[bool, str]:
        """
        Check mode-specific restrictions.
        Returns: (is_valid, reason)
        """
        mode = self.auth_manager.get_mode()
        
        if mode == TradingMode.DISABLED:
            return False, "Trading is DISABLED"
        
        if mode == TradingMode.LIVE:
            # Additional live trading checks
            if not self.auth_manager.verify_pin(self.auth_manager._pin_from_env):
                return False, "LIVE trading requires valid PIN in environment"
        
        return True, f"Mode OK ({mode.value})"
    
    def evaluate(self, order: OrderRequest, override_pin: Optional[int] = None) -> GateResult:
        """
        Evaluate an order request through all gate checks.
        
        Args:
            order: The order request to evaluate
            override_pin: Optional PIN for high-leverage override
            
        Returns:
            GateResult with decision and details
        """
        logger.info(f"🚧 Evaluating order: {order.symbol} {order.direction} {order.units} units")
        
        # PIN verification
        pin_required, pin_valid = self._check_pin_required(order)
        if override_pin:
            pin_valid = self.auth_manager.verify_pin(override_pin)
        
        # Gate 1: Mode restrictions
        mode_ok, mode_reason = self._check_mode_restrictions(order)
        if not mode_ok:
            result = GateResult(
                decision=GateDecision.REJECTED_MODE,
                order=order,
                reason=mode_reason,
                pin_verified=pin_valid,
                mode=self.auth_manager.get_mode()
            )
            self._log_decision(result)
            return result
        
        # Gate 2: PIN for high leverage
        if pin_required and not pin_valid:
            result = GateResult(
                decision=GateDecision.REJECTED_PIN,
                order=order,
                reason=f"High leverage ({order.leverage}x) requires PIN 841921",
                pin_verified=False,
                mode=self.auth_manager.get_mode()
            )
            self._log_decision(result)
            return result
        
        # Gate 3: Leverage limits
        leverage_ok, leverage_reason = self._check_leverage(order, pin_valid)
        if not leverage_ok:
            result = GateResult(
                decision=GateDecision.REJECTED_LEVERAGE,
                order=order,
                reason=leverage_reason,
                pin_verified=pin_valid,
                mode=self.auth_manager.get_mode()
            )
            self._log_decision(result)
            return result
        
        # Gate 4: Micro trading
        micro_ok, micro_reason = self._check_micro_trading(order)
        if not micro_ok:
            result = GateResult(
                decision=GateDecision.REJECTED_MICRO,
                order=order,
                reason=micro_reason,
                pin_verified=pin_valid,
                mode=self.auth_manager.get_mode()
            )
            self._log_decision(result)
            return result
        
        # Gate 5: Notional value
        notional_ok, notional_reason = self._check_notional(order)
        if not notional_ok:
            result = GateResult(
                decision=GateDecision.REJECTED_NOTIONAL,
                order=order,
                reason=notional_reason,
                pin_verified=pin_valid,
                mode=self.auth_manager.get_mode()
            )
            self._log_decision(result)
            return result
        
        # Gate 6: Risk/Reward
        rr_ok, rr_reason = self._check_risk_reward(order)
        if not rr_ok:
            result = GateResult(
                decision=GateDecision.REJECTED_RISK,
                order=order,
                reason=rr_reason,
                pin_verified=pin_valid,
                mode=self.auth_manager.get_mode()
            )
            self._log_decision(result)
            return result
        
        # ALL GATES PASSED
        result = GateResult(
            decision=GateDecision.APPROVED,
            order=order,
            reason="All gates passed",
            pin_verified=pin_valid,
            mode=self.auth_manager.get_mode()
        )
        self._log_decision(result)
        
        logger.info(f"✅ ORDER APPROVED: {order.symbol} {order.direction} {order.units} units")
        return result
    
    def _log_decision(self, result: GateResult) -> None:
        """Log gate decision for audit trail."""
        self.gate_log.append(result.to_dict())
        
        if result.is_approved:
            logger.info(f"✅ GATE PASSED: {result.order.symbol}")
        else:
            logger.warning(f"🚫 GATE BLOCKED: {result.order.symbol} - {result.reason}")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get gate statistics."""
        stats = {
            "total": len(self.gate_log),
            "approved": 0,
            "rejected_pin": 0,
            "rejected_leverage": 0,
            "rejected_micro": 0,
            "rejected_mode": 0,
            "rejected_risk": 0,
            "rejected_notional": 0
        }
        
        for entry in self.gate_log:
            decision = entry.get("decision", "")
            if decision == "APPROVED":
                stats["approved"] += 1
            elif "PIN" in decision:
                stats["rejected_pin"] += 1
            elif "LEVERAGE" in decision:
                stats["rejected_leverage"] += 1
            elif "MICRO" in decision:
                stats["rejected_micro"] += 1
            elif "MODE" in decision:
                stats["rejected_mode"] += 1
            elif "RISK" in decision:
                stats["rejected_risk"] += 1
            elif "NOTIONAL" in decision:
                stats["rejected_notional"] += 1
        
        return stats
    
    def export_log(self, filepath: str) -> bool:
        """Export gate log to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    "timestamp": datetime.utcnow().isoformat(),
                    "statistics": self.get_statistics(),
                    "log": self.gate_log
                }, f, indent=2)
            logger.info(f"💾 Gate log exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            return False


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
_gate_instance: Optional[ExecutionGate] = None

def get_execution_gate() -> ExecutionGate:
    """Get or create the singleton ExecutionGate instance."""
    global _gate_instance
    if _gate_instance is None:
        _gate_instance = ExecutionGate()
    return _gate_instance


# ============================================================================
# MODULE TEST
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("RICK Execution Gate - Self Test")
    print("=" * 60)
    
    gate = get_execution_gate()
    
    # Test orders
    test_orders = [
        # Should PASS - Standard order
        OrderRequest(
            symbol="EUR_USD", direction="BUY", units=5000,
            entry_price=1.0850, stop_loss=1.0800, take_profit=1.1050,
            leverage=5.0
        ),
        # Should FAIL - Micro trading (< 1000 units)
        OrderRequest(
            symbol="GBP_USD", direction="SELL", units=500,
            entry_price=1.2650, stop_loss=1.2700, take_profit=1.2450,
            leverage=3.0
        ),
        # Should FAIL - High leverage without PIN
        OrderRequest(
            symbol="USD_JPY", direction="BUY", units=10000,
            entry_price=149.50, stop_loss=148.50, take_profit=152.50,
            leverage=25.0
        ),
        # Should FAIL - Poor R:R
        OrderRequest(
            symbol="AUD_USD", direction="BUY", units=5000,
            entry_price=0.6500, stop_loss=0.6450, take_profit=0.6550,
            leverage=5.0
        ),
        # Should PASS - Good order
        OrderRequest(
            symbol="NZD_USD", direction="SELL", units=8000,
            entry_price=0.5900, stop_loss=0.5950, take_profit=0.5700,
            leverage=8.0
        ),
    ]
    
    print("\n" + "=" * 60)
    print("GATE EVALUATION RESULTS")
    print("=" * 60)
    
    for order in test_orders:
        result = gate.evaluate(order)
        status = "✅ APPROVED" if result.is_approved else f"🚫 {result.decision.value}"
        print(f"\n{order.symbol} {order.direction} {order.units} units @ {order.leverage}x leverage")
        print(f"   Decision: {status}")
        print(f"   Reason: {result.reason}")
    
    print("\n" + "=" * 60)
    print("GATE STATISTICS")
    print("=" * 60)
    stats = gate.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\nSelf-test complete.")
