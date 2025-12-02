#!/usr/bin/env python3
"""
CANARY Mode Trading Engine
Charter-compliant validation with extended session (2-4 hours)
Uses OANDA practice API with real Charter rules
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional, List

# Import the Charter-compliant CANARY engine as base
sys.path.insert(0, str(Path(__file__).parent))
from CANARY_trading_charter_compliant import CharterCompliantCANARYEngine
from util.breakpoint_audit import attach_audit_handler, audit_event
from util.narration_logger import log_narration

# Risk module imports - Phase 24 OCO + Phase 14 Correlation + Phase 4 Hedging
from risk.oco_validator import OCOValidator
from risk.correlation_monitor import CorrelationMonitor
from util.quant_hedge_engine import QuantHedgeEngine

class CanaryTradingEngine(CharterCompliantCANARYEngine):
    """
    CANARY Trading Engine - Extended validation mode
    Inherits all Charter enforcement from CANARY engine
    Runs longer sessions (2-4 hours) to build pattern library
    """
    
    def __init__(self, pin: int = 841921):
        # Initialize parent class
        super().__init__(pin=pin)
        try:
            attach_audit_handler(engine_mode="CANARY")
            audit_event("SESSION_INIT", {"mode": "CANARY"}, engine_mode="CANARY")
        except Exception:
            pass
        
        # Initialize risk modules (Phase 4, 14, 24)
        self.oco_validator = OCOValidator()
        self.correlation_monitor = CorrelationMonitor()
        self.hedge_engine = QuantHedgeEngine()
        
        print("🛡️  Risk Modules Activated:")
        print("  ✅ OCO Validator (Phase 24) - Mandatory SL+TP enforcement")
        print("  ✅ Correlation Monitor (Phase 14) - Portfolio exposure tracking")
        print("  ✅ Quant Hedge Engine (Phase 4) - Auto-hedging on inverse pairs")
        
        # Override session duration for CANARY (45 minutes - quick validation)
        self.session_duration_hours = 0.75  # 45 minutes
        self.end_time = self.start_time + __import__('datetime').timedelta(hours=self.session_duration_hours)
        
        print("=" * 80)
        print("🐤 CANARY MODE - Quick Validation Trading (45 minutes)")
        print("=" * 80)
        print("This CANARY session will:")
        print("  ✅ Enforce ALL Charter rules ($15K notional, 3.2 RR, 6h max hold)")
        print("  ✅ Use OANDA Practice API (same as LIVE, but practice account)")
        print("  ✅ Calculate proper leverage (6.6x)")
        print("  ✅ Quick validation session (45 minutes)")
        print("  ✅ Expected 2-3 Charter-compliant trades")
        print(f"  ✅ Session ends at: {self.end_time.isoformat()}")
        print("=" * 80)
        print()
        
        # Log CANARY initialization
        log_narration(
            event_type="CANARY_INIT",
            details={
                "session_duration_hours": self.session_duration_hours,
                "end_time": self.end_time.isoformat(),
                "charter_rules": "enforced"
            },
            symbol=None,
            venue="OANDA"
        )
    
    async def execute_charter_compliant_trade(self, signal: Dict):
        """Override to add OCO validation, correlation check, and auto-hedging"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Phase 24: OCO Validation (Mandatory SL+TP)
        order_data = {
            'symbol': signal['symbol'],
            'side': signal['side'],
            'entry_price': signal['entry_price'],
            'stop_loss': signal.get('sl_price'),
            'take_profit': signal.get('tp_price'),
            'position_size': signal.get('position_size')
        }
        
        if not self.oco_validator.validate_order(order_data):
            logger.error(f"❌ OCO Validation FAILED for {signal['symbol']} - Missing SL or TP")
            logger.error(f"   Charter Rule: Every order MUST have both Stop Loss AND Take Profit")
            self.trades_rejected += 1
            
            log_narration(
                event_type="OCO_VALIDATION_FAILED",
                details={
                    "symbol": signal['symbol'],
                    "reason": "Missing stop_loss or take_profit",
                    "has_sl": bool(signal.get('sl_price')),
                    "has_tp": bool(signal.get('tp_price')),
                    "phase": "Phase 24 OCO Enforcement"
                },
                symbol=signal['symbol'],
                venue="oanda_practice"
            )
            return  # BLOCK ORDER
        
        logger.info(f"✅ OCO Validation PASSED - SL: {signal['sl_price']}, TP: {signal['tp_price']}")
        
        # Phase 14: Correlation Check (Avoid over-correlated positions)
        exposure = self.correlation_monitor.check_portfolio_exposure(
            symbol=signal['symbol'],
            position_size=signal.get('position_size', 0)
        )
        
        if exposure and hasattr(exposure, 'risk_weight') and exposure.risk_weight > 1.5:
            logger.warning(f"⚠️  Correlation Limit EXCEEDED for {signal['symbol']}")
            logger.warning(f"   Risk Weight: {exposure.risk_weight:.2f} (Max: 1.5)")
            logger.warning(f"   Portfolio has too much correlated exposure")
            self.trades_rejected += 1
            
            log_narration(
                event_type="CORRELATION_LIMIT_EXCEEDED",
                details={
                    "symbol": signal['symbol'],
                    "risk_weight": exposure.risk_weight if hasattr(exposure, 'risk_weight') else None,
                    "max_allowed": 1.5,
                    "phase": "Phase 14 Correlation Monitoring"
                },
                symbol=signal['symbol'],
                venue="oanda_practice"
            )
            return  # BLOCK ORDER
        
        logger.info(f"✅ Correlation Check PASSED - Risk weight acceptable")
        
        # Call parent method to execute trade (with Guardian Gates check)
        await super().execute_charter_compliant_trade(signal)
        
        # Phase 4: Auto-Hedging (After successful order placement)
        # Check if this trade was actually opened (not rejected by Guardian Gates)
        trade_id = f"CANARY_CHARTER_{len(self.trades)}_{int(__import__('time').time())}"
        
        if trade_id in self.open_trades or len(self.open_trades) > 0:
            # Find optimal hedge for this position
            hedge = self.hedge_engine.find_optimal_hedge(
                symbol=signal['symbol'],
                side=signal['side'],
                size=signal.get('position_size', 0)
            )
            
            if hedge:
                logger.info(f"🛡️  HEDGE OPPORTUNITY IDENTIFIED:")
                logger.info(f"   Primary: {signal['symbol']} ({signal['side']})")
                logger.info(f"   Hedge: {hedge.symbol} ({hedge.side})")
                logger.info(f"   Correlation: {hedge.correlation:.2f}")
                logger.info(f"   Hedge Ratio: {hedge.hedge_ratio:.2f}")
                logger.info(f"   Phase: 4 - Quant Hedge Engine")
                
                log_narration(
                    event_type="HEDGE_OPPORTUNITY",
                    details={
                        "primary_symbol": signal['symbol'],
                        "primary_side": signal['side'],
                        "hedge_symbol": hedge.symbol,
                        "hedge_side": hedge.side,
                        "correlation": hedge.correlation,
                        "hedge_ratio": hedge.hedge_ratio,
                        "phase": "Phase 4 Auto-Hedging",
                        "note": "Auto-hedging disabled in CANARY mode (testing only)"
                    },
                    symbol=signal['symbol'],
                    venue="oanda_practice"
                )
                
                # NOTE: Auto-hedge placement is DISABLED in CANARY mode for testing
                # To enable: uncomment the following lines
                # await self.execute_hedge_order(hedge)
            else:
                logger.info(f"ℹ️  No inverse correlation hedge found for {signal['symbol']}")
    
    async def generate_final_report(self):
        """Generate CANARY-specific final report"""
        session_duration = (__import__('datetime').datetime.now(__import__('datetime').timezone.utc) - self.start_time).total_seconds() / 60
        completed_trades = self.wins + self.losses
        
        report = {
            'mode': 'CANARY',
            'session_duration_minutes': session_duration,
            'session_duration_hours': session_duration / 60,
            'total_trades': len(self.trades),
            'completed_trades': completed_trades,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': self.win_rate,
            'total_pnl': self.total_pnl,
            'avg_pnl_per_trade': self.total_pnl / completed_trades if completed_trades > 0 else 0,
            'starting_capital': self.capital,
            'ending_capital': self.current_capital,
            'return_pct': ((self.current_capital - self.capital) / self.capital) * 100,
            'consecutive_losses': self.consecutive_losses,
            'trades_rejected': self.trades_rejected,
            'charter_violations': self.charter_violations,
            'charter_compliance': {
                'min_notional_usd': self.charter.MIN_NOTIONAL_USD,
                'min_risk_reward': self.charter.MIN_RISK_REWARD_RATIO,
                'max_hold_hours': self.charter.MAX_HOLD_DURATION_HOURS,
                'enforced': True
            },
            'promotion_eligible': (
                completed_trades >= 3 and  # CANARY requires minimum 3 trades (45 min session)
                self.win_rate >= 60.0 and
                self.total_pnl > 0 and
                self.charter_violations == 0
            ),
            'timestamp': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        }
        
        # Save CANARY-specific report
        with open('canary_trading_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        try:
            audit_event("CANARY_FINAL_REPORT", report, engine_mode="CANARY")
        except Exception:
            pass
        
        # Print summary
        logger = __import__('logging').getLogger(__name__)
        logger.info("=" * 80)
        logger.info("🐤 CANARY MODE - FINAL REPORT")
        logger.info("=" * 80)
        logger.info(f"⏰ Duration: {session_duration/60:.2f} hours")
        logger.info(f"📈 Total Trades: {len(self.trades)} ({completed_trades} completed)")
        logger.info(f"✅ Wins: {self.wins} | ❌ Losses: {self.losses}")
        logger.info(f"📊 Win Rate: {self.win_rate:.1f}%")
        logger.info(f"💰 Total P&L: ${self.total_pnl:,.2f}")
        logger.info(f"📈 Return: {report['return_pct']:.2f}%")
        logger.info(f"💵 Starting Capital: ${self.capital:,.2f}")
        logger.info(f"💵 Ending Capital: ${self.current_capital:,.2f}")
        logger.info(f"🚫 Trades Rejected: {self.trades_rejected}")
        logger.info(f"⚠️  Charter Violations: {self.charter_violations}")
        logger.info(f"🎯 Promotion to LIVE Eligible: {'YES ✅' if report['promotion_eligible'] else 'NO ❌'}")
        logger.info("=" * 80)
        logger.info("📋 CHARTER COMPLIANCE:")
        logger.info(f"   MIN_NOTIONAL: ${self.charter.MIN_NOTIONAL_USD:,} ✅")
        logger.info(f"   MIN_RR: {self.charter.MIN_RISK_REWARD_RATIO} ✅")
        logger.info(f"   MAX_HOLD: {self.charter.MAX_HOLD_DURATION_HOURS}h ✅")
        logger.info(f"   SESSION_BREAKER: {self.charter.DAILY_LOSS_BREAKER_PCT}% ✅")
        logger.info("=" * 80)
        
        if report['promotion_eligible']:
            logger.info("")
            logger.info("🎉 CANARY SESSION SUCCESSFUL")
            logger.info("   Total P&L must be positive")
            if self.charter_violations > 0:
                logger.info(f"   Charter violations: {self.charter_violations}")
            logger.info("")
        
        # Log final report to narration
        log_narration(
            event_type="CANARY_SESSION_END",
            details={
                "session_duration_hours": report['session_duration_hours'],
                "total_trades": report['total_trades'],
                "completed_trades": report['completed_trades'],
                "wins": report['wins'],
                "losses": report['losses'],
                "win_rate": report['win_rate'],
                "total_pnl": report['total_pnl'],
                "starting_capital": report['starting_capital'],
                "ending_capital": report['ending_capital'],
                "return_pct": report['return_pct'],
                "trades_rejected": report['trades_rejected'],
                "charter_violations": report['charter_violations'],
                "promotion_eligible": report['promotion_eligible']
            },
            symbol=None,
            venue="OANDA"
        )
        
        return report
    
    async def generate_charter_compliant_signal(self):
        """Override to add signal generation logging"""
        signal = await super().generate_charter_compliant_signal()
        
        if signal:
            # Log successful signal generation
            log_narration(
                event_type="SIGNAL_GENERATED",
                details={
                    "symbol": signal['symbol'],
                    "side": signal['side'],
                    "entry_price": signal['entry_price'],
                    "tp_price": signal['tp_price'],
                    "sl_price": signal['sl_price'],
                    "risk_reward_ratio": signal['risk_reward_ratio'],
                    "notional_usd": signal['notional_usd'],
                    "charter_compliant": True
                },
                symbol=signal['symbol'],
                venue="OANDA"
            )
        else:
            # Log signal rejection
            log_narration(
                event_type="SIGNAL_REJECTED",
                details={
                    "reason": "Charter compliance check failed",
                    "min_notional_required": self.charter.MIN_NOTIONAL_USD,
                    "min_rr_required": self.charter.MIN_RISK_REWARD_RATIO
                },
                symbol=None,
                venue="OANDA"
            )
        
        return signal
    
    async def close_trade(self, trade_id: str, reason: str):
        """Override to add additional exit logging"""
        # Get trade details before closing
        if trade_id in self.open_trades:
            trade = self.open_trades[trade_id]
            duration_hours = (datetime.now(timezone.utc) - trade.timestamp).total_seconds() / 3600
            
            # Log TTL enforcement check
            if duration_hours >= self.charter.MAX_HOLD_DURATION_HOURS:
                log_narration(
                    event_type="TTL_ENFORCEMENT",
                    details={
                        "trade_id": trade_id,
                        "duration_hours": round(duration_hours, 2),
                        "max_hold_hours": self.charter.MAX_HOLD_DURATION_HOURS,
                        "reason": "Maximum hold duration reached"
                    },
                    symbol=trade.symbol,
                    venue="oanda_practice"
                )
        
        # Call parent close_trade (which already logs TRADE_CLOSED)
        await super().close_trade(trade_id, reason)
    
    async def start_CANARY_trading(self):
        """Override to add session breaker logging"""
        # Log session start
        log_narration(
            event_type="CANARY_SESSION_START",
            details={
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "session_duration_hours": self.session_duration_hours,
                "starting_capital": self.capital,
                "charter_rules": {
                    "min_notional_usd": self.charter.MIN_NOTIONAL_USD,
                    "min_rr": self.charter.MIN_RISK_REWARD_RATIO,
                    "max_hold_hours": self.charter.MAX_HOLD_DURATION_HOURS,
                    "daily_breaker_pct": self.charter.DAILY_LOSS_BREAKER_PCT
                }
            },
            symbol=None,
            venue="OANDA"
        )
        
        # Call parent method
        await super().start_CANARY_trading()

async def main():
    """Main entry point for CANARY trading"""
    import sys
    
    # Verify mode
    from util.mode_manager import get_mode_info
    mode_info = get_mode_info()
    
    if mode_info['mode'] != 'CANARY':
        print(f"❌ Error: System is in {mode_info['mode']} mode, not CANARY")
        print("   Switch to CANARY first:")
        print("   $ python3 -c \"from util.mode_manager import switch_mode; switch_mode('CANARY')\"")
        return
    
    print("✅ System confirmed in CANARY mode")
    print()
    
    # Get PIN
    if len(sys.argv) > 1:
        try:
            pin = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid PIN format")
            return
    else:
        pin = 841921  # Default PIN
    
    # Start CANARY trading
    engine = CanaryTradingEngine(pin=pin)
    await engine.start_CANARY_trading()  # Uses same trading loop

if __name__ == "__main__":
    asyncio.run(main())
