#!/usr/bin/env python3
"""
Test script for the Enhanced OANDA Connector with Parameter Manager integration
Demonstrates how to use the connector with persistent credential storage
"""

import os
import logging
import time
from brokers.oanda_connector_enhanced import EnhancedOandaConnector
from util.parameter_manager import ParameterManager

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment_switching():
    """Test switching between practice and live environments"""
    logger.info("Testing environment switching...")
    
    # Create connector with default environment (practice)
    connector = EnhancedOandaConnector()
    logger.info(f"Initial environment: {connector.environment}")
    
    # Switch to live
    connector.switch_environment("live")
    logger.info(f"Switched to: {connector.environment}")
    
    # Switch back to practice
    connector.switch_environment("practice")
    logger.info(f"Switched back to: {connector.environment}")
    
    # Verify parameter persistence
    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    config_path = os.path.join(config_dir, 'oanda_parameters.json')
    param_manager = ParameterManager(config_path)
    stored_env = param_manager.get("oanda.environment")
    logger.info(f"Stored environment in parameter manager: {stored_env}")
    
    return connector

def test_credential_persistence():
    """Test credential persistence across connector instances"""
    logger.info("Testing credential persistence...")
    
    # First instance - should load from .env if available
    connector1 = EnhancedOandaConnector(environment="practice")
    
    # Store a test token if none exists (for demo purposes)
    if not connector1.api_token or connector1.api_token == "your_practice_token_here":
        logger.info("No API token found, setting a test token")
        # Use the same parameter manager instance as the connector
        param_manager = connector1.param_manager
        param_manager.set(
            "oanda.practice.token",
            "test_token_for_demo",
            component="test script"
        )
        param_manager.set(
            "oanda.practice.account_id",
            "test-account-123",
            component="test script"
        )
    
    # Second instance - should load from parameter manager
    logger.info("Creating second connector instance - should use stored credentials")
    connector2 = EnhancedOandaConnector(environment="practice")
    
    # Check if credentials match
    logger.info(f"Connector 1 has token: {'Yes' if connector1.api_token else 'No'}")
    logger.info(f"Connector 2 has token: {'Yes' if connector2.api_token else 'No'}")
    
    return connector2

def test_order_parameters():
    """Test order parameter tracking"""
    logger.info("Testing order parameter tracking...")
    
    connector = EnhancedOandaConnector(environment="practice")
    
    # Place a test order
    result = connector.place_oco_order(
        instrument="EUR_USD",
        entry_price=1.0500,
        stop_loss=1.0450,
        take_profit=1.0600,
        units=1000,
        order_type="LIMIT"
    )
    
    logger.info(f"Order result: {result}")
    
    # Check if order was stored in parameter manager
    # Use the same parameter manager instance as the connector
    param_manager = connector.param_manager
    order_id = result.get("order_id")
    
    if order_id:
        order_params = param_manager.get(f"oanda.orders.{order_id}")
        logger.info(f"Stored order parameters: {order_params}")
    
    return result

def main():
    """Run all tests"""
    logger.info("Starting Enhanced OANDA Connector tests")
    
    # Test environment switching
    connector = test_environment_switching()
    
    # Test credential persistence
    test_credential_persistence()
    
    # Test order parameter tracking
    test_order_parameters()
    
    # Get account info if credentials are available
    if connector.api_token and connector.api_token != "your_practice_token_here":
        account = connector.get_account_info()
        if account:
            logger.info(f"Account balance: {account.balance} {account.currency}")
            logger.info(f"Open positions: {account.open_positions}")
    
    logger.info("All tests completed")

if __name__ == "__main__":
    main()