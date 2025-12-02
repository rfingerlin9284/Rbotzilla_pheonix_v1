#!/usr/bin/env python3
"""
RICK Charter Enforcement Module - RBOTzilla UNI Phase 2
Immutable trading constants and enforcement logic.
PIN: 841921 | Generated: 2025-09-26

EXTRACTED FROM: WSL Ubuntu /home/ing/RICK/RICK_LIVE_CLEAN
READ ONLY ACCESS - No modifications to source
"""

import logging
from typing import Dict, List, Optional, Union
from datetime import timedelta
from enum import Enum

class TimeFrame(Enum):
    """Allowed trading timeframes"""
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"

class RejectedTimeFrame(Enum):
    """Explicitly rejected timeframes"""
    M1 = "M1"
    M5 = "M5"

class RickCharter:
    """
    RICK Charter Core Enforcement - Immutable Constants
    All values are hardcoded for safety and cannot be overridden.
    """

    # CORE AUTHENTICATION
    PIN = 841921
    CHARTER_VERSION = "2.0_IMMUTABLE"

    # TRADING CONSTRAINTS
    MAX_HOLD_DURATION_HOURS = 6
    MAX_HOLD_DURATION = timedelta(hours=MAX_HOLD_DURATION_HOURS)

    # RISK MANAGEMENT
    DAILY_LOSS_BREAKER_PCT = -5.0  # -5% daily loss halt
    MIN_NOTIONAL_USD = 15000
    MIN_EXPECTED_PNL_USD = 100.0  # Gross PnL at TP must be >= $100

    # Minimum risk-reward ratio (guide compliance: 3.2)
    MIN_RISK_REWARD_RATIO = 3.2

    # TIMEFRAME ENFORCEMENT
    ALLOWED_TIMEFRAMES = [TimeFrame.M15, TimeFrame.M30, TimeFrame.H1]
    REJECTED_TIMEFRAMES = [RejectedTimeFrame.M1, RejectedTimeFrame.M5]

    # EXECUTION LIMITS
    MAX_CONCURRENT_POSITIONS = 3
    MAX_DAILY_TRADES = 12
    MAX_PLACEMENT_LATENCY_MS = 300  # Maximum 300ms for order placement

    # SPREAD & SLIPPAGE GATES
    FX_MAX_SPREAD_ATR_MULTIPLIER = 0.15    # 0.15x ATR14
    CRYPTO_MAX_SPREAD_ATR_MULTIPLIER = 0.10 # 0.10x ATR14

    # STOP LOSS REQUIREMENTS
    FX_STOP_LOSS_ATR_MULTIPLIER = 1.2      # 1.2x ATR
    CRYPTO_STOP_LOSS_ATR_MULTIPLIER = 1.5  # 1.5x ATR

    @classmethod
    def validate_pin(cls, pin: int) -> bool:
        """Validate PIN for charter access"""
        return pin == cls.PIN

    @classmethod
    def validate_timeframe(cls, timeframe: str) -> bool:
        """Validate if timeframe is allowed"""
        # Check if it's in allowed timeframes
        allowed_values = [tf.value for tf in cls.ALLOWED_TIMEFRAMES]
        if timeframe in allowed_values:
            return True

        # Explicitly reject forbidden timeframes
        rejected_values = [tf.value for tf in cls.REJECTED_TIMEFRAMES]
        if timeframe in rejected_values:
            return False

        # Unknown timeframe - reject by default
        return False

    @classmethod
    def validate_hold_duration(cls, hours: float) -> bool:
        """Validate position hold duration"""
        return 0 < hours <= cls.MAX_HOLD_DURATION_HOURS

    @classmethod
    def validate_risk_reward(cls, risk_reward_ratio: float) -> bool:
        """Validate risk-reward ratio meets minimum"""
        return risk_reward_ratio >= cls.MIN_RISK_REWARD_RATIO

    @classmethod
    def validate_notional(cls, notional_usd: float) -> bool:
        """Validate minimum notional size"""
        return notional_usd >= cls.MIN_NOTIONAL_USD

    @classmethod
    def validate_daily_pnl(cls, daily_pnl_pct: float) -> bool:
        """Validate daily PnL hasn't hit breaker"""
        return daily_pnl_pct > cls.DAILY_LOSS_BREAKER_PCT

    @classmethod
    def validate(cls, test_key: Optional[str] = None) -> bool:
        """
        Charter validation test
        Returns True if all charter constants are properly set
        """
        try:
            # Test all core constants exist and are correct type
            assert cls.PIN == 841921, "PIN mismatch"
            assert isinstance(cls.MAX_HOLD_DURATION_HOURS, int), "Hold duration type error"
            assert cls.MAX_HOLD_DURATION_HOURS == 6, "Hold duration value error"
            assert cls.DAILY_LOSS_BREAKER_PCT == -5.0, "Loss breaker error"
            assert cls.MIN_NOTIONAL_USD == 15000, "Notional minimum error"
            assert cls.MIN_RISK_REWARD_RATIO == 3.2, "Risk reward error"
            assert cls.MIN_EXPECTED_PNL_USD == 100.0, "Expected PnL minimum error"

            # Test timeframe enforcement
            assert cls.validate_timeframe("M15") == True, "M15 should be allowed"
            assert cls.validate_timeframe("M30") == True, "M30 should be allowed"
            assert cls.validate_timeframe("H1") == True, "H1 should be allowed"
            assert cls.validate_timeframe("M1") == False, "M1 should be rejected"
            assert cls.validate_timeframe("M5") == False, "M5 should be rejected"

            # Test validation functions
            assert cls.validate_hold_duration(6) == True, "6h should be valid"
            assert cls.validate_hold_duration(7) == False, "7h should be invalid"
            assert cls.validate_risk_reward(3.2) == True, "3.2 RR should be valid"
            assert cls.validate_risk_reward(3.1) == False, "3.1 RR should be invalid"
            assert cls.validate_notional(15000) == True, "15k should be valid"
            assert cls.validate_notional(14999) == False, "14999 should be invalid"
            assert cls.validate_daily_pnl(-4.9) == True, "-4.9% should be valid"
            assert cls.validate_daily_pnl(-5.1) == False, "-5.1% should hit breaker"

            logging.info("RICK Charter validation PASSED ✅")
            return True

        except AssertionError as e:
            logging.error(f"RICK Charter validation FAILED: {e}")
            return False
        except Exception as e:
            logging.error(f"RICK Charter validation ERROR: {e}")
            return False

    @classmethod
    def get_charter_summary(cls) -> Dict[str, Union[int, float, str, List[str]]]:
        """Return complete charter summary for logging"""
        return {
            "pin": cls.PIN,
            "version": cls.CHARTER_VERSION,
            "max_hold_hours": cls.MAX_HOLD_DURATION_HOURS,
            "daily_loss_breaker": cls.DAILY_LOSS_BREAKER_PCT,
            "min_notional_usd": cls.MIN_NOTIONAL_USD,
            "min_risk_reward": cls.MIN_RISK_REWARD_RATIO,
            "min_expected_pnl_usd": cls.MIN_EXPECTED_PNL_USD,
            "allowed_timeframes": [tf.value for tf in cls.ALLOWED_TIMEFRAMES],
            "rejected_timeframes": [tf.value for tf in cls.REJECTED_TIMEFRAMES],
            "max_concurrent": cls.MAX_CONCURRENT_POSITIONS,
            "max_daily_trades": cls.MAX_DAILY_TRADES
        }

# Charter enforcement on module import
if __name__ == "__main__":
    # Self-test on direct execution
    result = RickCharter.validate("test")
    print(f"Charter Validation: {'PASS' if result else 'FAIL'}")
    if result:
        summary = RickCharter.get_charter_summary()
        print("Charter Summary:", summary)
else:
    # Validate on import
    _validation_result = RickCharter.validate()
    if not _validation_result:
        raise ImportError("RICK Charter validation failed - module import blocked")