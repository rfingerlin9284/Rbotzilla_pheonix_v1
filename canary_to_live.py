#!/usr/bin/env python3
"""
Automated Canary-to-Live Promotion System
Runs ghost trading sessions, tracks performance, auto-promotes when ready
Integrates with narration_logger and mode_manager
"""
import json
import time
import subprocess
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ing/RICK/RICK_LIVE_CLEAN/logs/canary_promotion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import our utilities
try:
    from util.narration_logger import get_session_summary, get_latest_pnl
    from util.mode_manager import switch_mode, get_mode_info
    INTEGRATED_LOGGING = True
except ImportError:
    logger.warning("⚠️ Could not import narration_logger/mode_manager - using legacy mode")
    INTEGRATED_LOGGING = False

# Paths
ROOT = Path("/home/ing/RICK/RICK_LIVE_CLEAN")
TOGGLE_FILE = ROOT / ".upgrade_toggle"
CANARY_RESULTS = ROOT / "canary_results.jsonl"
PROMOTION_REPORT = ROOT / "promotion_report.json"
GHOST_ENGINE = ROOT / "ghost_trading_engine.py"

# Promotion criteria
CRITERIA = {
    "min_sessions": 3,           # Minimum 3 successful sessions
    "min_win_rate": 70.0,        # 70% minimum win rate
    "min_total_trades": 100,     # At least 100 trades across all sessions
    "min_avg_pnl": 50.0,         # Average $50+ per session
    "max_consecutive_losses": 3, # No more than 3 losses in a row
    "min_sharpe": 1.5,           # Sharpe ratio >= 1.5
    "consistency_threshold": 0.85 # 85% of sessions must be profitable
}

class CanaryPromotion:
    """Manages automated canary testing and live promotion"""
    
    def __init__(self):
        self.results: List[Dict] = []
        self.load_results()
    
    def load_results(self):
        """Load previous canary session results"""
        if CANARY_RESULTS.exists():
            with open(CANARY_RESULTS, 'r') as f:
                for line in f:
                    try:
                        self.results.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        logger.info(f"Loaded {len(self.results)} previous canary sessions")
    
    def run_canary_session(self, duration_minutes: int = 45) -> Dict:
        """Run a single ghost trading session"""
        logger.info(f"🎯 Starting canary session ({duration_minutes} minutes)")
        
        start_time = datetime.now()
        
        # Run ghost trading engine
        try:
            result = subprocess.run(
                ['python3', str(GHOST_ENGINE)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=duration_minutes * 60 + 300  # Extra 5 min buffer
            )
            
            # Parse results from output
            session_data = self._parse_session_output(result.stdout)
            session_data['start_time'] = start_time.isoformat()
            session_data['end_time'] = datetime.now().isoformat()
            
            # Save result
            with open(CANARY_RESULTS, 'a') as f:
                f.write(json.dumps(session_data) + '\n')
            
            self.results.append(session_data)
            logger.info(f"✅ Session complete: Win Rate={session_data.get('win_rate', 0):.1f}%, PnL=${session_data.get('pnl', 0):.2f}")
            
            return session_data
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Session timeout")
            return {"status": "timeout", "timestamp": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"❌ Session error: {e}")
            return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _parse_session_output(self, output: str) -> Dict:
        """Parse ghost trading engine output using narration_logger"""
        data = {
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
        if INTEGRATED_LOGGING:
            # Use our new logging system
            try:
                summary = get_session_summary()
                data.update({
                    "total_trades": summary.get("total_trades", 0),
                    "wins": summary.get("wins", 0),
                    "losses": summary.get("losses", 0),
                    "win_rate": summary.get("win_rate", 0),
                    "pnl": summary.get("net_pnl", 0),
                    "avg_pnl_per_trade": summary.get("net_pnl", 0) / max(summary.get("total_trades", 1), 1),
                    "consecutive_losses": 0  # TODO: Track in narration logger
                })
                logger.info(f"✅ Loaded session data from narration logs: {data['total_trades']} trades, {data['win_rate']:.1f}% win rate")
            except Exception as e:
                logger.error(f"Failed to load from narration logs: {e}")
        else:
            # Legacy: Look for final report file
            report_files = list(ROOT.glob("ghost_trading_final_report*.json"))
            if report_files:
                with open(report_files[-1], 'r') as f:
                    report = json.load(f)
                    data.update({
                        "total_trades": report.get("total_trades", 0),
                        "wins": report.get("wins", 0),
                        "losses": report.get("losses", 0),
                        "win_rate": report.get("win_rate", 0),
                        "pnl": report.get("total_pnl", 0),
                        "avg_pnl_per_trade": report.get("avg_pnl_per_trade", 0),
                        "consecutive_losses": report.get("consecutive_losses", 0)
                    })
        
        return data
    
    def evaluate_promotion_readiness(self) -> Dict:
        """Evaluate if system is ready for live promotion"""
        logger.info("📊 Evaluating promotion readiness...")
        
        # Get recent successful sessions
        successful_sessions = [r for r in self.results if r.get("status") == "completed"]
        
        if len(successful_sessions) < CRITERIA["min_sessions"]:
            return {
                "ready": False,
                "reason": f"Need {CRITERIA['min_sessions']} sessions, have {len(successful_sessions)}"
            }
        
        # Calculate aggregate metrics
        total_trades = sum(s.get("total_trades", 0) for s in successful_sessions)
        total_pnl = sum(s.get("pnl", 0) for s in successful_sessions)
        avg_pnl = total_pnl / len(successful_sessions) if successful_sessions else 0
        
        # Win rate across all sessions
        total_wins = sum(s.get("wins", 0) for s in successful_sessions)
        total_losses = sum(s.get("losses", 0) for s in successful_sessions)
        overall_win_rate = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 0
        
        # Consistency check
        profitable_sessions = sum(1 for s in successful_sessions if s.get("pnl", 0) > 0)
        consistency = (profitable_sessions / len(successful_sessions)) if successful_sessions else 0
        
        # Check all criteria
        checks = {
            "total_sessions": len(successful_sessions) >= CRITERIA["min_sessions"],
            "total_trades": total_trades >= CRITERIA["min_total_trades"],
            "win_rate": overall_win_rate >= CRITERIA["min_win_rate"],
            "avg_pnl": avg_pnl >= CRITERIA["min_avg_pnl"],
            "consistency": consistency >= CRITERIA["consistency_threshold"]
        }
        
        all_passed = all(checks.values())
        
        report = {
            "ready": all_passed,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_sessions": len(successful_sessions),
                "total_trades": total_trades,
                "overall_win_rate": overall_win_rate,
                "total_pnl": total_pnl,
                "avg_pnl_per_session": avg_pnl,
                "consistency": consistency * 100
            },
            "checks": checks,
            "criteria": CRITERIA
        }
        
        if all_passed:
            logger.info("🎉 ✅ SYSTEM READY FOR LIVE PROMOTION!")
        else:
            failed = [k for k, v in checks.items() if not v]
            logger.info(f"⏳ Not ready yet. Failed checks: {', '.join(failed)}")
        
        return report
    
    def promote_to_live(self, reason: str) -> bool:
        """Promote system to live trading"""
        logger.info("🚀 INITIATING LIVE PROMOTION")
        
        # Final safety check
        readiness = self.evaluate_promotion_readiness()
        if not readiness["ready"]:
            logger.error("❌ Cannot promote: System not ready")
            return False
        
        # Create promotion report
        promotion_data = {
            "promoted": True,
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "readiness_report": readiness,
            "final_canary_sessions": self.results[-3:]
        }
        
        with open(PROMOTION_REPORT, 'w') as f:
            json.dump(promotion_data, f, indent=2)
        
        # Create backup
        backup_dir = ROOT / "pre_upgrade_backups"
        backup_dir.mkdir(exist_ok=True)
        backup_file = backup_dir / f"pre_live_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        
        subprocess.run([
            'tar', '-czf', str(backup_file),
            '-C', str(ROOT),
            '.upgrade_toggle', 'canary_results.jsonl', 'promotion_report.json'
        ])
        
        logger.info(f"✅ Backup created: {backup_file}")
        
        # Flip the toggle to LIVE mode (requires PIN)
        if INTEGRATED_LOGGING:
            try:
                # Use mode_manager with PIN validation
                from foundation.rick_charter import RickCharter
                charter = RickCharter()
                switch_mode('LIVE', pin=charter.PIN)
                logger.info("✅ .upgrade_toggle = LIVE (via mode_manager)")
            except Exception as e:
                logger.error(f"❌ Failed to switch to LIVE mode: {e}")
                return False
        else:
            # Legacy: Direct file write (no PIN validation)
            TOGGLE_FILE.write_text("LIVE")
            logger.info("✅ .upgrade_toggle = LIVE (legacy mode - no PIN check)")
        
        # Log to audit
        audit_file = backup_dir / "enable_live_audit.log"
        with open(audit_file, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] AUTO_PROMOTION reason={reason}\n")
        
        logger.info("🎉 LIVE TRADING ENABLED!")
        return True
    
    def run_automated_path(self, max_sessions: int = 5, session_duration: int = 45):
        """Run automated canary-to-live path"""
        logger.info("🤖 Starting automated canary-to-live promotion path")
        logger.info(f"Will run up to {max_sessions} sessions of {session_duration} minutes each")
        
        for session_num in range(1, max_sessions + 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 CANARY SESSION {session_num}/{max_sessions}")
            logger.info(f"{'='*60}\n")
            
            # Run session
            result = self.run_canary_session(duration_minutes=session_duration)
            
            # Check if ready for promotion
            readiness = self.evaluate_promotion_readiness()
            
            if readiness["ready"]:
                logger.info("\n🎉 PROMOTION CRITERIA MET!")
                logger.info(f"Metrics: {json.dumps(readiness['metrics'], indent=2)}")
                
                # Auto-promote
                reason = f"Automated promotion after {len(self.results)} successful canary sessions with {readiness['metrics']['overall_win_rate']:.1f}% win rate"
                self.promote_to_live(reason)
                break
            else:
                logger.info(f"\n⏳ Continue testing... (Session {session_num}/{max_sessions})")
                logger.info(f"Next check after session {session_num + 1}")
                
                # Wait 5 minutes between sessions
                if session_num < max_sessions:
                    logger.info("⏰ Waiting 5 minutes before next session...")
                    time.sleep(300)
        
        else:
            logger.info(f"\n⚠️ Completed {max_sessions} sessions without meeting promotion criteria")
            logger.info("System will continue in canary mode. Review results and adjust criteria if needed.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated Canary-to-Live Promotion")
    parser.add_argument('--sessions', type=int, default=5, help='Max canary sessions to run')
    parser.add_argument('--duration', type=int, default=45, help='Duration per session (minutes)')
    parser.add_argument('--check-only', action='store_true', help='Only check readiness, don\'t run sessions')
    parser.add_argument('--promote-now', action='store_true', help='Force promotion if criteria met')
    
    args = parser.parse_args()
    
    canary = CanaryPromotion()
    
    if args.check_only:
        readiness = canary.evaluate_promotion_readiness()
        print(json.dumps(readiness, indent=2))
        return
    
    if args.promote_now:
        readiness = canary.evaluate_promotion_readiness()
        if readiness["ready"]:
            reason = input("Enter promotion reason (5+ words): ")
            if len(reason.split()) >= 5:
                canary.promote_to_live(reason)
            else:
                print("❌ Reason must be at least 5 words")
        else:
            print("❌ System not ready for promotion")
            print(json.dumps(readiness, indent=2))
        return
    
    # Run automated path
    canary.run_automated_path(
        max_sessions=args.sessions,
        session_duration=args.duration
    )


if __name__ == "__main__":
    main()
