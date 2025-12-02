#!/usr/bin/env python3
"""
Simple test script to verify parameter manager functionality
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the parameter manager
try:
    from util.parameter_manager import ParameterManager
    logger.info("Successfully imported ParameterManager")
except ImportError as e:
    logger.error(f"Failed to import ParameterManager: {e}")
    sys.exit(1)

def main():
    """Test parameter manager functionality"""
    logger.info("Starting simple parameter manager test")
    
    # Create config directory if it doesn't exist
    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    os.makedirs(config_dir, exist_ok=True)
    
    # Initialize parameter manager
    config_path = os.path.join(config_dir, 'test_parameters.json')
    logger.info(f"Initializing ParameterManager with config path: {config_path}")
    
    try:
        param_manager = ParameterManager(config_path)
        logger.info("Successfully created ParameterManager instance")
    except Exception as e:
        logger.error(f"Failed to create ParameterManager: {e}")
        sys.exit(1)
    
    # Test setting and getting parameters
    test_key = "test.parameter"
    test_value = "test_value"
    
    try:
        param_manager.set_parameter(
            test_key, 
            test_value,
            description="Test parameter",
            source="test_simple.py"
        )
        logger.info(f"Successfully set parameter {test_key} = {test_value}")
    except Exception as e:
        logger.error(f"Failed to set parameter: {e}")
    
    try:
        retrieved_value = param_manager.get_parameter(test_key)
        logger.info(f"Retrieved parameter {test_key} = {retrieved_value}")
        
        if retrieved_value == test_value:
            logger.info("Parameter retrieval successful!")
        else:
            logger.error(f"Parameter retrieval mismatch: expected {test_value}, got {retrieved_value}")
    except Exception as e:
        logger.error(f"Failed to get parameter: {e}")
    
    logger.info("Simple parameter manager test completed")

if __name__ == "__main__":
    main()