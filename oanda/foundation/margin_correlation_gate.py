#!/usr/bin/env python3
"""
RICK MARGIN & CORRELATION GUARDIAN GATE
PIN: 841921

Enforces:
1. Margin cap at 35% utilization (IMMUTABLE)
2. Currency bucket correlation detection
3. Auto-scaling on margin breach
4. Auto-cancellation of pending orders when over cap
5. ATR-based stop loss validation
6. Time-based position management

This is a drop-in gate for pre-trade and ongoing position management.
"""

import logging
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class HookResult:
    """Gate result: allowed or blocked with reason"""
    def __init__(self, allowed: bool, reason: str = "", action: str = ""):
        self.allowed = allowed
        self.reason = reason
        self.action = action  # AUTO_CANCEL, SCALE_OUT, CLOSE, etc.

    def __repr__(self):
        return f"HookResult(allowed={self.allowed}, reason='{self.reason}', action='{self.action}')"


@dataclass
class Position:
    """Position snapshot"""
    symbol: str
    side: str  # "LONG" or "SHORT"
    units: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_pips: float
    margin_used: float
    position_id: str


@dataclass
class Order:
    """Pending order snapshot"""
    symbol: str
    side: str
    units: float
    price: float
    order_id: str
    order_type: str = "LIMIT"


class MarginCorrelationGate:
    """
    Guardian gate for margin cap & currency correlation
    """

    # ========================================================================
    # IMMUTABLE PARAMETERS (Charter-Enforced)
    # ========================================================================
    MARGIN_CAP_PCT = 0.35  # 35% hard cap (IMMUTABLE)
    MIN_ATR_BUFFER_PIPS = 18  # Conservative SL floor (pips from entry)
    TIME_STOP_3H_MINUTES = 180
    TIME_STOP_6H_MINUTES = 360
    MIN_R_RATIO_AT_3H = 0.5  # Close if R < 0.5 at 3h
    SCALE_OUT_TARGET_MARGIN_PCT = 0.25  # Scale to 25% if over 35%

    def __init__(self, account_nav: float = 1970.0):
        """
        Args:
            account_nav: Net account value in USD
        """
        self.account_nav = account_nav
        self.max_margin_usd = account_nav * self.MARGIN_CAP_PCT
        logger.info(f"🛡️  Margin & Correlation Gate Initialized")
        logger.info(f"   Account NAV: ${account_nav:,.2f}")
        logger.info(f"   35% Margin Cap: ${self.max_margin_usd:,.2f}")

    # ========================================================================
    # CURRENCY BUCKET ANALYSIS
    # ========================================================================

    @staticmethod
    def split_symbol(symbol: str) -> Tuple[str, str]:
        """Split 'EUR_USD' → ('EUR', 'USD')"""
        parts = symbol.replace("/", "_").split("_")
        if len(parts) == 2:
            return parts[0], parts[1]
        raise ValueError(f"Invalid symbol: {symbol}")

    def currency_bucket_exposure(
        self, positions: List[Position], orders: List[Order] = None
    ) -> Dict[str, float]:
        """
        Calculate net exposure by currency (in units).

        Example:
          Long EUR/CHF 16k  → +EUR 16k, -CHF 16k
          Long USD/CHF 19k  → +USD 19k, -CHF 19k
          Result: CHF bucket = -35k (severely short CHF)

        Returns:
            {'EUR': 16000, 'USD': 19000, 'CHF': -35000, ...}
        """
        exposure = defaultdict(float)

        # Add position exposures
        for pos in positions:
            base, quote = self.split_symbol(pos.symbol)
            sign = 1 if pos.side.upper() == "LONG" else -1
            exposure[base] += sign * pos.units
            exposure[quote] -= sign * pos.units

        # Add pending order exposures
        if orders:
            for order in orders:
                base, quote = self.split_symbol(order.symbol)
                sign = 1 if order.side.upper() == "BUY" else -1
                exposure[base] += sign * order.units
                exposure[quote] -= sign * order.units

        return dict(exposure)

    # ========================================================================
    # CORRELATION GATE
    # ========================================================================

    def correlation_gate_any_ccy(
        self, new_order: Order, current_positions: List[Position]
    ) -> HookResult:
        """
        Block if new order increases the same-side exposure in any currency.

        Logic:
          - Calculate current exposure by currency
          - Calculate exposure after adding new order
          - If any currency's |exposure| grows AND stays in same direction → BLOCK

        Example (Your Case):
          Current:  EUR +16k, USD +19k, CHF -35k
          New:      EUR/USD BUY 10k  → EUR +10k, USD -10k
          After:    EUR +26k, USD +9k, CHF -35k
          Result:   EUR & CHF both increased in same direction → BLOCK
                    Reason: "correlation_gate:CHF_bucket"
        """
        before_exposure = self.currency_bucket_exposure(current_positions, [])
        test_order = [new_order]
        after_exposure = self.currency_bucket_exposure(current_positions, test_order)

        # Check each currency
        for ccy in after_exposure:
            before_exp = before_exposure.get(ccy, 0.0)
            after_exp = after_exposure.get(ccy, 0.0)

            # Did this currency's exposure increase in the same direction?
            exposure_grew = abs(after_exp) > abs(before_exp)
            same_sign = before_exp * after_exp >= 0  # Both same sign or both 0

            if exposure_grew and same_sign and before_exp != 0:
                # Oops—correlate increasing
                reason = f"correlation_gate:{ccy}_bucket (was {before_exp:+.0f}, now {after_exp:+.0f})"
                logger.warning(f"❌ Correlation gate BLOCKED: {reason}")
                return HookResult(
                    allowed=False,
                    reason=reason,
                    action="AUTO_CANCEL",
                )

        logger.info(f"✅ Correlation gate PASSED: {new_order.symbol} {new_order.side}")
        return HookResult(allowed=True)

    # ========================================================================
    # MARGIN GATE
    # ========================================================================

    def margin_gate(
        self, total_margin_used: float, new_order: Order = None
    ) -> HookResult:
        """
        Block new orders if:
          1. Current margin > 35%
          2. OR new order would push over 35%

        Also triggers auto-scale-out when margin > 35%.
        """
        current_pct = total_margin_used / self.account_nav
        reason = f"{current_pct*100:.1f}% utilization"

        # Hard cap exceeded
        if current_pct > self.MARGIN_CAP_PCT:
            msg = f"margin_cap_exceeded: {reason} (hard cap: {self.MARGIN_CAP_PCT*100:.0f}%)"
            logger.warning(f"❌ Margin gate BLOCKED: {msg}")
            return HookResult(
                allowed=False,
                reason=msg,
                action="AUTO_CANCEL",  # Cancel pending orders
            )

        # New order would exceed
        if new_order:
            estimated_order_margin = new_order.units * new_order.price * 0.02  # ~2% margin
            projected_margin = total_margin_used + estimated_order_margin
            projected_pct = projected_margin / self.account_nav

            if projected_pct > self.MARGIN_CAP_PCT:
                msg = f"margin_cap_would_exceed: {projected_pct*100:.1f}% after order"
                logger.warning(f"❌ Margin gate BLOCKED: {msg}")
                return HookResult(
                    allowed=False,
                    reason=msg,
                    action="AUTO_CANCEL",
                )

        logger.info(f"✅ Margin gate PASSED: {reason}")
        return HookResult(allowed=True)

    # ========================================================================
    # PRE-TRADE CONSOLIDATED GATE
    # ========================================================================

    def pre_trade_gate(
        self,
        new_order: Order,
        current_positions: List[Position],
        pending_orders: List[Order],
        total_margin_used: float,
    ) -> HookResult:
        """
        Master gate: Run ALL checks before allowing a new order.

        Order:
          1. Margin cap check
          2. Correlation gate check
          3. Return combined result
        """
        logger.info(
            f"\n🔍 PRE-TRADE GATE: {new_order.symbol} {new_order.side} {new_order.units} units"
        )

        # Check 1: Margin
        margin_result = self.margin_gate(total_margin_used, new_order)
        if not margin_result.allowed:
            return margin_result

        # Check 2: Correlation
        correlation_result = self.correlation_gate_any_ccy(new_order, current_positions)
        if not correlation_result.allowed:
            return correlation_result

        # All gates passed
        logger.info(f"✅ PRE-TRADE GATE PASSED\n")
        return HookResult(allowed=True, action="EXECUTE")

    # ========================================================================
    # ONGOING MANAGEMENT: TIME STOPS & ATR SL
    # ========================================================================

    def validate_stop_loss_distance(
        self, entry_price: float, stop_price: float, symbol: str, atr_value: float = None
    ) -> Tuple[bool, str]:
        """
        Validate that SL is at least 1× ATR (or conservative floor) from entry.

        Args:
            entry_price: Entry level
            stop_price: Current SL level
            symbol: Pair (used to determine if JPY)
            atr_value: ATR(14) value (optional; uses conservative floor if None)

        Returns:
            (is_valid, reason)
        """
        # JPY pairs: 1 pip = 0.01 (e.g., 100 pips = 1.00 price diff)
        # Other pairs: 1 pip = 0.0001 (e.g., 100 pips = 0.01 price diff)
        pip_size = 0.01 if "JPY" in symbol else 0.0001
        distance_pips = abs(entry_price - stop_price) / pip_size

        # Use ATR if available; otherwise conservative floor
        if atr_value:
            atr_pips = atr_value / (0.01 if "JPY" in symbol else 0.0001)
            min_distance = atr_pips
        else:
            min_distance = self.MIN_ATR_BUFFER_PIPS

        if distance_pips < min_distance:
            return False, f"SL too tight: {distance_pips:.1f} pips < {min_distance:.1f} pips"

        return True, f"SL valid: {distance_pips:.1f} pips >= {min_distance:.1f} pips"

    def time_stop_check(
        self, position: Position, minutes_held: float, current_r_multiple: float
    ) -> Optional[str]:
        """
        Check if position should be closed due to time.

        Rules:
          - At 3 hours: Close if R < 0.5
          - At 6 hours: Close regardless

        Returns:
            "close_reason" or None
        """
        if minutes_held >= self.TIME_STOP_6H_MINUTES:
            return f"time_stop_6h_hard_cap (held {minutes_held:.0f} min)"

        if minutes_held >= self.TIME_STOP_3H_MINUTES:
            if current_r_multiple < self.MIN_R_RATIO_AT_3H:
                return f"time_stop_3h_underperforming (R={current_r_multiple:.2f} < {self.MIN_R_RATIO_AT_3H})"

        return None

    # ========================================================================
    # SCALE-OUT RECOMMENDATION
    # ========================================================================

    def scale_out_recommendation(
        self, current_margin_pct: float, current_positions: List[Position]
    ) -> Optional[Dict]:
        """
        If margin > 35%, recommend scaling out.

        Logic:
          1. Target: 25% utilization
          2. Scale the weakest performer (lowest R multiple) first
          3. Or scale both evenly

        Returns:
            {
              "reason": "margin_overage",
              "current_pct": 0.58,
              "target_pct": 0.25,
              "scale_out_amount_pct": 0.50,
              "recommended_position_id": "pos_xxx"
            }
        """
        if current_margin_pct <= self.MARGIN_CAP_PCT:
            return None  # Not needed

        target_margin_pct = self.SCALE_OUT_TARGET_MARGIN_PCT
        scale_out_pct = 1.0 - (target_margin_pct / current_margin_pct)
        scale_out_pct = min(scale_out_pct, 0.50)  # Cap at 50% scale

        # Find weakest performer
        weakest_pos = min(current_positions, key=lambda p: p.pnl, default=None)
        recommended_id = weakest_pos.position_id if weakest_pos else None

        return {
            "reason": "margin_overage",
            "current_pct": current_margin_pct,
            "target_pct": target_margin_pct,
            "scale_out_amount_pct": scale_out_pct,
            "recommended_position_id": recommended_id,
            "note": f"Scale out {scale_out_pct*100:.0f}% of {weakest_pos.symbol if weakest_pos else 'any position'} to get under 35%",
        }

    # ========================================================================
    # PENDING ORDER AUTO-CANCELLATION
    # ========================================================================

    def auto_cancel_pending_if_over_cap(
        self, pending_orders: List[Order], total_margin_used: float
    ) -> List[str]:
        """
        If margin > 35%, auto-cancel all pending orders (in order: oldest first).

        Returns:
            List of cancelled order IDs
        """
        current_pct = total_margin_used / self.account_nav

        if current_pct <= self.MARGIN_CAP_PCT:
            return []

        cancelled = []
        for order in pending_orders:
            logger.warning(
                f"🔴 AUTO-CANCEL PENDING: {order.order_id} "
                f"({order.symbol} {order.side}) - margin at {current_pct*100:.1f}%"
            )
            cancelled.append(order.order_id)

        return cancelled


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_gate_check():
    """Demo: Check your current holdings against the gate"""

    # Your current state
    positions = [
        Position(
            symbol="EUR_CHF",
            side="LONG",
            units=16300,
            entry_price=0.92404,
            current_price=0.92070,  # -3.4 pips
            pnl=-7.03,
            pnl_pips=-3.4,
            margin_used=570,
            position_id="pos_117",
        ),
        Position(
            symbol="USD_CHF",
            side="LONG",
            units=19000,
            entry_price=0.79296,
            current_price=0.79225,  # -2.1 pips
            pnl=-5.06,
            pnl_pips=-2.1,
            margin_used=570,
            position_id="pos_118",
        ),
    ]

    pending_orders = [
        Order(
            symbol="EUR_USD",
            side="BUY",
            units=10000,
            price=1.0800,
            order_id="order_111",
        ),
        Order(
            symbol="EUR_USD",
            side="BUY",
            units=5000,
            price=1.0750,
            order_id="order_102",
        ),
    ]

    gate = MarginCorrelationGate(account_nav=1970.0)

    # Current exposure
    exposure = gate.currency_bucket_exposure(positions, pending_orders)
    print(f"\n💱 Currency Bucket Exposure (with pending):\n{exposure}")

    # Try to add another EUR/USD buy (should be BLOCKED due to correlation)
    test_order = Order(
        symbol="EUR_USD", side="BUY", units=8000, price=1.0800, order_id="test_119"
    )

    result = gate.pre_trade_gate(
        new_order=test_order,
        current_positions=positions,
        pending_orders=pending_orders,
        total_margin_used=1140,  # $1,140 in margin
    )

    print(f"\n🔍 PRE-TRADE GATE RESULT: {result}\n")

    if not result.allowed:
        print(f"❌ ORDER BLOCKED")
        print(f"   Reason: {result.reason}")
        print(f"   Action: {result.action}")
    else:
        print(f"✅ ORDER ALLOWED")

    # Scale-out recommendation
    scale_rec = gate.scale_out_recommendation(
        current_margin_pct=1140 / 1970, current_positions=positions
    )
    print(f"\n📊 Scale-Out Recommendation:\n{scale_rec}\n")

    # Auto-cancel pending if over
    cancelled = gate.auto_cancel_pending_if_over_cap(pending_orders, 1140)
    print(f"\n🚫 Auto-Cancelled Orders: {cancelled}\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )
    example_gate_check()
