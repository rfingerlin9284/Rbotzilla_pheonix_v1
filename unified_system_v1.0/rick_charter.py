#!/usr/bin/env python3
"""
RICK Charter Enforcement Module - RBOTzilla UNI Phase 2
Immutable trading constants and enforcement logic.
PIN: 841921 | Generated: 2025-09-26
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
    
    # =========================================================================
    # ADDENDUM: UI/DISPLAY SEPARATION (IMMUTABLE) - Approved PIN: 841921
    # Added: 2025-10-15
    # =========================================================================
    """
    CRITICAL IMMUTABLE RULE: UI/Dashboard Display Separation
    
    The timing, execution, and logic of ALL trading decisions are determined
    EXCLUSIVELY by ML intelligence and smart logic nodes. 
    
    Dashboard, UI, and display components are for VISUALIZATION AND USER 
    PREFERENCE ONLY and shall have ZERO effect on trading timing logic.
    
    This ensures:
    1. Trading logic remains pure and unaffected by display layer
    2. UI refresh rates can be adjusted without impacting execution
    3. User preferences do not introduce latency or timing issues
    4. ML/AI decision-making operates independently of visualization
    5. Charter compliance is enforced at logic layer, not UI layer
    
    ENFORCEMENT:
    - No trading logic shall read from or depend on UI state
    - Display refresh rates are independent of trade execution timing
    - UI components operate in separate threads/processes from trading engine
    - User UI preferences stored separately from trading parameters
    - Dashboard controls are READ-ONLY views of trading state
    
    VIOLATION: Any code that ties trading timing to UI refresh rates or
    user display preferences is a CHARTER VIOLATION and must be rejected.
    """
    UI_DISPLAY_SEPARATION_ENFORCED = True
    UI_CONTROLS_TRADING_LOGIC = False  # IMMUTABLE: Must always be False
    
    # =========================================================================
    # ADDENDUM: MANDATORY CODE REUSE SWEEP (IMMUTABLE) - Approved PIN: 841921
    # Added: 2025-10-15
    # =========================================================================
    """
    CRITICAL IMMUTABLE RULE: Pre-Implementation Code Discovery
    
    Before creating ANY new code, logic, or implementation, a MANDATORY sweep
    of ALL existing project folders MUST be performed to discover and reuse
    existing implementations.
    
    REQUIRED PROJECT FOLDERS TO SEARCH (in order of priority):
    1. /home/ing/RICK/RICK_LIVE_CLEAN (current working directory)
    2. /home/ing/RICK/RBOTZILLA_FINAL_v001
    3. /home/ing/RICK/R_H_UNI
    4. /home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE
    5. /home/ing/RICK/RICK_LIVE_PROTOTYPE
    6. /home/ing/RICK/Dev_unibot_v001
    7. /home/ing/RICK/Protoype [sic]
    8. /home/ing/RICK/Attached HTML and CSS Context
    
    ENFORCEMENT PROCEDURE:
    1. When ANY feature, function, or logic is requested, FIRST grep search
       all project folders for existing implementations
    2. If existing logic is found, EXTRACT and INTEGRATE it rather than
       creating new code from scratch
    3. Document the source folder and file where logic was found
    4. Preserve original author attribution and comments
    5. Only create NEW code if NO existing implementation exists
    
    SEARCH PATTERNS REQUIRED (minimum):
    - Exact function/class names mentioned in user request
    - Related feature keywords (e.g., "momentum", "trailing", "tp_cancel")
    - Similar logic patterns (e.g., regex for common implementations)
    
    VIOLATION: Creating new code without performing mandatory code reuse
    sweep is a CHARTER VIOLATION and results in:
    - Wasted development time duplicating existing work
    - Inconsistent implementations across codebase
    - Loss of battle-tested, validated logic
    - Technical debt from redundant implementations
    
    This rule ensures MAXIMUM code reuse, consistency, and preservation of
    existing validated implementations across all RICK project folders.
    """
    MANDATORY_CODE_REUSE_SWEEP_ENFORCED = True
    BYPASS_CODE_REUSE_SWEEP = False  # IMMUTABLE: Must always be False
    
    PROJECT_FOLDERS_TO_SEARCH = [
        "/home/ing/RICK/RICK_LIVE_CLEAN",
        "/home/ing/RICK/RBOTZILLA_FINAL_v001",
        "/home/ing/RICK/R_H_UNI",
        "/home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE",
        "/home/ing/RICK/RICK_LIVE_PROTOTYPE",
        "/home/ing/RICK/Dev_unibot_v001",
        "/home/ing/RICK/Protoype",
        "/home/ing/RICK/Attached HTML and CSS Context"
    ]
    
    # ========================================================================
    # SECTION 8: ENVIRONMENT-AGNOSTIC ARCHITECTURE (PIN 841921)
    # Approved: 2025-10-15
    # IMMUTABLE: Single unified codebase for practice/live environments
    # ========================================================================
    
    # ENVIRONMENT DIFFERENTIATION (IMMUTABLE)
    # The ONLY difference between practice and live trading shall be:
    # 1. API endpoint URL (practice vs live)
    # 2. API authentication token
    # NO other code paths, logic, or risk rules may differ between environments
    ENVIRONMENT_AGNOSTIC_ENFORCED = True  # IMMUTABLE: Must always be True
    ALLOW_ENVIRONMENT_SPECIFIC_LOGIC = False  # IMMUTABLE: Must always be False
    
    # PRACTICE/LIVE PARITY REQUIREMENTS (IMMUTABLE)
    IDENTICAL_CHARTER_ENFORCEMENT = True  # Same rules in practice and live
    IDENTICAL_RISK_PARAMETERS = True  # Same position sizing, stops, targets
    IDENTICAL_MOMENTUM_DETECTION = True  # Same TP cancellation logic
    IDENTICAL_TRAILING_STOPS = True  # Same adaptive trailing system
    IDENTICAL_NARRATION_LOGGING = True  # Same audit trail format
    
    # CONFIGURATION LOCATION (IMMUTABLE)
    # Environment selection MUST occur ONLY in:
    # - OandaConnector.__init__(environment='practice' or 'live')
    # - Command-line argument: --env practice|live
    # NO environment checks allowed in trading logic, risk management, or strategies
    ENVIRONMENT_CONFIG_CENTRALIZED = True  # IMMUTABLE
    
    # ========================================================================
    # SECTION 9: TP CANCELLATION & MOMENTUM TRAILING (PIN 841921)
    # Approved: 2025-10-15
    # IMMUTABLE: Battle-tested logic from rbotzilla_golden_age.py
    # ========================================================================
    
    # TP CANCELLATION TRIGGERS (IMMUTABLE)
    # Take Profit orders SHALL be cancelled and converted to trailing stops when:
    # 1. Hive Mind consensus >= 80% confidence AND signal matches position direction
    #    OR
    # 2. MomentumDetector confirms strong momentum:
    #    - Profit > 1.8-2.0x ATR (lower threshold in bull markets)
    #    - Trend strength > 0.65-0.70 (lower threshold in bull markets)
    #    - Strong market cycle OR high volatility (> 1.2x normal)
    TP_CANCELLATION_ENABLED = True  # IMMUTABLE: Must always be True
    DISABLE_TP_CANCELLATION = False  # IMMUTABLE: Must always be False
    
    # DUAL-SIGNAL TRIGGERING (IMMUTABLE)
    # TP cancellation fires when EITHER Hive OR Momentum confirms
    # Provides redundancy and maximum signal confirmation
    HIVE_TRIGGER_CONFIDENCE_MIN = 0.80  # IMMUTABLE: 80% consensus minimum
    MOMENTUM_PROFIT_THRESHOLD_ATR = 1.8  # IMMUTABLE: 1.8x ATR in bull markets
    MOMENTUM_TREND_THRESHOLD = 0.65  # IMMUTABLE: 0.65 in bull markets
    MOMENTUM_VOLATILITY_THRESHOLD = 1.2  # IMMUTABLE: 1.2x normal volatility
    
    # STOP LOSS PROTECTION (IMMUTABLE)
    # Stop Loss orders SHALL NEVER be removed or disabled
    # Only Take Profit orders may be cancelled (converted to trailing stops)
    STOP_LOSS_ALWAYS_REQUIRED = True  # IMMUTABLE: SL always present
    ALLOW_STOP_LOSS_REMOVAL = False  # IMMUTABLE: Must always be False
    
    # ADAPTIVE TRAILING STOPS (IMMUTABLE)
    # Progressive tightening system from rbotzilla_golden_age.py
    # 6 levels of trailing distance based on profit ATR multiples:
    TRAILING_LEVEL_1_PROFIT = 1.0  # 0-1x ATR profit
    TRAILING_LEVEL_1_DISTANCE = 1.2  # 1.2x ATR trail
    TRAILING_LEVEL_2_PROFIT = 2.0  # 1-2x ATR profit
    TRAILING_LEVEL_2_DISTANCE = 1.0  # 1.0x ATR trail
    TRAILING_LEVEL_3_PROFIT = 3.0  # 2-3x ATR profit
    TRAILING_LEVEL_3_DISTANCE = 0.8  # 0.8x ATR trail
    TRAILING_LEVEL_4_PROFIT = 4.0  # 3-4x ATR profit
    TRAILING_LEVEL_4_DISTANCE = 0.6  # 0.6x ATR trail
    TRAILING_LEVEL_5_PROFIT = 5.0  # 4-5x ATR profit
    TRAILING_LEVEL_5_DISTANCE = 0.5  # 0.5x ATR trail
    TRAILING_LEVEL_6_DISTANCE = 0.4  # 5+x ATR profit: 0.4x ATR trail (ultra-tight)
    
    # MOMENTUM LOOSENING FACTOR (IMMUTABLE)
    # When momentum detected, trailing stops loosen by 15% to let winners run
    MOMENTUM_TRAIL_LOOSENING_FACTOR = 1.15  # IMMUTABLE: 15% loosening
    
    # CODE ORIGIN ATTRIBUTION (IMMUTABLE)
    # All momentum detection and trailing logic extracted from:
    MOMENTUM_SOURCE_FILE = "/home/ing/RICK/RICK_LIVE_CLEAN/rbotzilla_golden_age.py"
    MOMENTUM_SOURCE_LINES = "140-230"  # MomentumDetector + SmartTrailingSystem
    MOMENTUM_EXTRACTION_DATE = "2025-10-15"
    MOMENTUM_EXTRACTION_PIN = 841921  # Charter-approved extraction
    
    # POSITION AGE REQUIREMENT (IMMUTABLE)
    # Positions must be >= 60 seconds old before TP cancellation considered
    # Prevents premature conversions on entry volatility
    MIN_POSITION_AGE_FOR_TP_CANCEL_SECONDS = 60  # IMMUTABLE
    
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
    def validate(cls, test_key: str = None) -> bool:
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
            
            # Test environment-agnostic enforcement
            assert cls.ENVIRONMENT_AGNOSTIC_ENFORCED == True, "Environment-agnostic must be enforced"
            assert cls.ALLOW_ENVIRONMENT_SPECIFIC_LOGIC == False, "Environment-specific logic forbidden"
            assert cls.IDENTICAL_CHARTER_ENFORCEMENT == True, "Charter must be identical across environments"
            
            # Test TP cancellation rules
            assert cls.TP_CANCELLATION_ENABLED == True, "TP cancellation must be enabled"
            assert cls.DISABLE_TP_CANCELLATION == False, "TP cancellation cannot be disabled"
            assert cls.STOP_LOSS_ALWAYS_REQUIRED == True, "Stop loss must always be required"
            assert cls.ALLOW_STOP_LOSS_REMOVAL == False, "Stop loss removal forbidden"
            assert cls.HIVE_TRIGGER_CONFIDENCE_MIN == 0.80, "Hive confidence threshold error"
            assert cls.MOMENTUM_PROFIT_THRESHOLD_ATR == 1.8, "Momentum profit threshold error"
            assert cls.MIN_POSITION_AGE_FOR_TP_CANCEL_SECONDS == 60, "Position age requirement error"
            
            # Test trailing stop levels
            assert cls.TRAILING_LEVEL_1_DISTANCE == 1.2, "Trailing level 1 error"
            assert cls.TRAILING_LEVEL_6_DISTANCE == 0.4, "Trailing level 6 error"
            assert cls.MOMENTUM_TRAIL_LOOSENING_FACTOR == 1.15, "Momentum loosening factor error"
            
            # Test code attribution
            assert cls.MOMENTUM_EXTRACTION_PIN == 841921, "Momentum extraction PIN error"
            assert cls.MOMENTUM_SOURCE_FILE.endswith("rbotzilla_golden_age.py"), "Momentum source file error"
            
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
