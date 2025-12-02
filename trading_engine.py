#!/usr/bin/env python3
"""
Unified Trading Engine for RICK Trading System
Supports both PAPER (api=true) and LIVE (api=false) modes
"""

import os
import sys
import time
import logging
import json
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/trading_engine.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("trading_engine")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import required modules
from util.mode_manager import get_mode_info, read_upgrade_toggle
from util.parameter_manager import ParameterManager

class TradingEngine:
    """Unified trading engine for both PAPER and LIVE modes"""
    
    def __init__(self):
        """Initialize the trading engine"""
        self.logger = logger
        self.logger.info("Initializing Unified Trading Engine")
        
        # Get current mode
        self.mode_info = get_mode_info()
        self.logger.info(f"Current mode: {self.mode_info['mode']}")
        self.logger.info(f"API Enabled: {self.mode_info['api']}")
        
        # Initialize parameter manager
        config_path = os.path.join(os.path.dirname(__file__), 'configs', 'system_parameters.json')
        self.param_manager = ParameterManager(config_path)
        
        # Set up trading parameters based on mode
        self.setup_trading_parameters()
        
        # Initialize brokers
        self.initialize_brokers()
        
        # Create PID file
        self.create_pid_file()
    
    def setup_trading_parameters(self):
        """Set up trading parameters based on current mode"""
        self.logger.info("Setting up trading parameters")
        
        # Load appropriate config based on mode
        if self.mode_info['mode'] == "PAPER":
            config_file = os.path.join(os.path.dirname(__file__), 'configs', 'paper_trading_config.json')
        else:  # LIVE
            config_file = os.path.join(os.path.dirname(__file__), 'configs', 'config_live.json')
        
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
                self.logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
        
        # Set API flag in parameters
        self.param_manager.set_parameter(
            "system.api_enabled", 
            self.mode_info['api'],
            description="API enabled flag (true for PAPER, false for LIVE)",
            source="trading_engine.py"
        )
        
        # Set mode in parameters
        self.param_manager.set_parameter(
            "system.mode", 
            self.mode_info['mode'],
            description="Current trading mode (PAPER or LIVE)",
            source="trading_engine.py"
        )
    
    def initialize_brokers(self):
        """Initialize broker connections based on current mode"""
        self.logger.info("Initializing broker connections")
        
        # Initialize OANDA connection
        oanda_env = self.mode_info['oanda_environment']
        self.logger.info(f"Connecting to OANDA ({oanda_env})")
        
        # Initialize Coinbase connection
        coinbase_env = self.mode_info['coinbase_environment']
        self.logger.info(f"Connecting to Coinbase ({coinbase_env})")
        
        # Additional broker initialization code would go here
    
    def create_pid_file(self):
        """Create PID file for the trading engine"""
        pid = os.getpid()
        pid_file = ".trading_engine.pid"
        
        with open(pid_file, 'w') as f:
            f.write(str(pid))
        
        self.logger.info(f"Created PID file: {pid_file} with PID: {pid}")
    
    def run(self):
        """Run the trading engine main loop"""
        self.logger.info(f"Starting trading engine in {self.mode_info['mode']} mode")
        
        try:
            while True:
                # Check if mode has changed
                current_mode = read_upgrade_toggle()
                if current_mode != self.mode_info['mode']:
                    self.logger.info(f"Mode changed from {self.mode_info['mode']} to {current_mode}")
                    self.logger.info("Restarting trading engine with new mode")
                    # In a real implementation, you might want to gracefully shut down
                    # and restart the engine, or handle the mode change dynamically
                    sys.exit(0)
                
                # Main trading logic would go here
                self.logger.info(f"Trading engine running in {self.mode_info['mode']} mode (API: {self.mode_info['api']})")
                
                # Sleep to avoid high CPU usage
                time.sleep(10)
        
        except KeyboardInterrupt:
            self.logger.info("Trading engine stopped by user")
        except Exception as e:
            self.logger.error(f"Trading engine error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources before exiting"""
        self.logger.info("Cleaning up resources")
        
        # Remove PID file
        pid_file = ".trading_engine.pid"
        if os.path.exists(pid_file):
            os.remove(pid_file)
            self.logger.info(f"Removed PID file: {pid_file}")

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Initialize and run the trading engine
    engine = TradingEngine()
    engine.run()