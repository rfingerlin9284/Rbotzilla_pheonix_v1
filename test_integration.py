#!/usr/bin/env python3
"""
RBOTzilla Integration Test Script
Tests all backend endpoints and bot functionality
"""

import sys
import time
import logging
from rbotzilla_client import RBOTzillaClient

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def print_header(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_health(client: RBOTzillaClient) -> bool:
    """Test health endpoint"""
    print_header("HEALTH CHECK")
    
    if client.health_check():
        logger.info("✅ Backend is healthy")
        return True
    else:
        logger.error("❌ Backend unreachable")
        logger.error("   Ensure: python3 backend.py")
        return False

def test_bot_start_stop(client: RBOTzillaClient) -> bool:
    """Test bot start/stop"""
    print_header("BOT CONTROL")
    
    # Start
    logger.info("Starting bot...")
    if not client.start_bot():
        logger.error("❌ Failed to start bot")
        return False
    logger.info("✅ Bot started")
    
    # Wait
    time.sleep(3)
    
    # Check running
    if not client.is_running():
        logger.error("❌ Bot not running after start")
        return False
    logger.info("✅ Bot is running")
    
    # Stop
    logger.info("Stopping bot...")
    if not client.stop_bot():
        logger.error("❌ Failed to stop bot")
        return False
    logger.info("✅ Bot stopped")
    
    return True

def test_status(client: RBOTzillaClient) -> bool:
    """Test status endpoint"""
    print_header("BOT STATUS")
    
    status = client.get_status()
    if not status:
        logger.error("❌ Failed to get status")
        return False
    
    logger.info(f"Status: {status.status}")
    logger.info(f"Uptime: {client.get_uptime_formatted()}")
    logger.info(f"Logs count: {len(status.logs)}")
    
    if status.current_metrics:
        logger.info(f"Current metrics available")
    else:
        logger.warning("No metrics yet (bot not running)")
    
    return True

def test_metrics(client: RBOTzillaClient) -> bool:
    """Test metrics"""
    print_header("METRICS")
    
    # Start bot for metrics
    client.start_bot()
    time.sleep(2)
    
    metrics = client.get_metrics()
    if not metrics:
        logger.warning("⚠️  No metrics available")
        client.stop_bot()
        return True
    
    logger.info(f"Equity: ${metrics.equity:.2f}")
    logger.info(f"P&L: ${metrics.pnl:.2f}")
    logger.info(f"Margin Used: ${metrics.margin_used:.2f}")
    logger.info(f"Trades open: {metrics.trades_open}")
    logger.info(f"Trades closed: {metrics.trades_closed}")
    logger.info(f"Leverage: {metrics.leverage:.1f}x")
    logger.info("✅ Metrics retrieved")
    
    client.stop_bot()
    return True

def test_logs(client: RBOTzillaClient) -> bool:
    """Test logging"""
    print_header("LOGS")
    
    # Start bot to generate logs
    client.start_bot()
    time.sleep(2)
    
    logs = client.get_logs(limit=10)
    if not logs:
        logger.warning("⚠️  No logs yet")
        client.stop_bot()
        return True
    
    logger.info(f"Retrieved {len(logs)} logs:")
    for i, log in enumerate(logs[-5:], 1):
        level = log.get("level", "?")
        message = log.get("message", "")
        source = log.get("source", "?")
        logger.info(f"  {i}. [{level}] {source}: {message[:50]}")
    
    logger.info("✅ Logs retrieved")
    
    client.stop_bot()
    return True

def test_error_handling(client: RBOTzillaClient) -> bool:
    """Test error handling"""
    print_header("ERROR HANDLING")
    
    # Try invalid operations
    logger.info("Testing connection error handling...")
    
    bad_client = RBOTzillaClient("http://invalid-host:9999")
    result = bad_client.health_check()
    
    if result is False:
        logger.info("✅ Connection errors handled gracefully")
        return True
    else:
        logger.error("❌ Connection errors not handled")
        return False

def test_broker_apis(client: RBOTzillaClient) -> bool:
    """Test broker API endpoints"""
    print_header("BROKER APIs")
    
    logger.info("Fetching OANDA account...")
    oanda = client.get_oanda_account()
    if oanda:
        logger.info(f"✅ OANDA: {type(oanda)}")
    else:
        logger.warning("⚠️  OANDA unavailable (API key not set?)")
    
    logger.info("Fetching OANDA trades...")
    trades = client.get_oanda_trades()
    if trades is not None:
        logger.info(f"✅ OANDA trades: {len(trades)} open")
    else:
        logger.warning("⚠️  OANDA trades unavailable")
    
    logger.info("Fetching Coinbase account...")
    cb = client.get_coinbase_account()
    if cb:
        logger.info(f"✅ Coinbase: {type(cb)}")
    else:
        logger.warning("⚠️  Coinbase unavailable (API key not set?)")
    
    return True

def run_all_tests(client: RBOTzillaClient) -> int:
    """Run all tests"""
    print("\n" + "="*60)
    print("  🤖 RBOTzilla Integration Test Suite")
    print("="*60)
    
    tests = [
        ("Health Check", test_health),
        ("Bot Control", test_bot_start_stop),
        ("Bot Status", test_status),
        ("Metrics", test_metrics),
        ("Logging", test_logs),
        ("Error Handling", test_error_handling),
        ("Broker APIs", test_broker_apis),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func(client):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"❌ Test failed with exception: {e}")
            failed += 1
    
    # Summary
    print_header("TEST SUMMARY")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total: {len(tests)}")
    
    if failed == 0:
        logger.info("✅ All tests passed!")
        return 0
    else:
        logger.error(f"❌ {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    # Create client
    backend_url = "http://127.0.0.1:8000"
    logger.info(f"Connecting to backend: {backend_url}")
    
    client = RBOTzillaClient(backend_url)
    
    # Wait for backend
    logger.info("Waiting for backend to be available...")
    if not client.wait_for_backend(timeout=10):
        logger.error("Backend not available after 10 seconds")
        logger.error("Start backend with: python3 backend.py")
        sys.exit(1)
    
    # Run tests
    exit_code = run_all_tests(client)
    sys.exit(exit_code)
