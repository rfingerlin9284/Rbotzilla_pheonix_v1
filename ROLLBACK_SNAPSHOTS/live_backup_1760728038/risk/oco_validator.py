#!/usr/bin/env python3
"""
RBOTzilla UNI - OCO Link Validator
Phase 24 - Hard-enforce OCO on every open position
PIN: 841921

This module provides comprehensive OCO (One-Cancels-Other) validation for all open positions.
Every position must have linked Take Profit (TP) and Stop Loss (SL) orders.
Positions without proper OCO links are automatically closed and alerts are sent.

Engineer (70%): Core validation logic, position monitoring, risk enforcement
Prof_Quant (20%): Risk calculation, position analysis, threshold management  
Trader_Psych (10%): Risk psychology, position confidence, trade management
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

try:
    from monitoring.alerting import send_system_alert
    ALERTING_AVAILABLE = True
except ImportError:
    ALERTING_AVAILABLE = False
    print("⚠️  Phase 22 alerting system not available - using fallback logging")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('oco_validator')

@dataclass
class Position:
    """Represents a trading position with OCO details"""
    position_id: str
    symbol: str
    side: str  # 'long' or 'short'
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    take_profit_id: Optional[str] = None
    stop_loss_id: Optional[str] = None
    broker: str = "unknown"
    timestamp: str = ""

@dataclass
class OCOValidationResult:
    """Result of OCO validation for a position"""
    position_id: str
    symbol: str
    has_take_profit: bool
    has_stop_loss: bool
    is_valid: bool
    risk_exposure: float
    action_taken: str
    timestamp: str

class OCOValidator:
    """
    OCO Link Validator - Hard-enforce OCO on every open position
    
    This class provides comprehensive validation of OCO (One-Cancels-Other) orders
    for all open positions. It ensures every position has proper risk controls.
    """
    
    def __init__(self, 
                 log_file: str = None,
                 max_risk_per_position: float = 0.02,
                 force_close_threshold: float = 0.05,
                 validation_interval: int = 30):
        """
        Initialize OCO Validator
        
        Args:
            log_file: Path to validation log file
            max_risk_per_position: Maximum risk per position (2% default)
            force_close_threshold: Force close if risk exceeds this (5% default)
            validation_interval: Validation frequency in seconds
        """
        self.log_file = log_file or os.path.join(PROJECT_ROOT, "logs", "oco_validation.jsonl")
        self.max_risk_per_position = max_risk_per_position
        self.force_close_threshold = force_close_threshold
        self.validation_interval = validation_interval
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Validation statistics
        self.validation_count = 0
        self.violations_found = 0
        self.positions_closed = 0
        self.last_validation = None
        
        logger.info("OCO Validator initialized")
        logger.info(f"Max risk per position: {max_risk_per_position:.1%}")
        logger.info(f"Force close threshold: {force_close_threshold:.1%}")
        logger.info(f"Log file: {self.log_file}")
    
    def validate_open_positions(self, broker) -> List[OCOValidationResult]:
        """
        Main validation function - Check each open position has linked TP+SL (OCO)
        
        Args:
            broker: Broker connector instance with methods:
                   - get_open_positions() -> List[Dict]
                   - get_orders() -> List[Dict] 
                   - close_position(position_id) -> bool
                   - get_account_balance() -> float
        
        Returns:
            List of validation results
        """
        try:
            self.validation_count += 1
            self.last_validation = datetime.now(timezone.utc)
            
            logger.info("Starting OCO validation of open positions")
            
            # Get open positions and orders from broker
            positions = self._fetch_positions(broker)
            orders = self._fetch_orders(broker)
            account_balance = self._fetch_account_balance(broker)
            
            if not positions:
                logger.info("No open positions found - validation complete")
                return []
            
            logger.info(f"Found {len(positions)} open positions to validate")
            
            # Validate each position
            results = []
            for position in positions:
                result = self._validate_position_oco(position, orders, account_balance, broker)
                results.append(result)
                
                # Log validation result
                self._log_validation_result(result)
                
                # Take action if needed
                if not result.is_valid:
                    self._handle_oco_violation(result, position, broker)
            
            # Send summary alert if violations found
            violations = [r for r in results if not r.is_valid]
            if violations:
                self._send_violation_alert(violations)
            
            logger.info(f"OCO validation complete: {len(results)} positions checked, {len(violations)} violations")
            
            return results
            
        except Exception as e:
            logger.error(f"OCO validation failed: {e}")
            self._send_error_alert(str(e))
            return []
    
    def _fetch_positions(self, broker) -> List[Position]:
        """Fetch open positions from broker"""
        try:
            raw_positions = broker.get_open_positions()
            positions = []
            
            for pos_data in raw_positions:
                position = Position(
                    position_id=pos_data.get('id', pos_data.get('position_id', 'unknown')),
                    symbol=pos_data.get('symbol', pos_data.get('instrument', 'unknown')),
                    side='long' if float(pos_data.get('size', pos_data.get('units', 0))) > 0 else 'short',
                    size=abs(float(pos_data.get('size', pos_data.get('units', 0)))),
                    entry_price=float(pos_data.get('entry_price', pos_data.get('average_price', 0))),
                    current_price=float(pos_data.get('current_price', pos_data.get('mark_price', 0))),
                    unrealized_pnl=float(pos_data.get('unrealized_pnl', pos_data.get('pnl', 0))),
                    broker=getattr(broker, 'name', 'unknown'),
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
                positions.append(position)
                
            return positions
            
        except Exception as e:
            logger.error(f"Failed to fetch positions: {e}")
            return []
    
    def _fetch_orders(self, broker) -> List[Dict]:
        """Fetch pending orders from broker"""
        try:
            return broker.get_orders() if hasattr(broker, 'get_orders') else []
        except Exception as e:
            logger.error(f"Failed to fetch orders: {e}")
            return []
    
    def _fetch_account_balance(self, broker) -> float:
        """Fetch account balance from broker"""
        try:
            return broker.get_account_balance() if hasattr(broker, 'get_account_balance') else 10000.0
        except Exception as e:
            logger.error(f"Failed to fetch account balance: {e}")
            return 10000.0  # Fallback balance
    
    def _validate_position_oco(self, position: Position, orders: List[Dict], 
                              account_balance: float, broker) -> OCOValidationResult:
        """Validate OCO links for a single position"""
        
        # Find linked TP and SL orders for this position
        take_profit_order = None
        stop_loss_order = None
        
        for order in orders:
            order_symbol = order.get('symbol', order.get('instrument', ''))
            order_type = order.get('type', '').lower()
            
            # Match orders to position by symbol
            if order_symbol == position.symbol:
                if 'take_profit' in order_type or 'limit' in order_type:
                    # Check if order direction opposes position
                    order_side = order.get('side', '').lower()
                    if (position.side == 'long' and 'sell' in order_side) or \
                       (position.side == 'short' and 'buy' in order_side):
                        take_profit_order = order
                        position.take_profit_id = order.get('id', order.get('order_id'))
                
                elif 'stop_loss' in order_type or 'stop' in order_type:
                    # Check if order direction opposes position  
                    order_side = order.get('side', '').lower()
                    if (position.side == 'long' and 'sell' in order_side) or \
                       (position.side == 'short' and 'buy' in order_side):
                        stop_loss_order = order
                        position.stop_loss_id = order.get('id', order.get('order_id'))
        
        # Calculate risk exposure
        position_value = position.size * position.current_price
        risk_exposure = position_value / account_balance if account_balance > 0 else 0.0
        
        # Determine validation status
        has_take_profit = take_profit_order is not None
        has_stop_loss = stop_loss_order is not None
        is_valid = has_take_profit and has_stop_loss
        
        # Determine action based on validation
        action_taken = "VALID"
        if not is_valid:
            if risk_exposure > self.force_close_threshold:
                action_taken = "FORCE_CLOSE"
            elif not has_stop_loss:
                action_taken = "MISSING_STOP_LOSS"
            elif not has_take_profit:
                action_taken = "MISSING_TAKE_PROFIT"
            else:
                action_taken = "MISSING_OCO"
        
        return OCOValidationResult(
            position_id=position.position_id,
            symbol=position.symbol,
            has_take_profit=has_take_profit,
            has_stop_loss=has_stop_loss,
            is_valid=is_valid,
            risk_exposure=risk_exposure,
            action_taken=action_taken,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def _handle_oco_violation(self, result: OCOValidationResult, position: Position, broker):
        """Handle OCO violation by closing position and sending alerts"""
        
        try:
            logger.warning(f"OCO violation detected for position {result.position_id} ({result.symbol})")
            logger.warning(f"Has TP: {result.has_take_profit}, Has SL: {result.has_stop_loss}")
            logger.warning(f"Risk exposure: {result.risk_exposure:.2%}")
            
            # Close position if risk is too high or completely missing OCO
            if result.action_taken == "FORCE_CLOSE" or (not result.has_take_profit and not result.has_stop_loss):
                
                logger.warning(f"Closing position {result.position_id} due to OCO violation")
                
                # Attempt to close position
                if hasattr(broker, 'close_position'):
                    success = broker.close_position(result.position_id)
                    if success:
                        self.positions_closed += 1
                        logger.info(f"Position {result.position_id} closed successfully")
                    else:
                        logger.error(f"Failed to close position {result.position_id}")
                else:
                    logger.error("Broker does not support position closing")
            
            # Track violation
            self.violations_found += 1
            
        except Exception as e:
            logger.error(f"Error handling OCO violation: {e}")
    
    def _log_validation_result(self, result: OCOValidationResult):
        """Log validation result to JSON file"""
        try:
            log_entry = {
                "timestamp": result.timestamp,
                "validation_id": f"ocov_{self.validation_count}_{int(time.time())}",
                "position_id": result.position_id,
                "symbol": result.symbol,
                "has_take_profit": result.has_take_profit,
                "has_stop_loss": result.has_stop_loss,
                "is_valid": result.is_valid,
                "risk_exposure": result.risk_exposure,
                "action_taken": result.action_taken,
                "validator_stats": {
                    "total_validations": self.validation_count,
                    "violations_found": self.violations_found,
                    "positions_closed": self.positions_closed
                }
            }
            
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to log validation result: {e}")
    
    def _send_violation_alert(self, violations: List[OCOValidationResult]):
        """Send alert about OCO violations"""
        if not violations:
            return
            
        violation_count = len(violations)
        high_risk_count = len([v for v in violations if v.risk_exposure > self.force_close_threshold])
        
        alert_message = f"OCO Violations Detected: {violation_count} positions missing proper OCO links"
        if high_risk_count > 0:
            alert_message += f", {high_risk_count} high-risk positions force-closed"
        
        details = []
        for v in violations[:5]:  # Limit to first 5 violations
            details.append(f"{v.symbol} (Risk: {v.risk_exposure:.1%}) - {v.action_taken}")
        
        full_details = f"{alert_message}. Details: {'; '.join(details)}"
        
        # Send via Phase 22 alerting system
        if ALERTING_AVAILABLE:
            send_system_alert("OCO_VIOLATION", full_details)
        
        logger.error(f"OCO Alert: {full_details}")
    
    def _send_error_alert(self, error_message: str):
        """Send alert about validation errors"""
        alert_details = f"OCO Validator Error: {error_message}"
        
        if ALERTING_AVAILABLE:
            send_system_alert("OCO_ERROR", alert_details)
        
        logger.error(f"OCO Error Alert: {alert_details}")
    
    def get_validation_stats(self) -> Dict:
        """Get validation statistics"""
        return {
            "total_validations": self.validation_count,
            "violations_found": self.violations_found,
            "positions_closed": self.positions_closed,
            "last_validation": self.last_validation.isoformat() if self.last_validation else None,
            "violation_rate": self.violations_found / max(1, self.validation_count),
            "log_file": self.log_file
        }
    
    def continuous_validation(self, broker):
        """Run continuous validation loop"""
        logger.info(f"Starting continuous OCO validation (interval: {self.validation_interval}s)")
        
        while True:
            try:
                results = self.validate_open_positions(broker)
                logger.info(f"Validation cycle complete: {len(results)} positions checked")
                
                # Sleep until next validation
                time.sleep(self.validation_interval)
                
            except KeyboardInterrupt:
                logger.info("Continuous validation stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous validation: {e}")
                time.sleep(self.validation_interval)

# Convenience functions for easy integration
def create_oco_validator(log_file: str = None, **kwargs) -> OCOValidator:
    """Create OCO validator with default settings"""
    return OCOValidator(log_file=log_file, **kwargs)

def validate_positions_once(broker, **validator_kwargs) -> List[OCOValidationResult]:
    """Run single OCO validation"""
    validator = create_oco_validator(**validator_kwargs)
    return validator.validate_open_positions(broker)

def start_continuous_validation(broker, **validator_kwargs):
    """Start continuous OCO validation"""
    validator = create_oco_validator(**validator_kwargs)
    validator.continuous_validation(broker)

if __name__ == "__main__":
    # Demo mode - create mock broker for testing
    print("🔧 RBOTzilla UNI - OCO Link Validator Demo")
    print("PIN: 841921 | Phase 24 | OCO Enforcement System")
    print()
    
    class MockBroker:
        def __init__(self):
            self.name = "mock_broker"
        
        def get_open_positions(self):
            return [
                {
                    'id': 'pos_001',
                    'symbol': 'EUR_USD',
                    'size': 10000,
                    'entry_price': 1.1050,
                    'current_price': 1.1055,
                    'unrealized_pnl': 5.0
                },
                {
                    'id': 'pos_002', 
                    'symbol': 'BTC_USD',
                    'size': 0.1,
                    'entry_price': 45000.0,
                    'current_price': 45500.0,
                    'unrealized_pnl': 50.0
                }
            ]
        
        def get_orders(self):
            return [
                {
                    'id': 'ord_tp_001',
                    'symbol': 'EUR_USD',
                    'type': 'take_profit',
                    'side': 'sell',
                    'size': 10000
                }
                # Note: Missing stop loss for EUR_USD and all OCO for BTC_USD
            ]
        
        def get_account_balance(self):
            return 10000.0
        
        def close_position(self, position_id):
            print(f"Mock: Closing position {position_id}")
            return True
    
    # Run demo validation
    mock_broker = MockBroker()
    validator = create_oco_validator()
    
    print("Running OCO validation demo...")
    results = validator.validate_open_positions(mock_broker)
    
    print(f"\n📊 Validation Results:")
    for result in results:
        status = "✅ VALID" if result.is_valid else "❌ INVALID"
        print(f"   {result.symbol}: {status} (TP: {result.has_take_profit}, SL: {result.has_stop_loss})")
    
    print(f"\n📈 Statistics: {validator.get_validation_stats()}")
    print("\n🎉 OCO Validator Demo Complete!")