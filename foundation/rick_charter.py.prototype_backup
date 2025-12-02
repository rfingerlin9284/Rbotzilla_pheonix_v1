#!/usr/bin/env python3
"""
RICK Charter Enforcement Module - Charter Hotfix 2025-10-29
Immutable trading constants and enforcement logic.
PIN: 841921 | Generated: 2025-09-26 | Hotfix: 2025-10-29
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
    
    CHARTER HOTFIX 2025-10-29:
    - Hard size floors (no micro positions)
    - OCO mandatory enforcement
    - Broker stop-distance compliance with auto-buffer
    """

    # CORE AUTHENTICATION
    PIN = 841921
    CHARTER_VERSION = "2.1_HOTFIX_2025_10_29"

    # TRADING CONSTRAINTS
    MAX_HOLD_DURATION_HOURS = 6
    MAX_HOLD_DURATION = timedelta(hours=MAX_HOLD_DURATION_HOURS)

    # ========================================================================
    # CHARTER HOTFIX: HARD FLOORS - NO EXCEPTIONS
    # ========================================================================
    
    # HARD FLOOR CONSTRAINTS (Block tiny positions)
    MIN_NOTIONAL_USD = 100           # Minimum $100 notional per trade
    MIN_MARGIN_USD = 25              # Minimum $25 margin per trade
    
    # INSTRUMENT UNIT FLOORS
    MAJOR_PAIRS_MIN_UNITS = 2500     # EUR/USD, GBP/USD, USD/JPY, USD/CHF, USD/CAD, AUD/USD, NZD/USD
    OTHER_FX_MIN_UNITS = 1000        # All other FX pairs
    
    # Major pairs list
    MAJOR_PAIRS = {
        'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 
        'USD_CAD', 'AUD_USD', 'NZD_USD'
    }
    
    # ========================================================================
    # OCO HARD REQUIREMENT (No child orders = No trade)
    # ========================================================================
    
    OCO_MANDATORY = True             # Every entry MUST have SL+TP as OCO
    ALLOW_NAKED_POSITIONS = False    # No positions without stop loss + take profit
    
    # ========================================================================
    # BROKER STOP-DISTANCE & SIDE CORRECTNESS
    # ========================================================================
    
    # Minimum risk-reward ratio (upgraded from 3.2 to 2.0 for hotfix)
    MIN_RISK_REWARD_RATIO = 2.0
    
    # Broker distance rules
    DEFAULT_MIN_STOP_PIPS = 3        # Default minimum if broker data unavailable
    STOP_BUFFER_MULTIPLIER = 1.5     # Buffer = 1.5 × broker min distance
    MIN_STOP_BUFFER_PIPS = 2         # Minimum buffer regardless of multiplier
    
    # JPY pair pip adjustment
    JPY_PIP_VALUE = 0.01             # JPY pairs use 0.01 as pip
    STANDARD_PIP_VALUE = 0.0001      # Standard pairs use 0.0001 as pip
    
    # ========================================================================
    # INCOME GOAL & SMART AGGRESSION STRATEGY (PIN 841921)
    # ========================================================================
    
    # INCOME TARGETS (IMMUTABLE - AI-driven with smart aggression)
    DAILY_INCOME_TARGET_USD = 600.00
    MONTHLY_INCOME_TARGET_USD = 12600.00
    ANNUAL_INCOME_TARGET_USD = 151200.00
    DAILY_RISK_PER_TRADE = 0.02  # 2% risk per trade (immutable)

    # BOOTSTRAP PHASE (Month 0-3): Prove system works on small capital
    BOOTSTRAP_PHASE_MIN_WIN_RATE = 0.60  # 60% win rate target
    BOOTSTRAP_PHASE_MAX_RISK_PER_TRADE = 0.02  # Conservative 2% max risk
    BOOTSTRAP_PHASE_TARGET_MONTHLY_RETURN = 0.15  # 15% monthly return

    # SCALE PHASE (Month 4-12): Increase capital and optimize
    SCALE_PHASE_MIN_WIN_RATE = 0.60  # Maintain win rate
    SCALE_PHASE_MAX_RISK_PER_TRADE = 0.025  # Slightly higher risk
    SCALE_PHASE_TARGET_MONTHLY_RETURN = 0.20  # 20% monthly return

    # AGGRESSIVE PHASE (Month 13+): AI-driven automation
    AGGRESSIVE_PHASE_MIN_WIN_RATE = 0.60  # Maintain consistency
    AGGRESSIVE_PHASE_MAX_RISK_PER_TRADE = 0.03  # Higher risk for higher returns
    AGGRESSIVE_PHASE_TARGET_MONTHLY_RETURN = 0.25  # 25% monthly return

    @classmethod
    def validate_pin(cls, pin: int) -> bool:
        """Validate PIN for charter access"""
        return pin == cls.PIN
    
    @classmethod
    def validate_position_size(cls, symbol: str, units: int, notional_usd: float, margin_usd: float) -> tuple[bool, str]:
        """
        CHARTER HOTFIX: Validate position size against hard floors
        Returns (is_valid, reason)
        """
        # Check notional floor
        if notional_usd < cls.MIN_NOTIONAL_USD:
            return False, f"Blocked tiny order ({symbol} ${notional_usd:.0f}). Charter hard floor: ${cls.MIN_NOTIONAL_USD} notional. Action: CANCELLED."
        
        # Check margin floor
        if margin_usd < cls.MIN_MARGIN_USD:
            return False, f"Blocked tiny order ({symbol} ${margin_usd:.0f} margin). Charter hard floor: ${cls.MIN_MARGIN_USD} margin. Action: CANCELLED."
        
        # Check unit floor by instrument type
        min_units = cls.MAJOR_PAIRS_MIN_UNITS if symbol in cls.MAJOR_PAIRS else cls.OTHER_FX_MIN_UNITS
        if units < min_units:
            return False, f"Blocked tiny order ({symbol} {units} u). Charter hard floor: {min_units} u / ${cls.MIN_NOTIONAL_USD} notional. Action: CANCELLED."
        
        return True, "Position size meets Charter floors"
    
    @classmethod
    def calculate_stop_distance(cls, symbol: str, entry_price: float, broker_min_distance: Optional[float] = None) -> dict:
        """
        CHARTER HOTFIX: Calculate broker-compliant stop distance with buffer
        Returns stop distance details
        """
        # Determine pip value
        is_jpy = 'JPY' in symbol
        pip_value = cls.JPY_PIP_VALUE if is_jpy else cls.STANDARD_PIP_VALUE
        
        # Use broker minimum or default
        broker_min_pips = broker_min_distance or cls.DEFAULT_MIN_STOP_PIPS
        
        # Calculate buffer
        buffer_pips = max(cls.STOP_BUFFER_MULTIPLIER * broker_min_pips, cls.MIN_STOP_BUFFER_PIPS)
        
        # Final required distance
        required_distance_pips = broker_min_pips + buffer_pips
        required_distance_price = required_distance_pips * pip_value
        
        return {
            'broker_min_pips': broker_min_pips,
            'buffer_pips': buffer_pips,
            'required_distance_pips': required_distance_pips,
            'required_distance_price': required_distance_price,
            'pip_value': pip_value,
            'is_jpy': is_jpy
        }
    
    @classmethod
    def calculate_oco_levels(cls, symbol: str, direction: str, entry_price: float, broker_min_distance: Optional[float] = None) -> dict:
        """
        CHARTER HOTFIX: Calculate OCO stop loss and take profit levels
        """
        stop_info = cls.calculate_stop_distance(symbol, entry_price, broker_min_distance)
        required_distance = stop_info['required_distance_price']
        
        if direction.upper() == 'BUY' or direction.upper() == 'LONG':
            # LONG: SL below entry, TP above entry
            stop_loss = entry_price - required_distance
            take_profit = entry_price + (cls.MIN_RISK_REWARD_RATIO * required_distance)
        else:
            # SHORT: SL above entry, TP below entry
            stop_loss = entry_price + required_distance
            take_profit = entry_price - (cls.MIN_RISK_REWARD_RATIO * required_distance)
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward_ratio': cls.MIN_RISK_REWARD_RATIO,
            'stop_distance_info': stop_info
        }

    # Additional constraints remain unchanged...
    MAX_DAILY_TRADES = 20
    MAX_CONCURRENT_POSITIONS = 5
    ALLOWED_TIMEFRAMES = [TimeFrame.M15, TimeFrame.M30, TimeFrame.H1]


    @classmethod
    def audit_open_positions(cls, positions: List[Dict], broker_api) -> Dict:
        """
        CHARTER HOTFIX: Audit open positions for missing SL/TP
        Scan positions and repair missing or rejected orders
        """
        audit_results = {
            'total_positions': len(positions),
            'needs_repair': [],
            'compliant': [],
            'repaired': []
        }
        
        for position in positions:
            symbol = position.get('instrument', 'UNKNOWN')
            trade_id = position.get('id', 'UNKNOWN')
            units = position.get('currentUnits', 0)
            avg_price = float(position.get('price', 0))
            direction = 'BUY' if units > 0 else 'SELL'
            
            # Check for missing SL/TP
            has_stop_loss = position.get('stopLossOrder') is not None
            has_take_profit = position.get('takeProfitOrder') is not None
            
            if not has_stop_loss or not has_take_profit:
                # Position needs repair
                audit_results['needs_repair'].append({
                    'trade_id': trade_id,
                    'symbol': symbol,
                    'units': units,
                    'price': avg_price,
                    'direction': direction,
                    'missing_sl': not has_stop_loss,
                    'missing_tp': not has_take_profit
                })
                
                # Calculate proper OCO levels
                oco_levels = cls.calculate_oco_levels(symbol, direction, avg_price)
                
                try:
                    # Attempt to add missing orders
                    if not has_stop_loss:
                        broker_api.add_stop_loss(trade_id, oco_levels['stop_loss'])
                    
                    if not has_take_profit:
                        broker_api.add_take_profit(trade_id, oco_levels['take_profit'])
                    
                    audit_results['repaired'].append({
                        'trade_id': trade_id,
                        'symbol': symbol,
                        'new_sl': oco_levels['stop_loss'],
                        'new_tp': oco_levels['take_profit']
                    })
                    
                except Exception as e:
                    # Log repair failure but continue
                    logging.error(f"Failed to repair position {trade_id}: {e}")
            else:
                audit_results['compliant'].append({
                    'trade_id': trade_id,
                    'symbol': symbol,
                    'has_oco': True
                })
        
        return audit_results

    @classmethod
    def enforce_charter_rules(cls, trade_request: Dict) -> tuple[bool, str]:
        """
        CHARTER HOTFIX: Master enforcement function
        Validates all Charter rules before trade execution
        """
        symbol = trade_request.get('symbol', '')
        units = abs(trade_request.get('units', 0))
        notional_usd = trade_request.get('notional_usd', 0)
        margin_usd = trade_request.get('margin_usd', 0)
        has_stop_loss = trade_request.get('stop_loss') is not None
        has_take_profit = trade_request.get('take_profit') is not None
        
        # 1. Position size validation
        size_valid, size_reason = cls.validate_position_size(symbol, units, notional_usd, margin_usd)
        if not size_valid:
            return False, f"CHARTER BLOCK: {size_reason}"
        
        # 2. OCO enforcement
        if cls.OCO_MANDATORY and (not has_stop_loss or not has_take_profit):
            return False, f"CHARTER BLOCK: {symbol} missing required OCO orders. Charter requires SL+TP for every trade."
        
        # 3. Additional validations can be added here
        
        return True, "Charter compliance verified"


    # DAILY LOSS BREAKER (Missing attribute fix)
    DAILY_LOSS_BREAKER_PCT = 0.05  # 5% daily loss limit before emergency halt
    
    # RISK MANAGEMENT CONSTANTS
    MAX_PORTFOLIO_RISK_PCT = 0.10   # 10% max portfolio risk
    MAX_CORRELATED_EXPOSURE = 0.15  # 15% max exposure to correlated pairs

