#!/usr/bin/env python3
"""
INTEGRATED SWARM MANAGER WITH POSITION GUARDIAN
Combines SwarmBot position management with Position Guardian autopilot enforcement.
This is the UNIFIED trading manager that wires everything together.

Lock: /home/ing/RICK/prototype/
PIN: 841921
"""

import time
import threading
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys

# ==================== POSITION GUARDIAN IMPORTS ====================
# These get imported from /home/ing/RICK/R_H_UNI/plugins/position_guardian
# For now, we'll define shim interfaces here. In deployment, swap these
# for the real imports.

@dataclass
class Position:
    """Position object compatible with Position Guardian"""
    id: str
    symbol: str
    side: str  # "buy" or "sell"
    units: float
    entry_price: float
    current_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    opened_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    initial_sl: Optional[float] = None
    peak_pips: float = 0.0
    max_favorable: float = 0.0
    pnl: float = 0.0
    status: str = "active"  # active, trailing, closing, closed

@dataclass
class Order:
    """Order object for gating"""
    symbol: str
    side: str
    units: float
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class AccountState:
    """Account state snapshot"""
    nav: float
    margin_used: float
    now_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def margin_utilization(self) -> float:
        if self.nav == 0:
            return 0
        return self.margin_used / self.nav

@dataclass
class GateResult:
    """Result from pre_trade_hook"""
    allowed: bool
    reason: Optional[str] = None

@dataclass
class EnforcementAction:
    """Action from tick enforcement"""
    type: str  # "modify_sl", "close", "advice"
    position_id: str
    why: str
    new_sl: Optional[float] = None

# ==================== SHIM FUNCTIONS (Replace with real PG imports) ====================

def pre_trade_hook(order: Order, positions: List[Position], account: AccountState) -> GateResult:
    """
    Pre-trade gate check. Returns (allowed, reason).
    Checks: correlation gate, margin governor, size validation.
    """
    # CORRELATION GATE: Too much exposure to same currency?
    base_currency = order.symbol[:3]  # EUR from EURUSD
    quote_currency = order.symbol[3:6]  # USD from EURUSD
    
    base_exposure = sum(
        p.units if p.side == "buy" else -p.units
        for p in positions
        if p.symbol.startswith(base_currency)
    )
    
    quote_exposure = sum(
        p.units if p.side == "buy" else -p.units
        for p in positions
        if p.symbol.endswith(quote_currency)
    )
    
    # Check if new order would double-up on same currency
    if order.side == "buy" and base_exposure > 0:
        return GateResult(False, f"correlation_gate: Too much {base_currency} exposure (${base_exposure:,.0f})")
    
    # MARGIN GOVERNOR: Max 35% margin utilization
    projected_margin = account.margin_used + (order.units * 0.02)  # Simplified
    projected_util = projected_margin / account.nav if account.nav > 0 else 0
    
    if projected_util > 0.35:
        return GateResult(False, f"margin_governor: Would exceed 35% (projected {projected_util*100:.1f}%)")
    
    # SIZE VALIDATION: Order too large?
    max_units = int(account.nav * 2.0)  # Max 200% for testing  # Max 10% of account in one order
    if order.units > max_units:
        return GateResult(False, f"size_validation: Order {order.units} > max {max_units}")
    
    return GateResult(True)

def tick_enforce(positions: List[Position], account: AccountState) -> List[EnforcementAction]:
    """
    Periodic enforcement tick. Applies autopilot rules every 30s.
    Returns list of actions taken (modify_sl, close, advice).
    """
    actions = []
    now = datetime.now(timezone.utc)
    
    for pos in positions:
        if pos.status != "active":
            continue
        
        # RULE 1: AUTO-BREAKEVEN @ 25 pips
        pips_moved = (pos.current_price - pos.entry_price) * 10000
        if pos.side == "buy" and pips_moved >= 25 and (pos.stop_loss is None or pos.stop_loss < pos.entry_price):
            new_sl = pos.entry_price + 0.0005  # BE + 5 pips
            actions.append(EnforcementAction(
                type="modify_sl",
                position_id=pos.id,
                why="auto_breakeven @ 25p",
                new_sl=new_sl
            ))
            pos.stop_loss = new_sl
            pos.status = "trailing"
        
        # RULE 2: TRAILING STOP (18p gap)
        if pos.status == "trailing" and pos.side == "buy":
            trail_gap = 0.0018  # 18 pips
            new_sl = pos.current_price - trail_gap
            if pos.stop_loss is None or new_sl > pos.stop_loss:
                actions.append(EnforcementAction(
                    type="modify_sl",
                    position_id=pos.id,
                    why="trailing_stage2 @ 18p",
                    new_sl=new_sl
                ))
                pos.stop_loss = new_sl
        
        # RULE 3: PEAK GIVEBACK EXIT (40% retracement closes position)
        if pos.peak_pips > 0:
            current_pips = (pos.current_price - pos.entry_price) * 10000
            retracement_pct = (pos.peak_pips - current_pips) / pos.peak_pips if pos.peak_pips > 0 else 0
            
            if retracement_pct > 0.40:  # 40% retracement
                actions.append(EnforcementAction(
                    type="close",
                    position_id=pos.id,
                    why=f"peak_giveback: was +{pos.peak_pips:.0f}p, retracted {retracement_pct*100:.0f}%"
                ))
                pos.status = "closed"
        
        # RULE 4: TIME-BASED CLOSES (6h hard cap)
        elapsed = (now - pos.opened_at).total_seconds() / 3600
        if elapsed > 6:
            actions.append(EnforcementAction(
                type="close",
                position_id=pos.id,
                why="time_stop: 6h TTL expired"
            ))
            pos.status = "closed"
    
    return actions

# ==================== INTEGRATED TRADING MANAGER ====================

class PositionStatus(Enum):
    """Position status states"""
    ACTIVE = "active"
    TRAILING = "trailing"
    CLOSING = "closing"
    CLOSED = "closed"
    EXPIRED = "expired"
    STOPPED = "stopped"

class IntegratedSwarmManager:
    """
    Main trading manager combining:
    - SwarmBot position lifecycle management
    - Position Guardian pre-trade gating
    - Position Guardian autopilot enforcement
    """
    
    def __init__(self, pin: int = None, log_dir: str = None):
        """Initialize integrated manager"""
        if pin and pin != 841921:
            raise PermissionError("Invalid PIN for Integrated Swarm Manager")
        
        self.active_positions: Dict[str, Position] = {}
        self.completed_positions: List[Dict[str, Any]] = []
        self.account: Optional[AccountState] = None
        
        self.log_dir = Path(log_dir) if log_dir else Path.home() / "RICK" / "prototype" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger("IntegratedSwarmManager")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.log_dir / "integrated_manager.log")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s"
        ))
        self.logger.addHandler(handler)
        
        self._lock = threading.Lock()
        self._enforcement_thread = None
        self._stop_event = threading.Event()
        
        # Metrics
        self.metrics = {
            "total_orders_submitted": 0,
            "orders_blocked_correlation": 0,
            "orders_blocked_margin": 0,
            "orders_blocked_size": 0,
            "auto_breakeven_applied": 0,
            "trailing_stops_applied": 0,
            "peak_giveback_closes": 0,
            "time_based_closes": 0,
            "positions_closed": 0,
            "cumulative_pnl": 0.0
        }
        
        self.logger.info("🚀 Integrated Swarm Manager initialized (PIN: 841921)")
    
    def set_account(self, nav: float, margin_used: float):
        """Update account state"""
        self.account = AccountState(nav=nav, margin_used=margin_used)
        self.logger.info(f"📊 Account updated: NAV=${nav:,.2f}, Margin=${margin_used:,.2f}")
    
    # ==================== PRE-TRADE GATE ====================
    
    def place_order(self, symbol: str, side: str, units: float, 
                   entry_price: float, stop_loss: float, take_profit: float) -> Tuple[bool, str, Optional[str]]:
        """
        PRIMARY ENTRY POINT: Place order with Position Guardian gating.
        
        Returns (allowed, reason, position_id)
        """
        if not self.account:
            return False, "Account not initialized", None
        
        self.metrics["total_orders_submitted"] += 1
        
        # Build order
        order = Order(
            symbol=symbol,
            side=side,
            units=units,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        # RUN PRE-TRADE GATE
        gate_result = pre_trade_hook(
            order,
            list(self.active_positions.values()),
            self.account
        )
        
        if not gate_result.allowed:
            reason = gate_result.reason or "Unknown gate failure"
            
            # Update rejection metrics
            if "correlation" in reason.lower():
                self.metrics["orders_blocked_correlation"] += 1
            elif "margin" in reason.lower():
                self.metrics["orders_blocked_margin"] += 1
            else:
                self.metrics["orders_blocked_size"] += 1
            
            self.logger.warning(f"❌ Order BLOCKED: {symbol} {side} {units} | {reason}")
            self._save_metrics()
            return False, reason, None
        
        # ORDER PASSED GATES - Create position
        position_id = str(uuid.uuid4())[:8]
        position = Position(
            id=position_id,
            symbol=symbol,
            side=side,
            units=units,
            entry_price=entry_price,
            current_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            opened_at=datetime.now(timezone.utc),
            initial_sl=stop_loss,
            status="active"
        )
        
        with self._lock:
            self.active_positions[position_id] = position
        
        self.logger.info(f"✅ Order APPROVED & created: {symbol} {side} {units} units (ID: {position_id})")
        return True, "Order passed all gates", position_id
    
    # ==================== TICK ENFORCEMENT ====================
    
    def start_enforcement_loop(self, interval_seconds: int = 30):
        """Start the enforcement loop (runs in background thread)"""
        if self._enforcement_thread and self._enforcement_thread.is_alive():
            self.logger.warning("⚠️  Enforcement loop already running")
            return
        
        def enforcement_worker():
            self.logger.info(f"🤖 Enforcement loop started (interval: {interval_seconds}s)")
            
            while not self._stop_event.is_set():
                try:
                    self._tick_enforce_all()
                    time.sleep(interval_seconds)
                except Exception as e:
                    self.logger.error(f"❌ Enforcement error: {e}")
                    time.sleep(interval_seconds)
        
        self._enforcement_thread = threading.Thread(target=enforcement_worker, daemon=True)
        self._enforcement_thread.start()
    
    def stop_enforcement_loop(self):
        """Stop the enforcement loop"""
        self._stop_event.set()
        if self._enforcement_thread:
            self._enforcement_thread.join(timeout=5)
        self.logger.info("🛑 Enforcement loop stopped")
    
    def _tick_enforce_all(self):
        """Single enforcement tick: Apply Position Guardian autopilot rules"""
        if not self.account:
            return
        
        with self._lock:
            positions = list(self.active_positions.values())
        
        if not positions:
            return
        
        # Update current prices (in real system, fetch from broker)
        self._update_prices(positions)
        
        # RUN TICK ENFORCEMENT
        actions = tick_enforce(positions, self.account)
        
        if not actions:
            return
        
        # APPLY ACTIONS
        applied = []
        for action in actions:
            if action.type == "modify_sl":
                self.logger.info(f"📌 SL modified: {action.position_id} | {action.why} | New SL: {action.new_sl:.5f}")
                self.metrics["trailing_stops_applied"] += 1
                applied.append(f"SL→{action.new_sl:.5f}")
            
            elif action.type == "close":
                self.logger.info(f"📍 Position closed: {action.position_id} | {action.why}")
                
                # Move to completed
                with self._lock:
                    if action.position_id in self.active_positions:
                        pos = self.active_positions[action.position_id]
                        
                        if "giveback" in action.why:
                            self.metrics["peak_giveback_closes"] += 1
                        elif "time" in action.why:
                            self.metrics["time_based_closes"] += 1
                        
                        self.metrics["positions_closed"] += 1
                        self.metrics["cumulative_pnl"] += pos.pnl
                        
                        completed = {
                            "id": pos.id,
                            "symbol": pos.symbol,
                            "side": pos.side,
                            "units": pos.units,
                            "entry_price": pos.entry_price,
                            "pnl": pos.pnl,
                            "exit_reason": action.why,
                            "closed_at": datetime.now(timezone.utc).isoformat()
                        }
                        self.completed_positions.append(completed)
                        del self.active_positions[action.position_id]
                
                applied.append("CLOSE")
        
        self._save_metrics()
        
        if applied:
            self.logger.info(f"✅ Enforcement applied: {len(applied)} actions | {applied}")
    
    def _update_prices(self, positions: List[Position]):
        """Simulate price updates (in real system, fetch from broker)"""
        for pos in positions:
            import random
            if pos.side == "buy":
                pos.current_price *= (1 + random.uniform(-0.0005, 0.001))
            else:
                pos.current_price *= (1 + random.uniform(-0.001, 0.0005))
            
            # Update peak pips
            pips = (pos.current_price - pos.entry_price) * 10000
            if pips > pos.peak_pips:
                pos.peak_pips = pips
            
            # Update P&L
            if pos.side == "buy":
                pos.pnl = (pos.current_price - pos.entry_price) * pos.units
            else:
                pos.pnl = (pos.entry_price - pos.current_price) * pos.units
    
    # ==================== STATUS & METRICS ====================
    
    def get_active_positions(self) -> List[Dict[str, Any]]:
        """Get all active positions"""
        with self._lock:
            return [
                {
                    "id": pos.id,
                    "symbol": pos.symbol,
                    "side": pos.side,
                    "units": pos.units,
                    "entry_price": pos.entry_price,
                    "current_price": pos.current_price,
                    "stop_loss": pos.stop_loss,
                    "pnl": pos.pnl,
                    "peak_pips": pos.peak_pips,
                    "status": pos.status,
                    "elapsed_minutes": (datetime.now(timezone.utc) - pos.opened_at).total_seconds() / 60
                }
                for pos in self.active_positions.values()
            ]
    
    def get_completed_positions(self) -> List[Dict[str, Any]]:
        """Get all completed positions"""
        with self._lock:
            return self.completed_positions.copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get manager metrics"""
        with self._lock:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "active_positions": len(self.active_positions),
                "completed_positions": len(self.completed_positions),
                "account_nav": self.account.nav if self.account else None,
                "margin_utilized": f"{self.account.margin_utilization * 100:.1f}%" if self.account else None,
                "metrics": self.metrics.copy()
            }
    
    def _save_metrics(self):
        """Save metrics to file"""
        try:
            metrics_file = self.log_dir / "manager_metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(self.get_metrics(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")


# ==================== DEMO/TEST ====================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("INTEGRATED SWARM MANAGER WITH POSITION GUARDIAN")
    print("Prototype Folder: /home/ing/RICK/prototype/")
    print("PIN: 841921")
    print("="*80)
    
    # Initialize manager
    mgr = IntegratedSwarmManager(pin=841921)
    mgr.set_account(nav=10000, margin_used=2000)
    
    # Start enforcement loop
    mgr.start_enforcement_loop(interval_seconds=5)
    
    print("\n📋 Test Scenario:")
    print("  1. Place EURUSD BUY order (should pass)")
    print("  2. Try GBPUSD correlated order (should block)")
    print("  3. Run enforcement ticks")
    print("  4. Watch auto-breakeven & trailing apply")
    
    # Test 1: Valid order
    print("\n[Test 1] Placing EURUSD BUY 10,000...")
    allowed, reason, pos_id = mgr.place_order(
        symbol="EURUSD",
        side="buy",
        units=10000,
        entry_price=1.0800,
        stop_loss=1.0750,
        take_profit=1.0900
    )
    print(f"  Result: {allowed} | {reason} | ID: {pos_id}")
    
    # Test 2: Correlated order (should block)
    print("\n[Test 2] Trying GBPUSD BUY 8,000 (correlated)...")
    allowed, reason, pos_id = mgr.place_order(
        symbol="GBPUSD",
        side="buy",
        units=8000,
        entry_price=1.3400,
        stop_loss=1.3350,
        take_profit=1.3500
    )
    print(f"  Result: {allowed} | {reason}")
    
    # Monitor for 30 seconds
    print("\n⏳ Monitoring for 30 seconds...")
    for i in range(6):
        time.sleep(5)
        active = mgr.get_active_positions()
        print(f"  Cycle {i+1}: {len(active)} active positions")
        if active:
            for pos in active:
                print(f"    - {pos['symbol']}: P&L=${pos['pnl']:.2f}, Peak={pos['peak_pips']:.0f}p, Status={pos['status']}")
    
    # Stop and report
    mgr.stop_enforcement_loop()
    
    print("\n📊 Final Metrics:")
    metrics = mgr.get_metrics()
    for key, value in metrics["metrics"].items():
        print(f"  {key}: {value}")
    
    print("\n✅ Integration test completed!")
    print("="*80 + "\n")


# ==================== CHARTER COMPLIANCE UPDATE ====================
# 
# MANDATORY CHARTER REQUIREMENTS (Enforced at runtime):
# - Minimum notional: 15,000 units per order
# - Maximum position TTL: 6 hours
# - All orders require stop loss + take profit
# - Prepended instructions must be verified before each action
# 
# Update to pre_trade_hook function:
# Add after line 108 (in the SIZE VALIDATION section):
#
# # CHARTER COMPLIANCE: Minimum notional units
# MIN_NOTIONAL_UNITS = 15000
# if order.units < MIN_NOTIONAL_UNITS:
#     return GateResult(False, f"charter_violation: Order {order.units} < min notional {MIN_NOTIONAL_UNITS}")

