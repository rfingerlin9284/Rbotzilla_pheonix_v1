#!/usr/bin/env python3
"""
Test script for the parameter manager
"""
import os
import sys
from util.parameter_manager import get_parameter_manager

def main():
    # Make sure the logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Initialize the parameter manager with a test config
    test_config_path = "configs/test_parameters.json"
    os.makedirs(os.path.dirname(test_config_path), exist_ok=True)
    
    param_manager = get_parameter_manager(test_config_path)
    
    # Set some test parameters
    print("Setting initial parameters...")
    param_manager.set("risk_reward_ratio", 3.2, "test_script")
    param_manager.set("min_notional", 15000, "test_script")
    param_manager.set("max_latency", 300, "test_script")
    
    # Read parameters back
    print("\nReading parameters:")
    print(f"Risk/Reward Ratio: {param_manager.get('risk_reward_ratio')}")
    print(f"Min Notional: {param_manager.get('min_notional')}")
    print(f"Max Latency: {param_manager.get('max_latency')}")
    
    # Lock a parameter
    print("\nLocking risk_reward_ratio parameter...")
    param_manager.lock_parameter("risk_reward_ratio")
    
    # Try to modify the locked parameter
    print("\nAttempting to modify locked parameter...")
    success = param_manager.set("risk_reward_ratio", 2.5, "test_script")
    print(f"Modification {'succeeded' if success else 'failed'}")
    
    # Check the value hasn't changed
    print(f"Risk/Reward Ratio after attempted change: {param_manager.get('risk_reward_ratio')}")
    
    # Unlock and modify
    print("\nUnlocking and modifying parameter...")
    param_manager.unlock_parameter("risk_reward_ratio")
    param_manager.set("risk_reward_ratio", 2.5, "test_script")
    print(f"Risk/Reward Ratio after unlock and change: {param_manager.get('risk_reward_ratio')}")
    
    # Test bulk update
    print("\nTesting bulk update...")
    param_manager.bulk_update({
        "risk_reward_ratio": 3.0,
        "min_notional": 20000,
        "new_parameter": "test value"
    }, "test_script")
    
    # Show all parameters
    print("\nAll parameters after updates:")
    for key, value in param_manager.get_all_parameters().items():
        print(f"{key}: {value}")
    
    print("\nParameter manager test completed successfully!")
    print("Check logs/parameter_changes.log for the audit trail.")

if __name__ == "__main__":
    main()