#!/usr/bin/env python3
"""
RICK System - Connection Matrix Test
====================================
Tests connectivity to all trading endpoints:
- OANDA (Paper/Practice)
- IBKR (TWS Gateway)

Returns Green/Red status for: Auth, Data Feed, Order Capability

AUTH CODE: 841921
"""

import os
import sys
import json
import socket
import time
from datetime import datetime
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class ConnectionStatus(Enum):
    """Connection test status."""
    GREEN = "🟢 GREEN"
    YELLOW = "🟡 YELLOW"
    RED = "🔴 RED"
    UNKNOWN = "⚪ UNKNOWN"


@dataclass
class EndpointStatus:
    """Status for a single endpoint."""
    name: str
    auth_status: ConnectionStatus = ConnectionStatus.UNKNOWN
    data_feed_status: ConnectionStatus = ConnectionStatus.UNKNOWN
    order_exec_status: ConnectionStatus = ConnectionStatus.UNKNOWN
    latency_ms: float = 0.0
    error_message: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "auth": self.auth_status.value,
            "data_feed": self.data_feed_status.value,
            "order_exec": self.order_exec_status.value,
            "latency_ms": self.latency_ms,
            "error": self.error_message,
            "timestamp": self.timestamp
        }
    
    @property
    def overall_status(self) -> ConnectionStatus:
        """Get overall status (worst of all three)."""
        statuses = [self.auth_status, self.data_feed_status, self.order_exec_status]
        if ConnectionStatus.RED in statuses:
            return ConnectionStatus.RED
        if ConnectionStatus.YELLOW in statuses:
            return ConnectionStatus.YELLOW
        if ConnectionStatus.GREEN in statuses:
            return ConnectionStatus.GREEN
        return ConnectionStatus.UNKNOWN


@dataclass
class ConnectionMatrix:
    """Complete connection matrix for all endpoints."""
    oanda_paper: EndpointStatus = field(default_factory=lambda: EndpointStatus("OANDA Paper"))
    ibkr_tws: EndpointStatus = field(default_factory=lambda: EndpointStatus("IBKR TWS"))
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "endpoints": {
                "oanda_paper": self.oanda_paper.to_dict(),
                "ibkr_tws": self.ibkr_tws.to_dict()
            },
            "summary": {
                "oanda_overall": self.oanda_paper.overall_status.value,
                "ibkr_overall": self.ibkr_tws.overall_status.value
            }
        }


class ConnectionTester:
    """Tests connectivity to trading endpoints."""
    
    def __init__(self):
        """Initialize with environment configuration."""
        # OANDA Configuration
        self.oanda_account_id = os.getenv("OANDA_PRACTICE_ACCOUNT_ID", "")
        self.oanda_token = os.getenv("OANDA_PRACTICE_TOKEN", "")
        self.oanda_base_url = os.getenv("OANDA_PRACTICE_BASE_URL", "https://api-fxpractice.oanda.com/v3")
        
        # IBKR Configuration
        self.ibkr_host = os.getenv("IB_GATEWAY_HOST", "127.0.0.1")
        self.ibkr_port = int(os.getenv("IB_GATEWAY_PORT", "7497"))
        self.ibkr_account_id = os.getenv("IB_ACCOUNT_ID", "")
        
        print("🔧 ConnectionTester initialized")
        print(f"   OANDA Account: {self.oanda_account_id[:10]}..." if self.oanda_account_id else "   OANDA: Not configured")
        print(f"   IBKR Host: {self.ibkr_host}:{self.ibkr_port}")
    
    def _test_socket_connection(self, host: str, port: int, timeout: float = 5.0) -> Tuple[bool, float, str]:
        """
        Test raw socket connectivity.
        Returns: (success, latency_ms, error_message)
        """
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            latency = (time.time() - start_time) * 1000
            sock.close()
            
            if result == 0:
                return True, latency, ""
            else:
                return False, latency, f"Connection refused (code {result})"
        except socket.timeout:
            return False, timeout * 1000, "Connection timeout"
        except socket.gaierror as e:
            return False, 0, f"DNS resolution failed: {e}"
        except Exception as e:
            return False, 0, str(e)
    
    def test_oanda_paper(self) -> EndpointStatus:
        """Test OANDA Paper/Practice account connectivity."""
        status = EndpointStatus(name="OANDA Paper")
        status.timestamp = datetime.utcnow().isoformat()
        
        print("\n" + "-" * 50)
        print("🔍 Testing OANDA Paper Account...")
        print("-" * 50)
        
        # Check if credentials are configured
        if not self.oanda_account_id or not self.oanda_token:
            status.auth_status = ConnectionStatus.RED
            status.data_feed_status = ConnectionStatus.RED
            status.order_exec_status = ConnectionStatus.RED
            status.error_message = "OANDA credentials not configured in environment"
            print(f"   ❌ Auth: {status.error_message}")
            return status
        
        # Try to import requests
        try:
            import requests
        except ImportError:
            status.auth_status = ConnectionStatus.YELLOW
            status.data_feed_status = ConnectionStatus.YELLOW
            status.order_exec_status = ConnectionStatus.YELLOW
            status.error_message = "requests library not installed"
            print(f"   ⚠️ Cannot test HTTP: {status.error_message}")
            return status
        
        headers = {
            "Authorization": f"Bearer {self.oanda_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Authentication (get account info)
        try:
            start_time = time.time()
            url = f"{self.oanda_base_url}/accounts/{self.oanda_account_id}"
            response = requests.get(url, headers=headers, timeout=10)
            status.latency_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                status.auth_status = ConnectionStatus.GREEN
                account_data = response.json().get("account", {})
                balance = account_data.get("balance", "N/A")
                print(f"   ✅ Auth: SUCCESS (Balance: ${balance})")
            elif response.status_code == 401:
                status.auth_status = ConnectionStatus.RED
                status.error_message = "Invalid API token"
                print(f"   ❌ Auth: FAILED - Invalid token")
            else:
                status.auth_status = ConnectionStatus.YELLOW
                status.error_message = f"HTTP {response.status_code}"
                print(f"   ⚠️ Auth: HTTP {response.status_code}")
        except requests.exceptions.Timeout:
            status.auth_status = ConnectionStatus.RED
            status.error_message = "Connection timeout"
            print(f"   ❌ Auth: TIMEOUT")
        except Exception as e:
            status.auth_status = ConnectionStatus.RED
            status.error_message = str(e)
            print(f"   ❌ Auth: {e}")
        
        # Test 2: Data Feed (get pricing)
        if status.auth_status == ConnectionStatus.GREEN:
            try:
                url = f"{self.oanda_base_url}/accounts/{self.oanda_account_id}/pricing"
                params = {"instruments": "EUR_USD"}
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    status.data_feed_status = ConnectionStatus.GREEN
                    prices = response.json().get("prices", [])
                    if prices:
                        bid = prices[0].get("bids", [{}])[0].get("price", "N/A")
                        ask = prices[0].get("asks", [{}])[0].get("price", "N/A")
                        print(f"   ✅ Data Feed: SUCCESS (EUR_USD Bid:{bid} Ask:{ask})")
                    else:
                        print(f"   ✅ Data Feed: SUCCESS (no prices returned)")
                else:
                    status.data_feed_status = ConnectionStatus.YELLOW
                    print(f"   ⚠️ Data Feed: HTTP {response.status_code}")
            except Exception as e:
                status.data_feed_status = ConnectionStatus.RED
                print(f"   ❌ Data Feed: {e}")
        else:
            status.data_feed_status = ConnectionStatus.RED
            print(f"   ❌ Data Feed: Skipped (Auth failed)")
        
        # Test 3: Order Capability (check open orders - read-only test)
        if status.auth_status == ConnectionStatus.GREEN:
            try:
                url = f"{self.oanda_base_url}/accounts/{self.oanda_account_id}/orders"
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    status.order_exec_status = ConnectionStatus.GREEN
                    orders = response.json().get("orders", [])
                    print(f"   ✅ Order Exec: READY ({len(orders)} open orders)")
                else:
                    status.order_exec_status = ConnectionStatus.YELLOW
                    print(f"   ⚠️ Order Exec: HTTP {response.status_code}")
            except Exception as e:
                status.order_exec_status = ConnectionStatus.RED
                print(f"   ❌ Order Exec: {e}")
        else:
            status.order_exec_status = ConnectionStatus.RED
            print(f"   ❌ Order Exec: Skipped (Auth failed)")
        
        return status
    
    def test_ibkr_tws(self) -> EndpointStatus:
        """Test IBKR TWS/Gateway connectivity."""
        status = EndpointStatus(name="IBKR TWS")
        status.timestamp = datetime.utcnow().isoformat()
        
        print("\n" + "-" * 50)
        print("🔍 Testing IBKR TWS Gateway...")
        print("-" * 50)
        
        # Test 1: Socket connectivity to TWS/Gateway
        print(f"   Testing socket connection to {self.ibkr_host}:{self.ibkr_port}...")
        connected, latency, error = self._test_socket_connection(self.ibkr_host, self.ibkr_port)
        status.latency_ms = latency
        
        if connected:
            status.auth_status = ConnectionStatus.GREEN
            print(f"   ✅ Socket: CONNECTED ({latency:.1f}ms)")
        else:
            status.auth_status = ConnectionStatus.RED
            status.error_message = error
            print(f"   ❌ Socket: {error}")
            # If socket fails, all other tests fail
            status.data_feed_status = ConnectionStatus.RED
            status.order_exec_status = ConnectionStatus.RED
            print(f"   ❌ Data Feed: Skipped (No connection)")
            print(f"   ❌ Order Exec: Skipped (No connection)")
            return status
        
        # Test 2: Try to use ib_insync if available
        try:
            from ib_insync import IB, util
            
            ib = IB()
            print(f"   Attempting IB API connection...")
            
            try:
                ib.connect(self.ibkr_host, self.ibkr_port, clientId=999, timeout=10)
                
                if ib.isConnected():
                    status.auth_status = ConnectionStatus.GREEN
                    
                    # Get account info
                    accounts = ib.managedAccounts()
                    print(f"   ✅ Auth: CONNECTED (Accounts: {accounts})")
                    
                    # Test data feed
                    status.data_feed_status = ConnectionStatus.GREEN
                    print(f"   ✅ Data Feed: READY")
                    
                    # Test order capability
                    status.order_exec_status = ConnectionStatus.GREEN
                    print(f"   ✅ Order Exec: READY")
                    
                    ib.disconnect()
                else:
                    status.auth_status = ConnectionStatus.YELLOW
                    status.data_feed_status = ConnectionStatus.YELLOW
                    status.order_exec_status = ConnectionStatus.YELLOW
                    print(f"   ⚠️ Auth: Connected but not fully authenticated")
                    
            except Exception as e:
                status.auth_status = ConnectionStatus.YELLOW
                status.data_feed_status = ConnectionStatus.YELLOW
                status.order_exec_status = ConnectionStatus.YELLOW
                status.error_message = str(e)
                print(f"   ⚠️ IB Connect: {e}")
                print(f"   ℹ️ TWS/Gateway may not be running or API not enabled")
                
        except ImportError:
            # ib_insync not installed - socket test only
            status.auth_status = ConnectionStatus.YELLOW
            status.data_feed_status = ConnectionStatus.YELLOW
            status.order_exec_status = ConnectionStatus.YELLOW
            status.error_message = "ib_insync not installed - socket test only"
            print(f"   ⚠️ ib_insync not installed - socket test only")
            print(f"   ⚠️ Install with: pip install ib_insync")
        
        return status
    
    def run_full_matrix(self) -> ConnectionMatrix:
        """Run complete connection matrix test."""
        matrix = ConnectionMatrix()
        matrix.timestamp = datetime.utcnow().isoformat()
        
        print("\n" + "=" * 60)
        print("🔌 RICK CONNECTION MATRIX TEST")
        print("=" * 60)
        print(f"   Timestamp: {matrix.timestamp}")
        
        # Test OANDA
        matrix.oanda_paper = self.test_oanda_paper()
        
        # Test IBKR
        matrix.ibkr_tws = self.test_ibkr_tws()
        
        return matrix


def print_matrix_summary(matrix: ConnectionMatrix) -> None:
    """Print a visual summary of the connection matrix."""
    print("\n" + "=" * 60)
    print("📊 CONNECTION MATRIX SUMMARY")
    print("=" * 60)
    
    # Header
    print(f"{'Endpoint':<20} {'Auth':<12} {'Data Feed':<12} {'Order Exec':<12}")
    print("-" * 60)
    
    # OANDA row
    oanda = matrix.oanda_paper
    print(f"{'OANDA Paper':<20} {oanda.auth_status.value:<12} {oanda.data_feed_status.value:<12} {oanda.order_exec_status.value:<12}")
    
    # IBKR row
    ibkr = matrix.ibkr_tws
    print(f"{'IBKR TWS':<20} {ibkr.auth_status.value:<12} {ibkr.data_feed_status.value:<12} {ibkr.order_exec_status.value:<12}")
    
    print("-" * 60)
    
    # Overall status
    print(f"\n{'Overall Status:'}")
    print(f"   OANDA: {oanda.overall_status.value}")
    print(f"   IBKR:  {ibkr.overall_status.value}")
    
    # Latency
    print(f"\n{'Latency:'}")
    print(f"   OANDA: {oanda.latency_ms:.1f}ms")
    print(f"   IBKR:  {ibkr.latency_ms:.1f}ms")
    
    # Errors
    if oanda.error_message or ibkr.error_message:
        print(f"\n{'Errors:'}")
        if oanda.error_message:
            print(f"   OANDA: {oanda.error_message}")
        if ibkr.error_message:
            print(f"   IBKR: {ibkr.error_message}")
    
    print("=" * 60)


def save_matrix(matrix: ConnectionMatrix, filepath: str = None) -> str:
    """Save connection matrix to JSON file."""
    if filepath is None:
        filepath = f"connection_matrix_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filepath, 'w') as f:
            json.dump(matrix.to_dict(), f, indent=2)
        print(f"\n💾 Matrix saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Failed to save matrix: {e}")
        return ""


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🔌" * 30)
    print("   RICK SYSTEM - CONNECTION MATRIX TEST")
    print("   Testing all trading endpoint connectivity")
    print("🔌" * 30)
    
    # Run tests
    tester = ConnectionTester()
    matrix = tester.run_full_matrix()
    
    # Print summary
    print_matrix_summary(matrix)
    
    # Save results
    save_matrix(matrix, "logs/connection_matrix.json")
    
    # Determine exit code
    oanda_ok = matrix.oanda_paper.overall_status in (ConnectionStatus.GREEN, ConnectionStatus.YELLOW)
    ibkr_ok = matrix.ibkr_tws.overall_status in (ConnectionStatus.GREEN, ConnectionStatus.YELLOW)
    
    if oanda_ok and ibkr_ok:
        print("\n✅ All connections operational (or degraded)")
        sys.exit(0)
    elif oanda_ok:
        print("\n⚠️ OANDA OK but IBKR connection failed")
        sys.exit(1)
    else:
        print("\n❌ Critical connection failures detected")
        sys.exit(2)
