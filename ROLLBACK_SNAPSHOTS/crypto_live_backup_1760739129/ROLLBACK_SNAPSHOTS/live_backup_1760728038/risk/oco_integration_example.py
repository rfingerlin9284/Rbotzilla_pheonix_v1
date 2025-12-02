#!/usr/bin/env python3
"""
RBOTzilla UNI - OCO Validator Integration Example
Phase 24 - Trading Engine Integration with OCO Enforcement
PIN: 841921

This example demonstrates how to integrate the OCO validator with the main trading engine.
Shows both periodic validation and continuous monitoring approaches.
"""

import os
import sys
import time
import threading
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from risk.oco_validator import OCOValidator, validate_positions_once

class TradingEngineWithOCO:
    """
    Example trading engine with integrated OCO validation
    
    This shows how to integrate the OCO validator into the main trading loop
    to ensure all positions have proper risk controls.
    """
    
    def __init__(self, broker, validation_interval=60):
        self.broker = broker
        self.oco_validator = OCOValidator(
            max_risk_per_position=0.02,  # 2% max risk per position
            force_close_threshold=0.05,  # 5% force close threshold
            validation_interval=validation_interval
        )
        self.running = False
        self.validation_thread = None
        
        print("🔧 Trading Engine with OCO Validation initialized")
        print(f"   Validation interval: {validation_interval}s")
        print(f"   Max risk per position: 2%")
        print(f"   Force close threshold: 5%")
    
    def start_trading(self):
        """Start the main trading engine with OCO validation"""
        print("\n🚀 Starting trading engine with OCO enforcement...")
        self.running = True
        
        # Start OCO validation in separate thread
        self.validation_thread = threading.Thread(
            target=self._continuous_oco_validation,
            daemon=True
        )
        self.validation_thread.start()
        
        # Main trading loop
        try:
            self._main_trading_loop()
        except KeyboardInterrupt:
            print("\n⏹️  Stopping trading engine...")
            self.running = False
            if self.validation_thread:
                self.validation_thread.join(timeout=5)
    
    def _main_trading_loop(self):
        """Main trading loop with OCO validation integration"""
        loop_count = 0
        
        while self.running:
            loop_count += 1
            print(f"\n📊 Trading Loop #{loop_count} - {datetime.now().strftime('%H:%M:%S')}")
            
            try:
                # 1. Regular trading logic (mock)
                self._execute_trading_strategy()
                
                # 2. OCO validation (every 5 loops for demo)
                if loop_count % 5 == 0:
                    self._validate_oco_compliance()
                
                # 3. Risk monitoring
                self._monitor_risk_exposure()
                
                # Sleep before next loop
                time.sleep(10)
                
            except Exception as e:
                print(f"❌ Error in trading loop: {e}")
                time.sleep(5)
    
    def _execute_trading_strategy(self):
        """Mock trading strategy execution"""
        # This would contain actual trading logic
        print("   📈 Executing trading strategies...")
        print("   📊 Analyzing market conditions...")
        print("   💹 Looking for entry opportunities...")
        
        # Simulate occasional new position
        import random
        if random.random() < 0.1:  # 10% chance
            print("   🎯 New position detected - OCO validation will verify risk controls")
    
    def _validate_oco_compliance(self):
        """Validate OCO compliance for all open positions"""
        print("   🔍 Running OCO compliance check...")
        
        try:
            results = self.oco_validator.validate_open_positions(self.broker)
            
            if not results:
                print("   ✅ No open positions - OCO compliance satisfied")
                return
            
            valid_positions = [r for r in results if r.is_valid]
            violations = [r for r in results if not r.is_valid]
            
            print(f"   📊 OCO Status: {len(valid_positions)} valid, {len(violations)} violations")
            
            if violations:
                print(f"   ⚠️  {len(violations)} positions with OCO violations detected!")
                for violation in violations:
                    print(f"      🚨 {violation.symbol}: {violation.action_taken} (Risk: {violation.risk_exposure:.1%})")
            else:
                print("   ✅ All positions have proper OCO links")
                
        except Exception as e:
            print(f"   ❌ OCO validation error: {e}")
    
    def _monitor_risk_exposure(self):
        """Monitor overall risk exposure"""
        stats = self.oco_validator.get_validation_stats()
        
        if stats['total_validations'] > 0:
            violation_rate = stats['violation_rate'] * 100
            print(f"   📈 OCO Stats: {stats['total_validations']} checks, "
                  f"{stats['violations_found']} violations ({violation_rate:.1f}%), "
                  f"{stats['positions_closed']} force-closed")
    
    def _continuous_oco_validation(self):
        """Continuous OCO validation in background thread"""
        print("🔄 Starting continuous OCO validation thread...")
        
        while self.running:
            try:
                # Run validation
                results = self.oco_validator.validate_open_positions(self.broker)
                
                # Check for critical violations
                critical_violations = [r for r in results if not r.is_valid and r.risk_exposure > 0.05]
                if critical_violations:
                    print(f"\n🚨 CRITICAL OCO VIOLATIONS: {len(critical_violations)} high-risk positions!")
                    for violation in critical_violations:
                        print(f"   ⚠️  {violation.symbol}: {violation.action_taken}")
                
                # Sleep until next validation
                time.sleep(self.oco_validator.validation_interval)
                
            except Exception as e:
                print(f"🚨 OCO validation thread error: {e}")
                time.sleep(30)  # Wait longer on error

class MockBrokerWithPositions:
    """Mock broker with realistic position and order data"""
    
    def __init__(self):
        self.name = "enhanced_mock_broker"
        self.positions = [
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
                'symbol': 'GBP_USD', 
                'size': -8000,  # Short position
                'entry_price': 1.2500,
                'current_price': 1.2480,
                'unrealized_pnl': 16.0
            },
            {
                'id': 'pos_003',
                'symbol': 'BTC_USD',
                'size': 0.05,
                'entry_price': 45000.0,
                'current_price': 46000.0,
                'unrealized_pnl': 50.0
            }
        ]
        
        self.orders = [
            # EUR_USD has full OCO
            {
                'id': 'ord_tp_001',
                'symbol': 'EUR_USD',
                'type': 'take_profit',
                'side': 'sell',
                'size': 10000,
                'price': 1.1100
            },
            {
                'id': 'ord_sl_001',
                'symbol': 'EUR_USD',
                'type': 'stop_loss',
                'side': 'sell',
                'size': 10000,
                'price': 1.1000
            },
            # GBP_USD has only stop loss (missing TP)
            {
                'id': 'ord_sl_002',
                'symbol': 'GBP_USD',
                'type': 'stop_loss',
                'side': 'buy',
                'size': 8000,
                'price': 1.2550
            },
            # BTC_USD has no OCO orders (high risk!)
        ]
        
        self.balance = 25000.0
        self.closed_positions = []
    
    def get_open_positions(self):
        """Return open positions"""
        return [pos for pos in self.positions if pos['id'] not in self.closed_positions]
    
    def get_orders(self):
        """Return pending orders"""
        return self.orders
    
    def get_account_balance(self):
        """Return account balance"""
        return self.balance
    
    def close_position(self, position_id):
        """Close a position"""
        print(f"🔒 Broker: Force-closing position {position_id} due to OCO violation")
        self.closed_positions.append(position_id)
        return True

def run_integration_demo():
    """Run the OCO validator integration demonstration"""
    print("🎯 RBOTzilla UNI - OCO Validator Integration Demo")
    print("=" * 60)
    print("PIN: 841921 | Phase 24 | OCO Enforcement Integration")
    print()
    
    # Create mock broker with realistic data
    print("📊 Creating mock broker with test positions...")
    broker = MockBrokerWithPositions()
    
    positions = broker.get_open_positions()
    orders = broker.get_orders()
    
    print(f"   Positions: {len(positions)}")
    for pos in positions:
        print(f"     {pos['symbol']}: {pos['size']} @ {pos['entry_price']}")
    
    print(f"   Orders: {len(orders)}")
    for order in orders:
        print(f"     {order['symbol']} {order['type']}: {order.get('price', 'market')}")
    
    print()
    
    # Test single validation
    print("🔍 Testing single OCO validation...")
    results = validate_positions_once(broker, max_risk_per_position=0.02)
    
    print("\n📊 Validation Results:")
    for result in results:
        status = "✅ VALID" if result.is_valid else "❌ INVALID"
        print(f"   {result.symbol}: {status}")
        print(f"     TP: {result.has_take_profit} | SL: {result.has_stop_loss}")
        print(f"     Risk: {result.risk_exposure:.1%} | Action: {result.action_taken}")
    
    violations = [r for r in results if not r.is_valid]
    print(f"\n📈 Summary: {len(results)} positions, {len(violations)} OCO violations")
    
    # Offer to run trading engine demo
    print("\n" + "="*60)
    print("🚀 Integration Demo Options:")
    print("   1. Run single validation (completed above)")
    print("   2. Run trading engine with continuous OCO validation")
    print("   3. Exit demo")
    
    try:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "2":
            print("\n🔄 Starting trading engine with OCO validation...")
            print("   (Press Ctrl+C to stop)")
            
            # Create trading engine with OCO validation
            engine = TradingEngineWithOCO(broker, validation_interval=30)
            engine.start_trading()
            
        else:
            print("Demo complete - thanks for testing OCO validation!")
            
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    
    print("\n🎉 OCO Validator Integration Demo Complete!")

if __name__ == "__main__":
    run_integration_demo()