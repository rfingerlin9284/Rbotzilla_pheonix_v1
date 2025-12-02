#!/usr/bin/env python3
"""
Rick Trading Process Narrator - Real-Time Scanning & Filtering Commentary
Provides step-by-step narration of Rick's decision-making process
PIN: 841921
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from util.rick_narrator import rick_narrate

logger = logging.getLogger(__name__)

class RickProcessNarrator:
    """
    Real-time narration of Rick's trading process:
    - Market scanning
    - Pattern detection
    - Signal generation
    - Filter validation
    - Trade decision
    """
    
    def __init__(self):
        self.current_scan_id = None
        self.scan_start_time = None
    
    def narrate_scan_start(self, pairs: List[str]) -> None:
        """Narrate the beginning of a market scan"""
        self.scan_start_time = datetime.now(timezone.utc)
        
        details = {
            "pairs": pairs,
            "pair_count": len(pairs),
            "scan_type": "opportunity_hunt"
        }
        
        rick_narrate("SCAN_START", details, venue="scanner")
        logger.info(f"📡 Rick scanning {len(pairs)} pairs for opportunities...")
    
    def narrate_pair_check(self, pair: str, price: float, spread_pips: float) -> None:
        """Narrate checking individual pair"""
        details = {
            "pair": pair,
            "price": price,
            "spread_pips": spread_pips,
            "spread_status": "tight" if spread_pips < 2.0 else "wide"
        }
        
        rick_narrate("PAIR_CHECK", details, symbol=pair, venue="scanner")
    
    def narrate_pattern_detection(self, pair: str, patterns_found: List[str], 
                                  confidence: float) -> None:
        """Narrate pattern detection results"""
        details = {
            "pair": pair,
            "patterns": patterns_found,
            "pattern_count": len(patterns_found),
            "confidence": confidence,
            "status": "promising" if confidence > 0.70 else "weak"
        }
        
        rick_narrate("PATTERN_DETECTION", details, symbol=pair, venue="analyzer")
    
    def narrate_ml_analysis(self, pair: str, ml_signal: Dict[str, Any]) -> None:
        """Narrate ML model analysis"""
        details = {
            "pair": pair,
            "direction": ml_signal.get('direction', 'NEUTRAL'),
            "confidence": ml_signal.get('confidence', 0.0),
            "regime": ml_signal.get('regime', 'unknown'),
            "model_type": ml_signal.get('model_type', 'A'),
            "recommendation": "strong" if ml_signal.get('confidence', 0) > 0.75 else "moderate"
        }
        
        rick_narrate("ML_ANALYSIS", details, symbol=pair, venue="ml_brain")
    
    def narrate_filter_check(self, pair: str, filter_name: str, 
                            passed: bool, score: float, reason: str) -> None:
        """Narrate individual filter check"""
        details = {
            "pair": pair,
            "filter_name": filter_name,
            "passed": passed,
            "score": score,
            "reason": reason,
            "status": "✅ PASS" if passed else "❌ FAIL"
        }
        
        rick_narrate("FILTER_CHECK", details, symbol=pair, venue="smart_logic")
    
    def narrate_rr_calculation(self, pair: str, entry: float, stop: float, 
                               target: float, rr_ratio: float) -> None:
        """Narrate risk/reward calculation"""
        charter_min = 3.2
        passes_charter = rr_ratio >= charter_min
        
        details = {
            "pair": pair,
            "entry_price": entry,
            "stop_loss": stop,
            "take_profit": target,
            "rr_ratio": rr_ratio,
            "charter_min": charter_min,
            "passes_charter": passes_charter,
            "quality": "excellent" if rr_ratio > 4.0 else "good" if rr_ratio > 3.5 else "acceptable"
        }
        
        rick_narrate("RR_CALCULATION", details, symbol=pair, venue="risk_calculator")
    
    def narrate_confluence_check(self, pair: str, confluence_score: float, 
                                 passing_filters: List[str]) -> None:
        """Narrate confluence analysis"""
        details = {
            "pair": pair,
            "confluence_score": confluence_score,
            "passing_filters": passing_filters,
            "filter_count": len(passing_filters),
            "min_required": 0.65,
            "passes": confluence_score >= 0.65,
            "strength": "strong" if confluence_score > 0.80 else "moderate"
        }
        
        rick_narrate("CONFLUENCE_CHECK", details, symbol=pair, venue="smart_logic")
    
    def narrate_position_sizing(self, pair: str, capital: float, risk_pct: float,
                                position_size: float, notional: float) -> None:
        """Narrate position size calculation"""
        details = {
            "pair": pair,
            "account_balance": capital,
            "risk_percentage": risk_pct,
            "position_size": position_size,
            "notional_value": notional,
            "min_notional": 15000,
            "meets_charter": notional >= 15000
        }
        
        rick_narrate("POSITION_SIZING", details, symbol=pair, venue="risk_manager")
    
    def narrate_correlation_check(self, pair: str, existing_positions: List[str],
                                  correlation_level: float) -> None:
        """Narrate correlation check against open positions"""
        details = {
            "pair": pair,
            "existing_positions": existing_positions,
            "correlation_level": correlation_level,
            "max_allowed": 0.60,
            "passes": correlation_level < 0.60,
            "risk": "high" if correlation_level > 0.70 else "moderate" if correlation_level > 0.50 else "low"
        }
        
        rick_narrate("CORRELATION_CHECK", details, symbol=pair, venue="risk_manager")
    
    def narrate_final_decision(self, pair: str, decision: str, reason: str,
                              total_score: float, filters_passed: int) -> None:
        """Narrate final trade decision"""
        details = {
            "pair": pair,
            "decision": decision,
            "reason": reason,
            "total_score": total_score,
            "filters_passed": filters_passed,
            "action": "EXECUTE" if decision == "TRADE" else "SKIP"
        }
        
        rick_narrate("TRADE_DECISION", details, symbol=pair, venue="decision_engine")
    
    def narrate_trade_execution(self, pair: str, direction: str, entry: float,
                               stop: float, target: float, position_size: float) -> None:
        """Narrate trade execution"""
        details = {
            "pair": pair,
            "direction": direction,
            "entry_price": entry,
            "stop_loss": stop,
            "take_profit": target,
            "position_size": position_size,
            "status": "EXECUTING"
        }
        
        rick_narrate("TRADE_EXECUTION", details, symbol=pair, venue="oanda")
    
    def narrate_trade_rejected(self, pair: str, rejection_reason: str,
                              failed_filters: List[str]) -> None:
        """Narrate trade rejection"""
        details = {
            "pair": pair,
            "rejection_reason": rejection_reason,
            "failed_filters": failed_filters,
            "status": "REJECTED"
        }
        
        rick_narrate("TRADE_REJECTED", details, symbol=pair, venue="decision_engine")
    
    def narrate_scan_complete(self, pairs_scanned: int, opportunities_found: int,
                             trades_executed: int, scan_duration_ms: float) -> None:
        """Narrate scan completion summary"""
        details = {
            "pairs_scanned": pairs_scanned,
            "opportunities_found": opportunities_found,
            "trades_executed": trades_executed,
            "scan_duration_ms": scan_duration_ms,
            "efficiency": f"{trades_executed}/{opportunities_found}" if opportunities_found > 0 else "0/0"
        }
        
        rick_narrate("SCAN_COMPLETE", details, venue="scanner")


# Global narrator instance
_process_narrator = None

def get_process_narrator() -> RickProcessNarrator:
    """Get global process narrator instance"""
    global _process_narrator
    if _process_narrator is None:
        _process_narrator = RickProcessNarrator()
    return _process_narrator


# Convenience functions for easy integration

def narrate_scan_start(pairs: List[str]) -> None:
    """Narrate scan start"""
    get_process_narrator().narrate_scan_start(pairs)

def narrate_pair_check(pair: str, price: float, spread_pips: float) -> None:
    """Narrate pair check"""
    get_process_narrator().narrate_pair_check(pair, price, spread_pips)

def narrate_pattern_detection(pair: str, patterns: List[str], confidence: float) -> None:
    """Narrate pattern detection"""
    get_process_narrator().narrate_pattern_detection(pair, patterns, confidence)

def narrate_ml_analysis(pair: str, ml_signal: Dict[str, Any]) -> None:
    """Narrate ML analysis"""
    get_process_narrator().narrate_ml_analysis(pair, ml_signal)

def narrate_filter_check(pair: str, filter_name: str, passed: bool, 
                        score: float, reason: str) -> None:
    """Narrate filter check"""
    get_process_narrator().narrate_filter_check(pair, filter_name, passed, score, reason)

def narrate_rr_calculation(pair: str, entry: float, stop: float, 
                          target: float, rr_ratio: float) -> None:
    """Narrate RR calculation"""
    get_process_narrator().narrate_rr_calculation(pair, entry, stop, target, rr_ratio)

def narrate_confluence_check(pair: str, confluence_score: float, 
                            passing_filters: List[str]) -> None:
    """Narrate confluence check"""
    get_process_narrator().narrate_confluence_check(pair, confluence_score, passing_filters)

def narrate_position_sizing(pair: str, capital: float, risk_pct: float,
                           position_size: float, notional: float) -> None:
    """Narrate position sizing"""
    get_process_narrator().narrate_position_sizing(pair, capital, risk_pct, 
                                                   position_size, notional)

def narrate_correlation_check(pair: str, existing_positions: List[str],
                             correlation_level: float) -> None:
    """Narrate correlation check"""
    get_process_narrator().narrate_correlation_check(pair, existing_positions, 
                                                     correlation_level)

def narrate_final_decision(pair: str, decision: str, reason: str,
                          total_score: float, filters_passed: int) -> None:
    """Narrate final decision"""
    get_process_narrator().narrate_final_decision(pair, decision, reason, 
                                                  total_score, filters_passed)

def narrate_trade_execution(pair: str, direction: str, entry: float,
                           stop: float, target: float, position_size: float) -> None:
    """Narrate trade execution"""
    get_process_narrator().narrate_trade_execution(pair, direction, entry, 
                                                   stop, target, position_size)

def narrate_trade_rejected(pair: str, rejection_reason: str,
                          failed_filters: List[str]) -> None:
    """Narrate trade rejection"""
    get_process_narrator().narrate_trade_rejected(pair, rejection_reason, failed_filters)

def narrate_scan_complete(pairs_scanned: int, opportunities_found: int,
                         trades_executed: int, scan_duration_ms: float) -> None:
    """Narrate scan complete"""
    get_process_narrator().narrate_scan_complete(pairs_scanned, opportunities_found,
                                                 trades_executed, scan_duration_ms)


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("\n=== Testing Rick Process Narrator ===\n")
    
    # Simulate a complete scan cycle
    pairs = ["EUR_USD", "GBP_USD", "USD_JPY"]
    
    # Start scan
    narrate_scan_start(pairs)
    
    # Check EUR/USD
    narrate_pair_check("EUR_USD", 1.1604, 1.2)
    narrate_pattern_detection("EUR_USD", ["ascending_triangle", "bullish_divergence"], 0.78)
    
    ml_signal = {
        "direction": "BUY",
        "confidence": 0.82,
        "regime": "bull",
        "model_type": "A"
    }
    narrate_ml_analysis("EUR_USD", ml_signal)
    
    # Filter checks
    narrate_rr_calculation("EUR_USD", 1.1604, 1.1580, 1.1680, 3.2)
    narrate_filter_check("EUR_USD", "risk_reward", True, 0.85, "RR 3.2:1 meets charter")
    narrate_filter_check("EUR_USD", "fvg_confluence", True, 0.78, "FVG aligned with direction")
    narrate_filter_check("EUR_USD", "fibonacci", True, 0.72, "Entry at 0.618 fib level")
    
    # Confluence
    narrate_confluence_check("EUR_USD", 0.82, ["risk_reward", "fvg", "fibonacci"])
    
    # Position sizing
    narrate_position_sizing("EUR_USD", 2271.38, 2.0, 5000, 15800)
    
    # Correlation
    narrate_correlation_check("EUR_USD", [], 0.0)
    
    # Final decision
    narrate_final_decision("EUR_USD", "TRADE", "All filters passed with 82% confluence", 0.82, 4)
    
    # Execution
    narrate_trade_execution("EUR_USD", "BUY", 1.1604, 1.1580, 1.1680, 5000)
    
    # Complete scan
    narrate_scan_complete(3, 1, 1, 2847.5)
    
    print("\n✅ Process narration test complete!")
