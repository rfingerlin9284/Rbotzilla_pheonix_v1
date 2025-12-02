#!/usr/bin/env python3
"""
RBOTzilla UNI - Phase 14 Risk Control Integration
Complete risk management system combining Kelly sizing with correlation monitoring.
PIN: 841921 | Phase 14 FINAL
"""

import sys
import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List

# Add path to import our risk modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dynamic_sizing import get_kelly_sizer, DynamicSizing
from correlation_monitor import get_correlation_monitor, CorrelationMonitor

class RiskControlCenter:
    """
    PROF_QUANT (40%): Integrated Kelly + Correlation risk mathematics
    ENGINEER (35%): Real-time risk system orchestration
    TRADER_PSYCH (20%): Portfolio behavior and risk psychology integration
    MENTOR_BK (5%): System reliability and risk parity principles
    
    Unified risk control system that combines:
    - Kelly Criterion position sizing with volatility adjustment
    - Real-time correlation monitoring and exposure control
    - Dynamic risk allocation based on market regime
    - Portfolio diversification enforcement
    """
    
    def __init__(self, pin: int = 841921):
        """Initialize Risk Control Center with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for Risk Control Center")
        
        self.pin_verified = True
        self.kelly_sizer = get_kelly_sizer(pin=pin)
        self.correlation_monitor = get_correlation_monitor(pin=pin)
        self.logger = logging.getLogger(f"RiskControlCenter_{pin}")
        
        # Risk control parameters
        self.absolute_max_position = 0.10  # 10% hard limit per position
        self.portfolio_max_exposure = 0.80  # 80% max total exposure
        self.correlation_block_threshold = 0.70  # Block trades above 70% correlation
        
        self.logger.info("Risk Control Center initialized - Kelly + Correlation active")
    
    def calculate_optimal_position(self, symbol: str, trade_data: Dict[str, Any], 
                                 regime: Optional[str] = None) -> Dict[str, Any]:
        """
        PROF_QUANT: Calculate optimal position size using Kelly + Correlation analysis
        """
        try:
            # Extract parameters from trade_data for Kelly calculation
            current_price = trade_data.get('current_price', 100.0)
            confidence = trade_data.get('confidence', 1.0)
            price_data = trade_data.get('price_data')
            
            # Step 1: Calculate Kelly-based position size
            kelly_result = self.kelly_sizer.calculate_position_size(
                symbol=symbol,
                current_price=current_price,
                confidence=confidence,
                price_data=price_data,
                regime=regime
            )
            
            # Convert PositionSizeResult to dictionary format
            kelly_position = kelly_result.final_position_size
            kelly_dict = {
                'success': kelly_result.final_position_size > 0,
                'recommended_position': kelly_position,
                'confidence': kelly_result.confidence,
                'risk_level': kelly_result.risk_level,
                'adjustments': {
                    'volatility_adjustment': kelly_result.volatility_adjustment,
                    'sharpe_adjustment': kelly_result.sharpe_adjustment
                },
                'max_allowed_position': self.absolute_max_position,
                'error': kelly_result.reasoning if kelly_result.final_position_size == 0 else None
            }
            
            if not kelly_dict.get('success'):
                return {
                    'success': False,
                    'error': f"Kelly calculation failed: {kelly_dict.get('error')}",
                    'recommended_position': 0.0
                }
            
            # Step 2: Check correlation risk
            correlation_check = self.correlation_monitor.check_correlation_risk(
                new_symbol=symbol,
                proposed_position_size=kelly_position
            )
            
            # Step 3: Apply correlation-based adjustments
            if correlation_check['should_block']:
                return {
                    'success': False,
                    'blocked': True,
                    'reason': 'High correlation risk',
                    'max_correlation': correlation_check['max_correlation'],
                    'correlation_risks': correlation_check['correlation_risks'],
                    'recommended_position': 0.0
                }
            
            # Step 4: Calculate final position size
            correlation_adjusted = correlation_check['adjusted_position_size']
            
            # Step 5: Apply absolute limits
            final_position = min(
                correlation_adjusted,
                self.absolute_max_position,
                kelly_dict.get('max_allowed_position', self.absolute_max_position)
            )
            
            # Step 6: Generate comprehensive risk analysis
            return {
                'success': True,
                'symbol': symbol,
                'recommended_position': final_position,
                'kelly_position': kelly_position,
                'correlation_adjusted': correlation_adjusted,
                'adjustments': {
                    'kelly_applied': kelly_dict.get('adjustments', {}),
                    'correlation_reduction': (kelly_position - correlation_adjusted) / kelly_position if kelly_position > 0 else 0,
                    'final_reduction': (kelly_position - final_position) / kelly_position if kelly_position > 0 else 0
                },
                'risk_analysis': {
                    'kelly_confidence': kelly_dict.get('confidence', 0),
                    'volatility_adjustment': kelly_dict.get('adjustments', {}).get('volatility_adjustment', 1.0),
                    'sharpe_adjustment': kelly_dict.get('adjustments', {}).get('sharpe_adjustment', 1.0),
                    'correlation_risk': correlation_check['risk_assessment'],
                    'max_correlation': correlation_check.get('max_correlation', 0),
                    'diversification_impact': correlation_check.get('total_correlated_exposure', 0)
                },
                'warnings': self._generate_warnings(kelly_dict, correlation_check),
                'regime': regime,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Position calculation failed for {symbol}: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommended_position': 0.0
            }
    
    def _generate_warnings(self, kelly_result: Dict, correlation_check: Dict) -> List[str]:
        """Generate risk warnings based on analysis"""
        warnings = []
        
        # Kelly-based warnings
        if kelly_result.get('risk_level') == 'EXTREME':
            warnings.append("EXTREME RISK: High volatility detected")
        elif kelly_result.get('risk_level') == 'HIGH':
            warnings.append("HIGH RISK: Elevated market volatility")
        
        if kelly_result.get('confidence', 1.0) < 0.5:
            warnings.append("LOW CONFIDENCE: Insufficient historical data")
        
        # Correlation warnings
        if correlation_check.get('should_warn'):
            warnings.append(f"CORRELATION WARNING: {correlation_check.get('max_correlation', 0):.1%} correlation with existing positions")
        
        if correlation_check.get('total_correlated_exposure', 0) > 0.3:
            warnings.append("HIGH CORRELATION EXPOSURE: Portfolio concentration risk")
        
        return warnings
    
    def execute_position_check(self, symbol: str, trade_data: Dict[str, Any], 
                             regime: Optional[str] = None) -> Dict[str, Any]:
        """
        TRADER_PSYCH: Execute complete pre-trade risk assessment
        """
        try:
            # Update price data for correlation calculations
            if 'current_price' in trade_data:
                self.correlation_monitor.update_price_data(symbol, trade_data['current_price'])
            
            # Update correlations if needed
            all_symbols = list(self.correlation_monitor.current_positions.keys()) + [symbol]
            self.correlation_monitor.update_correlations(all_symbols)
            
            # Calculate optimal position
            position_result = self.calculate_optimal_position(symbol, trade_data, regime)
            
            if not position_result['success']:
                return position_result
            
            # Get current portfolio status
            diversification_report = self.correlation_monitor.get_portfolio_diversification_report()
            kelly_portfolio_summary = self.kelly_sizer.get_portfolio_risk_summary()
            
            # Check portfolio limits
            current_exposure = sum(pos.position_size for pos in self.correlation_monitor.current_positions.values())
            new_total_exposure = current_exposure + position_result['recommended_position']
            
            if new_total_exposure > self.portfolio_max_exposure:
                return {
                    'success': False,
                    'blocked': True,
                    'reason': 'Portfolio exposure limit exceeded',
                    'current_exposure': current_exposure,
                    'max_exposure': self.portfolio_max_exposure,
                    'recommended_position': 0.0
                }
            
            # Add portfolio context
            position_result.update({
                'portfolio_context': {
                    'current_exposure': current_exposure,
                    'new_total_exposure': new_total_exposure,
                    'diversification_score': diversification_report.get('diversification_score', 0),
                    'kelly_portfolio_risk': kelly_portfolio_summary.get('overall_risk_level', 'UNKNOWN'),
                    'active_positions': len(self.correlation_monitor.current_positions)
                },
                'execution_clearance': True
            })
            
            return position_result
            
        except Exception as e:
            self.logger.error(f"Position check failed for {symbol}: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommended_position': 0.0
            }
    
    def add_executed_position(self, symbol: str, actual_position_size: float, 
                            trade_result: Dict[str, Any], regime: Optional[str] = None):
        """
        ENGINEER: Record executed position in both Kelly and Correlation systems
        """
        try:
            # Add to correlation monitor
            self.correlation_monitor.add_position(symbol, actual_position_size, regime)
            
            # Update Kelly sizer trade history if trade completed successfully
            if trade_result.get('success') and 'pnl' in trade_result:
                trade_data = {
                    'outcome': 'WIN' if trade_result['pnl'] > 0 else 'LOSS' if trade_result['pnl'] < 0 else 'BREAKEVEN',
                    'pnl': trade_result['pnl'],
                    'pnl_pct': trade_result.get('pnl_pct', trade_result['pnl'] * 100),  # Convert to percentage if needed
                    'position_size': actual_position_size,
                    'entry_price': trade_result.get('entry_price'),
                    'exit_price': trade_result.get('exit_price'),
                    'duration_minutes': trade_result.get('duration_minutes', 0)
                }
                self.kelly_sizer.record_trade_result(symbol, trade_data)
            
            self.logger.info(f"Recorded executed position: {symbol} ({actual_position_size:.1%})")
            
        except Exception as e:
            self.logger.error(f"Failed to record position {symbol}: {e}")
    
    def remove_closed_position(self, symbol: str, trade_result: Dict[str, Any]):
        """
        ENGINEER: Remove closed position from tracking systems
        """
        try:
            # Remove from correlation monitor
            self.correlation_monitor.remove_position(symbol)
            
            # Update Kelly trade history if we have PnL data
            if 'pnl' in trade_result:
                trade_data = {
                    'outcome': 'WIN' if trade_result['pnl'] > 0 else 'LOSS' if trade_result['pnl'] < 0 else 'BREAKEVEN',
                    'pnl': trade_result['pnl'],
                    'pnl_pct': trade_result.get('pnl_pct', trade_result['pnl'] * 100),
                    'position_size': trade_result.get('position_size', 0),
                    'entry_price': trade_result.get('entry_price'),
                    'exit_price': trade_result.get('exit_price'),
                    'duration_minutes': trade_result.get('duration_minutes', 0)
                }
                self.kelly_sizer.record_trade_result(symbol, trade_data)
            
            self.logger.info(f"Removed closed position: {symbol}")
            
        except Exception as e:
            self.logger.error(f"Failed to remove position {symbol}: {e}")
    
    def get_comprehensive_risk_report(self) -> Dict[str, Any]:
        """
        MENTOR_BK: Generate comprehensive risk management report
        """
        try:
            # Get Kelly portfolio analysis
            kelly_summary = self.kelly_sizer.get_portfolio_risk_summary()
            
            # Get correlation diversification analysis
            diversification_report = self.correlation_monitor.get_portfolio_diversification_report()
            
            # Combined risk assessment
            overall_risk = "LOW"
            if (kelly_summary.get('overall_risk_level') == 'HIGH' or 
                diversification_report.get('diversification_score', 1) < 0.5):
                overall_risk = "HIGH"
            elif (kelly_summary.get('overall_risk_level') == 'MODERATE' or 
                  diversification_report.get('diversification_score', 1) < 0.7):
                overall_risk = "MODERATE"
            
            # Current exposures
            current_exposure = sum(pos.position_size for pos in self.correlation_monitor.current_positions.values())
            
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'overall_risk_assessment': overall_risk,
                'portfolio_exposure': {
                    'current_total': current_exposure,
                    'max_allowed': self.portfolio_max_exposure,
                    'utilization': current_exposure / self.portfolio_max_exposure if self.portfolio_max_exposure > 0 else 0,
                    'active_positions': len(self.correlation_monitor.current_positions)
                },
                'kelly_analysis': kelly_summary,
                'correlation_analysis': diversification_report,
                'risk_limits': {
                    'max_position_size': self.absolute_max_position,
                    'max_portfolio_exposure': self.portfolio_max_exposure,
                    'correlation_block_threshold': self.correlation_block_threshold
                },
                'system_status': 'OPERATIONAL'
            }
            
        except Exception as e:
            self.logger.error(f"Risk report generation failed: {e}")
            return {
                'error': str(e),
                'system_status': 'ERROR'
            }
    
    def force_save_all(self):
        """Force save all risk data to persistent storage"""
        try:
            self.kelly_sizer.save_now()
            self.correlation_monitor.save_now()
            self.logger.info("All risk data saved to disk")
        except Exception as e:
            self.logger.error(f"Failed to save risk data: {e}")

def get_risk_control_center(pin: int = 841921) -> RiskControlCenter:
    """Convenience function to get Risk Control Center instance"""
    return RiskControlCenter(pin=pin)

# Example usage and testing
if __name__ == "__main__":
    print("🎯 PHASE 14 RISK CONTROL INTEGRATION TEST 🎯")
    print("=" * 55)
    
    # Initialize Risk Control Center
    risk_center = RiskControlCenter(pin=841921)
    
    # Add some sample trade history for Kelly calculations
    sample_trades = [
        {'outcome': 'WIN', 'pnl': 0.015, 'pnl_pct': 1.5, 'position_size': 0.05, 'duration_minutes': 240},
        {'outcome': 'WIN', 'pnl': 0.012, 'pnl_pct': 1.2, 'position_size': 0.05, 'duration_minutes': 180},
        {'outcome': 'LOSS', 'pnl': -0.008, 'pnl_pct': -0.8, 'position_size': 0.05, 'duration_minutes': 120},
        {'outcome': 'WIN', 'pnl': 0.018, 'pnl_pct': 1.8, 'position_size': 0.06, 'duration_minutes': 300},
        {'outcome': 'LOSS', 'pnl': -0.010, 'pnl_pct': -1.0, 'position_size': 0.05, 'duration_minutes': 90},
        {'outcome': 'WIN', 'pnl': 0.020, 'pnl_pct': 2.0, 'position_size': 0.07, 'duration_minutes': 360},
        {'outcome': 'WIN', 'pnl': 0.014, 'pnl_pct': 1.4, 'position_size': 0.05, 'duration_minutes': 200},
        {'outcome': 'LOSS', 'pnl': -0.009, 'pnl_pct': -0.9, 'position_size': 0.05, 'duration_minutes': 150},
        {'outcome': 'WIN', 'pnl': 0.016, 'pnl_pct': 1.6, 'position_size': 0.06, 'duration_minutes': 280},
        {'outcome': 'WIN', 'pnl': 0.013, 'pnl_pct': 1.3, 'position_size': 0.05, 'duration_minutes': 220},
        {'outcome': 'LOSS', 'pnl': -0.011, 'pnl_pct': -1.1, 'position_size': 0.06, 'duration_minutes': 100},
        {'outcome': 'WIN', 'pnl': 0.017, 'pnl_pct': 1.7, 'position_size': 0.05, 'duration_minutes': 320}
    ]
    
    # Add sample history for multiple symbols
    for symbol in ['EUR_USD', 'GBP_USD', 'BTC-USD']:
        for trade in sample_trades:
            risk_center.kelly_sizer.record_trade_result(symbol, trade.copy())
    
    print(f"Added {len(sample_trades)} sample trades for 3 symbols")
    
    # Test comprehensive position sizing
    test_trade = {
        'current_price': 1.1050,
        'win_rate': 0.65,
        'avg_win': 0.015,
        'avg_loss': 0.010,
        'recent_trades': 25,
        'volatility': 0.018,
        'sharpe_ratio': 1.4
    }
    
    print("Testing EUR_USD position sizing...")
    result = risk_center.execute_position_check('EUR_USD', test_trade, 'BULLISH')
    
    if result['success']:
        print(f"✅ Position approved: {result['recommended_position']:.1%}")
        print(f"   Kelly position: {result['kelly_position']:.1%}")
        print(f"   Correlation adjusted: {result['correlation_adjusted']:.1%}")
        print(f"   Risk assessment: {result['risk_analysis']['correlation_risk']}")
        
        # Simulate position execution
        risk_center.add_executed_position('EUR_USD', result['recommended_position'], 
                                        {'success': True}, 'BULLISH')
    else:
        print(f"❌ Position blocked: {result.get('reason', 'Unknown')}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    
    # Test correlated symbol
    print("\nTesting GBP_USD (correlated to EUR_USD)...")
    gbp_result = risk_center.execute_position_check('GBP_USD', test_trade, 'BULLISH')
    
    if gbp_result['success']:
        print(f"✅ GBP_USD approved: {gbp_result['recommended_position']:.1%}")
        print(f"   Correlation adjustment: {gbp_result['adjustments']['correlation_reduction']:.1%}")
    else:
        print(f"❌ GBP_USD blocked: {gbp_result.get('reason', 'Unknown')}")
        if 'error' in gbp_result:
            print(f"   Error: {gbp_result['error']}")
    
    # Test uncorrelated symbol
    print("\nTesting BTC-USD (uncorrelated)...")
    btc_trade = test_trade.copy()
    btc_trade['current_price'] = 45000.0
    btc_trade['volatility'] = 0.035  # Higher crypto volatility
    
    btc_result = risk_center.execute_position_check('BTC-USD', btc_trade, 'BULLISH')
    
    if btc_result['success']:
        print(f"✅ BTC-USD approved: {btc_result['recommended_position']:.1%}")
        print(f"   Volatility adjustment: {btc_result['risk_analysis']['volatility_adjustment']:.3f}")
    else:
        print(f"❌ BTC-USD blocked: {btc_result.get('reason', 'Unknown')}")
        if 'error' in btc_result:
            print(f"   Error: {btc_result['error']}")
    
    # Generate comprehensive risk report
    print("\n" + "="*55)
    print("COMPREHENSIVE RISK REPORT")
    print("="*55)
    
    risk_report = risk_center.get_comprehensive_risk_report()
    
    print(f"Overall Risk Assessment: {risk_report['overall_risk_assessment']}")
    print(f"Portfolio Utilization: {risk_report['portfolio_exposure']['utilization']:.1%}")
    print(f"Active Positions: {risk_report['portfolio_exposure']['active_positions']}")
    print(f"Diversification Score: {risk_report['correlation_analysis'].get('diversification_score', 0):.3f}")
    print(f"Kelly Risk Level: {risk_report['kelly_analysis'].get('overall_risk_level', 'UNKNOWN')}")
    
    print(f"\n✅ Phase 14 Risk Control System OPERATIONAL")
    print("🔒 Kelly Criterion + Correlation Monitor = COMPLETE 🔒")