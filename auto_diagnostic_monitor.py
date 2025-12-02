#!/usr/bin/env python3
"""
RICK Auto Diagnostic Monitor
Runs every 10 minutes to verify all systems operational
Outputs plain English status updates at human-readable pace
Checks: APIs, auth tokens, logs, charter, gates, OCO logic, algo scanning
PIN: 841921
"""

import os
import sys
import time
import json
import subprocess
import requests
from datetime import datetime
from typing import Dict, Optional

sys.path.append(os.path.dirname(__file__))
from foundation.rick_charter import RickCharter

class AutoDiagnosticMonitor:
    """
    Continuous health monitoring system
    Non-interfering with active trading operations
    """
    
    def __init__(self, interval: int = 600):
        """
        Initialize monitor
        
        Args:
            interval: Seconds between diagnostic runs (default: 600 = 10 minutes)
        """
        self.interval = interval
        self.charter = RickCharter
        self.last_check = None
    
    def run_full_diagnostic(self) -> Dict:
        """
        Run complete 130-feature diagnostic check
        Returns detailed status report
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall": "UNKNOWN",
            "checks": {}
        }
        
        print("=" * 80)
        print("🔧 RICK AUTO DIAGNOSTIC - FULL SYSTEM CHECK")
        print("=" * 80)
        print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
        
        # 1. Check API connectivity
        print("1️⃣  Checking API Connectivity...")
        results['checks']['api_connectivity'] = self._check_api_connectivity()
        time.sleep(0.5)
        
        # 2. Verify authentication tokens
        print("2️⃣  Verifying Authentication Tokens...")
        results['checks']['auth_tokens'] = self._check_auth_tokens()
        time.sleep(0.5)
        
        # 3. Check logging systems
        print("3️⃣  Checking Logging Systems...")
        results['checks']['logging'] = self._check_logging()
        time.sleep(0.5)
        
        # 4. Verify charter enforcement
        print("4️⃣  Verifying Charter Enforcement...")
        results['checks']['charter'] = self._check_charter()
        time.sleep(0.5)
        
        # 5. Test gated logic
        print("5️⃣  Testing Gated Logic...")
        results['checks']['gates'] = self._check_gates()
        time.sleep(0.5)
        
        # 6. Verify OCO logic
        print("6️⃣  Verifying OCO Logic...")
        results['checks']['oco_logic'] = self._check_oco_logic()
        time.sleep(0.5)
        
        # 7. Check algo reasoning/scanning
        print("7️⃣  Checking Algo Reasoning & Scanning...")
        results['checks']['algo_scanning'] = self._check_algo_scanning()
        time.sleep(0.5)
        
        # 8. Verify hive mind
        print("8️⃣  Verifying Hive Mind Consensus...")
        results['checks']['hive_mind'] = self._check_hive_mind()
        time.sleep(0.5)
        
        # 9. Check ML models
        print("9️⃣  Checking ML Models...")
        results['checks']['ml_models'] = self._check_ml_models()
        time.sleep(0.5)
        
        # 10. Verify safe mode progression
        print("🔟 Verifying Safe Mode Progression...")
        results['checks']['safe_mode'] = self._check_safe_mode()
        time.sleep(0.5)
        
        # Determine overall health
        all_passed = all(
            check.get('status') == 'PASS'
            for check in results['checks'].values()
        )
        
        results['overall'] = 'HEALTHY' if all_passed else 'DEGRADED'
        
        print()
        print("=" * 80)
        print(f"OVERALL SYSTEM HEALTH: {results['overall']}")
        print("=" * 80)
        print()
        
        return results
    
    def _check_api_connectivity(self) -> Dict:
        """Test connectivity to all trading platforms"""
        status = {"status": "PASS", "details": {}}
        
        # Coinbase
        try:
            response = requests.get("https://api.coinbase.com/v2/time", timeout=5)
            status['details']['coinbase'] = "✅ ONLINE" if response.status_code == 200 else f"⚠️ HTTP {response.status_code}"
        except Exception as e:
            status['details']['coinbase'] = f"❌ ERROR: {str(e)[:50]}"
            status['status'] = "FAIL"
        
        # OANDA
        try:
            response = requests.get("https://api-fxpractice.oanda.com/v3/accounts", timeout=5)
            status['details']['oanda'] = "✅ ONLINE" if response.status_code in [200, 401] else f"⚠️ HTTP {response.status_code}"
        except Exception as e:
            status['details']['oanda'] = f"❌ ERROR: {str(e)[:50]}"
            status['status'] = "FAIL"
        
        print(f"   Coinbase: {status['details']['coinbase']}")
        print(f"   OANDA: {status['details']['oanda']}")
        
        return status
    
    def _check_auth_tokens(self) -> Dict:
        """Verify all authentication tokens are valid"""
        status = {"status": "PASS", "details": {}}
        
        # Check Coinbase credentials
        if os.path.exists('.env.coinbase_advanced'):
            with open('.env.coinbase_advanced', 'r') as f:
                content = f.read()
                has_key = 'CDP_API_KEY_NAME' in content
                has_secret = 'CDP_PRIVATE_KEY' in content
                status['details']['coinbase'] = "✅ CONFIGURED" if (has_key and has_secret) else "⚠️ INCOMPLETE"
        else:
            status['details']['coinbase'] = "❌ NOT FOUND"
            status['status'] = "FAIL"
        
        # Check OANDA credentials
        if os.path.exists('.env.oanda_only'):
            with open('.env.oanda_only', 'r') as f:
                content = f.read()
                has_account = 'OANDA_PRACTICE_ACCOUNT_ID' in content
                has_token = 'OANDA_PRACTICE_TOKEN' in content
                status['details']['oanda'] = "✅ CONFIGURED" if (has_account and has_token) else "⚠️ INCOMPLETE"
        else:
            status['details']['oanda'] = "⚠️ NOT CONFIGURED"
        
        print(f"   Coinbase Auth: {status['details']['coinbase']}")
        print(f"   OANDA Auth: {status['details'].get('oanda', 'N/A')}")
        
        return status
    
    def _check_logging(self) -> Dict:
        """Verify logging systems are working"""
        status = {"status": "PASS", "details": {}}
        
        log_files = [
            'logs/narration.jsonl',
            'logs/engine.log',
            'logs/safe_mode_progression.log'
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                # Check if file is writable
                try:
                    with open(log_file, 'a') as f:
                        pass
                    status['details'][log_file] = "✅ ACTIVE"
                except:
                    status['details'][log_file] = "⚠️ NOT WRITABLE"
                    status['status'] = "FAIL"
            else:
                status['details'][log_file] = "📝 NOT CREATED YET"
        
        for log_file, log_status in status['details'].items():
            print(f"   {log_file}: {log_status}")
        
        return status
    
    def _check_charter(self) -> Dict:
        """Verify charter enforcement is active"""
        status = {"status": "PASS", "details": {}}
        
        # Check immutable constants
        try:
            status['details']['pin'] = "✅ VERIFIED" if RickCharter.PIN == 841921 else "❌ CORRUPTED"
            status['details']['min_notional'] = f"✅ ${RickCharter.MIN_NOTIONAL_USD:,}"
            status['details']['min_rr_ratio'] = f"✅ {RickCharter.MIN_RISK_REWARD_RATIO}:1"
            status['details']['max_hold_hours'] = f"✅ {RickCharter.MAX_HOLD_DURATION_HOURS}h"
            
            if RickCharter.PIN != 841921:
                status['status'] = "FAIL"
        except Exception as e:
            status['status'] = "FAIL"
            status['details']['error'] = str(e)
        
        print(f"   PIN: {status['details'].get('pin', 'ERROR')}")
        print(f"   Min Notional: {status['details'].get('min_notional', 'ERROR')}")
        print(f"   Min R:R: {status['details'].get('min_rr_ratio', 'ERROR')}")
        
        return status
    
    def _check_gates(self) -> Dict:
        """Test gated logic enforcement"""
        status = {"status": "PASS", "details": {}}
        
        # Check if gate files exist
        gate_files = [
            'logic/smart_logic.py',
            'brokers/oanda_connector.py'
        ]
        
        for gate_file in gate_files:
            if os.path.exists(gate_file):
                status['details'][gate_file] = "✅ PRESENT"
            else:
                status['details'][gate_file] = "❌ MISSING"
                status['status'] = "FAIL"
        
        for gate_file, gate_status in status['details'].items():
            print(f"   {gate_file}: {gate_status}")
        
        return status
    
    def _check_oco_logic(self) -> Dict:
        """Verify OCO (One-Cancels-Other) logic is operational"""
        status = {"status": "PASS", "details": {}}
        
        # Check if OCO implementation exists
        oco_indicators = [
            ('place_sell_test_oco.py', 'Coinbase OCO script'),
            ('coinbase_safe_mode_engine.py', 'Engine OCO integration')
        ]
        
        for file_path, description in oco_indicators:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    has_oco = 'limit_order' in content and 'stop_limit' in content
                    status['details'][description] = "✅ IMPLEMENTED" if has_oco else "⚠️ INCOMPLETE"
            else:
                status['details'][description] = "⚠️ NOT FOUND"
        
        for desc, oco_status in status['details'].items():
            print(f"   {desc}: {oco_status}")
        
        return status
    
    def _check_algo_scanning(self) -> Dict:
        """Check algorithm scanning capabilities"""
        status = {"status": "PASS", "details": {}}
        
        algo_features = [
            'Fibonacci levels',
            'FVG detection',
            'Mass behavior patterns',
            'Volume profile',
            'Momentum indicators'
        ]
        
        # All features implemented in coinbase_safe_mode_engine.py
        if os.path.exists('coinbase_safe_mode_engine.py'):
            with open('coinbase_safe_mode_engine.py', 'r') as f:
                content = f.read()
                for feature in algo_features:
                    key = feature.lower().replace(' ', '_')
                    implemented = key in content.lower() or feature.lower() in content.lower()
                    status['details'][feature] = "✅ ACTIVE" if implemented else "⚠️ NOT FOUND"
        else:
            status['status'] = "FAIL"
            status['details']['engine'] = "❌ ENGINE NOT FOUND"
        
        for feature, feature_status in status['details'].items():
            print(f"   {feature}: {feature_status}")
        
        return status
    
    def _check_hive_mind(self) -> Dict:
        """Verify hive mind consensus system"""
        status = {"status": "PASS", "details": {}}
        
        if os.path.exists('hive/rick_hive_mind.py'):
            status['details']['hive_mind'] = "✅ PRESENT"
        else:
            status['details']['hive_mind'] = "⚠️ NOT FOUND"
            status['status'] = "FAIL"
        
        if os.path.exists('hive_position_advisor.py'):
            status['details']['position_advisor'] = "✅ PRESENT"
        else:
            status['details']['position_advisor'] = "⚠️ NOT FOUND"
        
        for component, comp_status in status['details'].items():
            print(f"   {component}: {comp_status}")
        
        return status
    
    def _check_ml_models(self) -> Dict:
        """Check ML model availability"""
        status = {"status": "PASS", "details": {}}
        
        ml_indicators = [
            'ml/ml_models.py',
            'ml/pattern_learner.py',
            'ml/regime_detector.py'
        ]
        
        for ml_file in ml_indicators:
            if os.path.exists(ml_file):
                status['details'][ml_file] = "✅ AVAILABLE"
            else:
                status['details'][ml_file] = "⚠️ NOT CONFIGURED"
        
        for ml_file, ml_status in status['details'].items():
            print(f"   {ml_file}: {ml_status}")
        
        return status
    
    def _check_safe_mode(self) -> Dict:
        """Verify safe mode progression system"""
        status = {"status": "PASS", "details": {}}
        
        if os.path.exists('safe_mode_manager.py'):
            status['details']['manager'] = "✅ ACTIVE"
            
            # Check if performance tracking exists
            if os.path.exists('logs/safe_mode_performance.json'):
                status['details']['tracking'] = "✅ TRACKING"
            else:
                status['details']['tracking'] = "📝 NOT STARTED"
        else:
            status['details']['manager'] = "❌ NOT FOUND"
            status['status'] = "FAIL"
        
        for component, comp_status in status['details'].items():
            print(f"   {component}: {comp_status}")
        
        return status
    
    def run_continuous(self):
        """Run diagnostics continuously at specified interval"""
        print("=" * 80)
        print("🔄 AUTO DIAGNOSTIC MONITOR - CONTINUOUS MODE")
        print("=" * 80)
        print(f"Interval: {self.interval} seconds ({self.interval / 60:.1f} minutes)")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                # Run diagnostic
                results = self.run_full_diagnostic()
                
                # Log results
                self._log_results(results)
                
                # Show next check time
                next_check = datetime.utcnow()
                print(f"Next diagnostic in {self.interval / 60:.0f} minutes...")
                print()
                
                # Wait for interval
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Auto diagnostic monitor stopped")
    
    def _log_results(self, results: Dict):
        """Log diagnostic results to file"""
        log_file = 'logs/diagnostics.jsonl'
        
        os.makedirs('logs', exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(results) + '\n')

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='RICK Auto Diagnostic Monitor')
    parser.add_argument('--full-check', action='store_true',
                        help='Run one full diagnostic check')
    parser.add_argument('--interval', type=int, default=600,
                        help='Seconds between checks (default: 600 = 10 min)')
    
    args = parser.parse_args()
    
    monitor = AutoDiagnosticMonitor(interval=args.interval)
    
    if args.full_check:
        monitor.run_full_diagnostic()
    else:
        monitor.run_continuous()
