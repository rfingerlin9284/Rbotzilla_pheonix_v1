#!/usr/bin/env python3
"""
CRYPTO ENTRY GATE SYSTEM - ALL 4 IMPROVEMENTS IMPLEMENTED
Combines: Hive consensus 90%, Time windows, Volatility sizing, Confluence gates
PIN: 841921 | Date: 2025-10-19
"""

import logging
from datetime import datetime
import pytz
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from foundation.rick_charter import RickCharter

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class GateResult(Enum):
    """Gate evaluation results"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass
class CryptoEntryGateResult:
    """Result of full crypto entry gate validation"""
    overall_result: str  # APPROVED or REJECTED
    hive_consensus_gate: Dict
    time_window_gate: Dict
    volatility_gate: Dict
    confluence_gates: Dict
    final_position_size: float
    rejection_reasons: List[str]
    approvals: List[str]
    timestamp: str


class CryptoEntryGateSystem:
    """
    Unified entry gate system for crypto trading
    Implements all 4 improvements simultaneously:
    1. 90% AI Hive consensus (vs 80% forex)
    2. 8 AM - 4 PM ET time windows
    3. Volatility-adjusted position sizing
    4. 4/5 confluence gate scoring
    """
    
    def __init__(self, pin: int = 841921):
        """Initialize gate system with Charter validation"""
        if pin != 841921:
            raise ValueError("Invalid PIN - Charter enforcement required")
        
        self.charter = RickCharter
        self.logger = logger
        try:
            self.et_tz = pytz.timezone('America/New_York')
        except:
            self.et_tz = pytz.timezone('Eastern')
        self.rejection_log = []
        self.approval_log = []
    
    # =========================================================================
    # GATE #1: CRYPTO-SPECIFIC AI HIVE VOTING (90% CONSENSUS)
    # =========================================================================
    
    def evaluate_hive_consensus_gate(self, symbol: str, hive_consensus: float) -> Dict:
        """
        Gate #1: Require higher consensus for crypto
        - Crypto (BTC/ETH): 90% required
        - Forex: 80% required
        """
        result = {
            "gate_name": "HIVE_CONSENSUS",
            "symbol": symbol,
            "consensus_percentage": hive_consensus * 100,
            "status": GateResult.APPROVED.value
        }
        
        # Determine threshold based on asset type
        if symbol in self.charter.CRYPTO_HIVE_CONSENSUS_APPLIES_TO:
            threshold = self.charter.CRYPTO_AI_HIVE_VOTE_CONSENSUS
            asset_type = "CRYPTO"
        else:
            threshold = self.charter.FOREX_AI_HIVE_VOTE_CONSENSUS
            asset_type = "FOREX"
        
        result["threshold"] = threshold * 100
        result["asset_type"] = asset_type
        
        # Check consensus
        if hive_consensus >= threshold:
            result["status"] = GateResult.APPROVED.value
            result["message"] = f"{asset_type} consensus {hive_consensus:.0%} >= {threshold:.0%} ✓"
            self.approval_log.append(result["message"])
        else:
            result["status"] = GateResult.REJECTED.value
            result["message"] = f"{asset_type} consensus {hive_consensus:.0%} < {threshold:.0%} REJECTED"
            self.rejection_log.append(f"GATE_1_HIVE: {result['message']}")
        
        return result
    
    # =========================================================================
    # GATE #2: TIME-BASED TRADING WINDOWS (8 AM - 4 PM ET, MON-FRI)
    # =========================================================================
    
    def evaluate_time_window_gate(self, symbol: str) -> Dict:
        """
        Gate #2: Only trade during peak liquidity hours
        - Hours: 8 AM - 4 PM ET (0800-1600 ET)
        - Days: Mon-Fri only
        - Applies to: Crypto pairs only (BTC/USD, ETH/USD, BTC-PERP, ETH-PERP)
        """
        result = {
            "gate_name": "TIME_WINDOW",
            "symbol": symbol,
            "status": GateResult.APPROVED.value
        }
        
        # Check if applies to crypto
        if symbol not in self.charter.CRYPTO_HIVE_CONSENSUS_APPLIES_TO:
            result["message"] = f"Time window gate NOT REQUIRED for {symbol} (forex pair)"
            result["status"] = GateResult.APPROVED.value
            return result
        
        # Get current time in ET
        now_et = datetime.now(self.et_tz)
        day_name = now_et.strftime("%A").upper()
        hour = now_et.hour
        
        result["current_time_et"] = now_et.strftime("%Y-%m-%d %H:%M:%S %Z")
        result["current_day"] = day_name
        result["current_hour"] = hour
        
        # Check day
        if day_name not in self.charter.CRYPTO_TRADE_WINDOW_DAYS:
            result["status"] = GateResult.REJECTED.value
            result["message"] = f"Outside trading days - {day_name} not in {self.charter.CRYPTO_TRADE_WINDOW_DAYS}"
            self.rejection_log.append(f"GATE_2_TIME_WINDOW_DAY: {result['message']}")
            return result
        
        # Check hour
        if hour < self.charter.CRYPTO_TRADE_WINDOW_START_HOUR_ET:
            result["status"] = GateResult.REJECTED.value
            result["message"] = f"Before trading window: {hour}:00 < {self.charter.CRYPTO_TRADE_WINDOW_START_HOUR_ET}:00 ET"
            self.rejection_log.append(f"GATE_2_TIME_WINDOW_HOUR_BEFORE: {result['message']}")
            return result
        
        if hour >= self.charter.CRYPTO_TRADE_WINDOW_END_HOUR_ET:
            result["status"] = GateResult.REJECTED.value
            result["message"] = f"After trading window: {hour}:00 >= {self.charter.CRYPTO_TRADE_WINDOW_END_HOUR_ET}:00 ET"
            self.rejection_log.append(f"GATE_2_TIME_WINDOW_HOUR_AFTER: {result['message']}")
            return result
        
        # Approved
        result["status"] = GateResult.APPROVED.value
        result["message"] = f"Within trading window: {day_name} {hour:02d}:00 ET ✓"
        self.approval_log.append(result["message"])
        
        return result
    
    # =========================================================================
    # GATE #3: VOLATILITY-ADJUSTED POSITION SIZING
    # =========================================================================
    
    def calculate_atr_volatility_tier(self, current_atr: float, normal_atr: float = 1.0) -> Dict:
        """
        Calculate volatility tier based on ATR ratio
        Returns scaling factor for position size
        """
        atr_ratio = current_atr / normal_atr if normal_atr > 0 else 1.0
        
        if atr_ratio > self.charter.VOLATILITY_HIGH_ATR_THRESHOLD:
            tier = "HIGH"
            scale = self.charter.VOLATILITY_HIGH_POSITION_SCALE
            description = f"High volatility: {atr_ratio:.2f}x > {self.charter.VOLATILITY_HIGH_ATR_THRESHOLD}x"
        elif atr_ratio < self.charter.VOLATILITY_LOW_ATR_THRESHOLD:
            tier = "LOW"
            scale = self.charter.VOLATILITY_LOW_POSITION_SCALE
            description = f"Low volatility: {atr_ratio:.2f}x < {self.charter.VOLATILITY_LOW_ATR_THRESHOLD}x"
        else:
            tier = "NORMAL"
            scale = self.charter.VOLATILITY_NORMAL_POSITION_SCALE
            description = f"Normal volatility: {atr_ratio:.2f}x in {self.charter.VOLATILITY_NORMAL_ATR_MIN}-{self.charter.VOLATILITY_NORMAL_ATR_MAX}x"
        
        return {
            "tier": tier,
            "atr_ratio": atr_ratio,
            "scale_factor": scale,
            "description": description
        }
    
    def evaluate_volatility_gate(self, symbol: str, current_atr: float, normal_atr: float = 1.0) -> Dict:
        """
        Gate #3: Scale position size to current volatility
        - High volatility (ATR > 2.0x): 50% position
        - Normal volatility (1.0-1.5x): 100% position
        - Low volatility (ATR < 1.0x): 150% position
        """
        result = {
            "gate_name": "VOLATILITY_SIZING",
            "symbol": symbol,
            "status": GateResult.APPROVED.value
        }
        
        volatility_info = self.calculate_atr_volatility_tier(current_atr, normal_atr)
        result.update(volatility_info)
        result["message"] = volatility_info["description"]
        
        self.approval_log.append(f"Volatility tier {volatility_info['tier']}: {result['message']}")
        
        return result
    
    # =========================================================================
    # GATE #4: CONFLUENCE GATES (4/5 SIGNALS REQUIRED)
    # =========================================================================
    
    def score_confluence_gates(self, symbol: str, signal_data: Dict) -> Dict:
        """
        Gate #4: Score entry on 5 technical signals
        Requires 4/5 gates to pass
        
        Gate signals:
        1. RSI: 30-70 (healthy, not overbought/oversold)
        2. MA: Price above/below key moving average
        3. Volume: > 1.5x average volume
        4. Hive: >= 90% consensus
        5. Trend: 4-hour trend aligned with 15-min entry
        """
        result = {
            "gate_name": "CONFLUENCE_GATES",
            "symbol": symbol,
            "total_gates": 5,
            "gates_required": self.charter.CRYPTO_CONFLUENCE_SCORE_REQUIRED,
            "gates_passed": 0,
            "status": GateResult.APPROVED.value,
            "gate_details": {}
        }
        
        score = 0
        
        # Gate 1: RSI in healthy range
        if self.charter.CRYPTO_CONFLUENCE_GATE_1_RSI:
            rsi = signal_data.get('rsi', 50)
            if 30 <= rsi <= 70:
                score += 1
                result["gate_details"]["RSI"] = {"passed": True, "value": rsi, "range": "30-70"}
            else:
                result["gate_details"]["RSI"] = {"passed": False, "value": rsi, "range": "30-70", "reason": "overbought/oversold"}
        
        # Gate 2: Price aligned with MA
        if self.charter.CRYPTO_CONFLUENCE_GATE_2_MA:
            price = signal_data.get('price', 0)
            ma_20 = signal_data.get('ma_20', 0)
            ma_50 = signal_data.get('ma_50', 0)
            direction = signal_data.get('direction', 'UP')
            
            aligned = False
            if direction == 'UP' and price > ma_20 > ma_50:
                aligned = True
            elif direction == 'DOWN' and price < ma_20 < ma_50:
                aligned = True
            
            if aligned:
                score += 1
                result["gate_details"]["MA"] = {"passed": True, "direction": direction, "price_ma_alignment": "confirmed"}
            else:
                result["gate_details"]["MA"] = {"passed": False, "direction": direction, "price_ma_alignment": "weak"}
        
        # Gate 3: Volume spike
        if self.charter.CRYPTO_CONFLUENCE_GATE_3_VOLUME:
            volume = signal_data.get('volume', 0)
            avg_volume = signal_data.get('avg_volume_20', 1)
            volume_ratio = volume / avg_volume if avg_volume > 0 else 0
            
            if volume_ratio > 1.5:
                score += 1
                result["gate_details"]["VOLUME"] = {"passed": True, "ratio": f"{volume_ratio:.2f}x", "threshold": "1.5x"}
            else:
                result["gate_details"]["VOLUME"] = {"passed": False, "ratio": f"{volume_ratio:.2f}x", "threshold": "1.5x"}
        
        # Gate 4: Hive consensus
        if self.charter.CRYPTO_CONFLUENCE_GATE_4_HIVE:
            hive_consensus = signal_data.get('hive_consensus', 0)
            if hive_consensus >= self.charter.CRYPTO_AI_HIVE_VOTE_CONSENSUS:
                score += 1
                result["gate_details"]["HIVE"] = {"passed": True, "consensus": f"{hive_consensus:.0%}", "threshold": f"{self.charter.CRYPTO_AI_HIVE_VOTE_CONSENSUS:.0%}"}
            else:
                result["gate_details"]["HIVE"] = {"passed": False, "consensus": f"{hive_consensus:.0%}", "threshold": f"{self.charter.CRYPTO_AI_HIVE_VOTE_CONSENSUS:.0%}"}
        
        # Gate 5: 4-hour trend aligned
        if self.charter.CRYPTO_CONFLUENCE_GATE_5_TREND:
            trend_4h = signal_data.get('trend_4h', 'NEUTRAL')
            trend_15m = signal_data.get('trend_15m', 'NEUTRAL')
            
            if trend_4h == trend_15m and trend_4h != 'NEUTRAL':
                score += 1
                result["gate_details"]["TREND"] = {"passed": True, "4h": trend_4h, "15m": trend_15m, "aligned": True}
            else:
                result["gate_details"]["TREND"] = {"passed": False, "4h": trend_4h, "15m": trend_15m, "aligned": False}
        
        result["gates_passed"] = score
        
        # Determine if approved
        if score >= result["gates_required"]:
            result["status"] = GateResult.APPROVED.value
            result["message"] = f"Confluence gates {score}/{result['total_gates']} passed ✓"
            self.approval_log.append(result["message"])
        else:
            result["status"] = GateResult.REJECTED.value
            result["message"] = f"Confluence gates {score}/{result['total_gates']} < {result['gates_required']} required - REJECTED"
            self.rejection_log.append(f"GATE_4_CONFLUENCE: {result['message']}")
        
        return result
    
    # =========================================================================
    # UNIFIED ENTRY VALIDATION
    # =========================================================================
    
    def validate_crypto_entry(
        self,
        symbol: str,
        hive_consensus: float,
        base_position_size: float,
        current_atr: float,
        normal_atr: float = 1.0,
        signal_data: Optional[Dict] = None
    ) -> CryptoEntryGateResult:
        """
        Execute all 4 gates simultaneously
        Returns detailed result with approval/rejection reasons
        """
        self.rejection_log = []
        self.approval_log = []
        
        timestamp = datetime.now(self.et_tz).isoformat()
        
        # Evaluate all 4 gates
        gate_1 = self.evaluate_hive_consensus_gate(symbol, hive_consensus)
        gate_2 = self.evaluate_time_window_gate(symbol)
        gate_3 = self.evaluate_volatility_gate(symbol, current_atr, normal_atr)
        gate_4 = self.score_confluence_gates(symbol, signal_data or {})
        
        # Calculate final position size (apply volatility scaling)
        final_position_size = base_position_size * gate_3["scale_factor"]
        
        # Determine overall result (ALL gates must pass for approval)
        gates_status = [gate_1["status"], gate_2["status"], gate_3["status"], gate_4["status"]]
        
        # Non-crypto pairs bypass time window requirement
        if symbol not in self.charter.CRYPTO_HIVE_CONSENSUS_APPLIES_TO:
            # For forex: check hive (80%) and confluence only
            gates_status = [gate_1["status"], gate_4["status"]]
        
        all_gates_passed = all(status == GateResult.APPROVED.value for status in gates_status)
        overall_result = GateResult.APPROVED.value if all_gates_passed else GateResult.REJECTED.value
        
        # Create result object
        result = CryptoEntryGateResult(
            overall_result=overall_result,
            hive_consensus_gate=gate_1,
            time_window_gate=gate_2,
            volatility_gate=gate_3,
            confluence_gates=gate_4,
            final_position_size=final_position_size,
            rejection_reasons=self.rejection_log,
            approvals=self.approval_log,
            timestamp=timestamp
        )
        
        # Log result
        self._log_entry_result(result, symbol)
        
        return result
    
    def _log_entry_result(self, result: CryptoEntryGateResult, symbol: str):
        """Log entry validation result"""
        sep = "=" * 80
        
        if result.overall_result == GateResult.APPROVED.value:
            self.logger.info(f"\n{sep}")
            self.logger.info(f"✅ CRYPTO ENTRY APPROVED - {symbol}")
            self.logger.info(f"{sep}")
            for approval in result.approvals:
                self.logger.info(f"  ✓ {approval}")
            self.logger.info(f"\nFinal Position Size: {result.final_position_size:.2f} (scaled {result.volatility_gate['scale_factor']}x)")
            self.logger.info(f"Volatility Tier: {result.volatility_gate['tier']}")
            self.logger.info(f"\n{sep}\n")
        else:
            self.logger.warning(f"\n{sep}")
            self.logger.warning(f"❌ CRYPTO ENTRY REJECTED - {symbol}")
            self.logger.warning(f"{sep}")
            for rejection in result.rejection_reasons:
                self.logger.warning(f"  ✗ {rejection}")
            self.logger.warning(f"\n{sep}\n")
    
    def validate_broker_connectivity(self) -> Dict:
        """
        Validate broker connectivity using immutable Charter config
        Returns: {'status': 'VALID'|'INVALID', 'oanda': bool, 'ibkr': bool, 'details': str}
        """
        result = {
            "status": "VALID",
            "oanda_connected": False,
            "ibkr_connected": False,
            "details": []
        }
        
        # Check OANDA (immutable from Charter)
        if self.charter.OANDA_ENABLED:
            try:
                from brokers.oanda_connector import OandaConnector
                oanda = OandaConnector()
                result["oanda_connected"] = True
                result["details"].append(f"✓ OANDA: {self.charter.OANDA_ENVIRONMENT_CANARY} account ready")
            except Exception as e:
                result["oanda_connected"] = False
                result["details"].append(f"✗ OANDA: Connection failed - {str(e)}")
                result["status"] = "INVALID"
        
        # Check IBKR Gateway (immutable from Charter)
        if self.charter.IBKR_GATEWAY_ENABLED:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                timeout = self.charter.BROKER_VALIDATION_TIMEOUT_SECONDS
                sock.settimeout(timeout)
                host = self.charter.IBKR_GATEWAY_HOST
                port = self.charter.IBKR_GATEWAY_PORT
                result_code = sock.connect_ex((host, port))
                sock.close()
                
                if result_code == 0:
                    result["ibkr_connected"] = True
                    result["details"].append(f"✓ IBKR: Gateway {host}:{port} ready (paper)")
                else:
                    result["ibkr_connected"] = False
                    result["details"].append(f"✗ IBKR: Gateway {host}:{port} unreachable")
                    result["status"] = "INVALID"
            except Exception as e:
                result["ibkr_connected"] = False
                result["details"].append(f"✗ IBKR: Connection error - {str(e)}")
                result["status"] = "INVALID"
        
        # If validation fails, check for HALT action
        if result["status"] == "INVALID" and self.charter.BROKER_CONNECTION_FAILURE_ACTION == "HALT":
            result["action"] = "HALT_TRADING"
            self.logger.error(f"🛑 BROKER CONNECTION FAILURE - TRADING HALTED")
        
        return result
    
    def get_status_summary(self) -> Dict:
        """Get current gate system status"""
        return {
            "charter_version": self.charter.CHARTER_VERSION,
            "crypto_hive_consensus": f"{self.charter.CRYPTO_AI_HIVE_VOTE_CONSENSUS:.0%}",
            "forex_hive_consensus": f"{self.charter.FOREX_AI_HIVE_VOTE_CONSENSUS:.0%}",
            "time_window": f"{self.charter.CRYPTO_TRADE_WINDOW_START_HOUR_ET}am-{self.charter.CRYPTO_TRADE_WINDOW_END_HOUR_ET}pm ET",
            "trading_days": self.charter.CRYPTO_TRADE_WINDOW_DAYS,
            "volatility_tiers": {
                "high": f"ATR > {self.charter.VOLATILITY_HIGH_ATR_THRESHOLD}x: {self.charter.VOLATILITY_HIGH_POSITION_SCALE*100:.0f}% position",
                "normal": f"ATR {self.charter.VOLATILITY_NORMAL_ATR_MIN}-{self.charter.VOLATILITY_NORMAL_ATR_MAX}x: {self.charter.VOLATILITY_NORMAL_POSITION_SCALE*100:.0f}% position",
                "low": f"ATR < {self.charter.VOLATILITY_LOW_ATR_THRESHOLD}x: {self.charter.VOLATILITY_LOW_POSITION_SCALE*100:.0f}% position"
            },
            "confluence_gates_required": f"{self.charter.CRYPTO_CONFLUENCE_SCORE_REQUIRED}/5",
            "all_4_improvements_active": True
        }


# ============================================================================
# TESTING & VALIDATION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CRYPTO ENTRY GATE SYSTEM - INITIALIZATION TEST")
    print("="*80 + "\n")
    
    # Initialize system
    gate_system = CryptoEntryGateSystem(pin=841921)
    
    # Display status
    status = gate_system.get_status_summary()
    print("✅ System initialized successfully")
    print("\nActive Configuration:")
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")
    
    print("\n" + "="*80)
    print("TEST CASE 1: Perfect Crypto Entry (All gates pass)")
    print("="*80)
    
    result1 = gate_system.validate_crypto_entry(
        symbol="BTC/USD",
        hive_consensus=0.95,
        base_position_size=450,
        current_atr=1.2,
        normal_atr=1.2,
        signal_data={
            'rsi': 45,
            'price': 100,
            'ma_20': 99,
            'ma_50': 98,
            'direction': 'UP',
            'volume': 2.0,
            'avg_volume_20': 1.0,
            'hive_consensus': 0.95,
            'trend_4h': 'UP',
            'trend_15m': 'UP'
        }
    )
    print(f"\nResult: {result1.overall_result}")
    print(f"Final Position Size: {result1.final_position_size:.2f}")
    
    print("\n" + "="*80)
    print("TEST CASE 2: Weak Crypto Entry (Insufficient confluence gates)")
    print("="*80)
    
    result2 = gate_system.validate_crypto_entry(
        symbol="ETH/USD",
        hive_consensus=0.88,  # Below 90%
        base_position_size=450,
        current_atr=2.5,  # High volatility
        normal_atr=1.2,
        signal_data={
            'rsi': 75,  # Overbought
            'price': 100,
            'ma_20': 102,
            'ma_50': 101,
            'direction': 'DOWN',
            'volume': 1.1,  # Weak volume
            'avg_volume_20': 1.0,
            'hive_consensus': 0.88,
            'trend_4h': 'DOWN',
            'trend_15m': 'UP'  # Counter-trend
        }
    )
    print(f"\nResult: {result2.overall_result}")
    print(f"Final Position Size: {result2.final_position_size:.2f}")
    print(f"Rejections: {len(result2.rejection_reasons)}")
    
    print("\n✅ All tests complete\n")
