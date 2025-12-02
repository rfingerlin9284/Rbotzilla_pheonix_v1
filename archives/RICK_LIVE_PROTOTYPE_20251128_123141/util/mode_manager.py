#!/usr/bin/env python3
"""
Mode Manager - .upgrade_toggle Integration
Reads system mode from .upgrade_toggle file and maps to connector environments
PIN: 841921
"""

from pathlib import Path
from typing import Dict, Optional
import sys

# Simple logger replacement (avoid util/logging.py conflict)
class SimpleLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

logger = SimpleLogger()

# Project paths
PROJECT_ROOT = Path("/home/ing/RICK/RICK_LIVE_CLEAN")
TOGGLE_FILE = PROJECT_ROOT / ".upgrade_toggle"

# Mode mappings
MODE_MAP = {
    "OFF": {"oanda": "practice", "coinbase": "sandbox", "description": "System OFF - paper trading only"},
    "GHOST": {"oanda": "practice", "coinbase": "sandbox", "description": "Ghost mode - 45min validation sessions"},
    "CANARY": {"oanda": "practice", "coinbase": "sandbox", "description": "Canary mode - extended validation with live-like params"},
    "LIVE": {"oanda": "live", "coinbase": "live", "description": "LIVE mode - REAL MONEY TRADING"}
}


def read_upgrade_toggle() -> str:
    """
    Read current mode from .upgrade_toggle file
    
    Returns:
        str: Current mode ('OFF', 'GHOST', 'CANARY', 'LIVE')
    """
    try:
        if not TOGGLE_FILE.exists():
            logger.warning(f".upgrade_toggle file not found at {TOGGLE_FILE}, defaulting to OFF")
            # Create with OFF default
            write_upgrade_toggle("OFF")
            return "OFF"
        
        with open(TOGGLE_FILE, 'r') as f:
            mode = f.read().strip().upper()
        
        # Validate mode
        if mode not in MODE_MAP:
            logger.warning(f"Invalid mode '{mode}' in .upgrade_toggle, defaulting to OFF")
            return "OFF"
        
        return mode
    
    except Exception as e:
        logger.error(f"Failed to read .upgrade_toggle: {e}, defaulting to OFF")
        return "OFF"


def write_upgrade_toggle(mode: str) -> bool:
    """
    Write mode to .upgrade_toggle file (requires PIN validation in production)
    
    Args:
        mode: Mode to set ('OFF', 'GHOST', 'CANARY', 'LIVE')
    
    Returns:
        bool: Success
    """
    try:
        mode = mode.strip().upper()
        
        if mode not in MODE_MAP:
            logger.error(f"Invalid mode '{mode}', must be one of: {list(MODE_MAP.keys())}")
            return False
        
        with open(TOGGLE_FILE, 'w') as f:
            f.write(mode + '\n')
        
        logger.info(f"✅ Updated .upgrade_toggle to: {mode}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to write .upgrade_toggle: {e}")
        return False


def get_connector_environment(venue: str) -> str:
    """
    Get connector environment based on current .upgrade_toggle mode
    
    Args:
        venue: 'oanda' or 'coinbase'
    
    Returns:
        str: Environment ('practice', 'sandbox', or 'live')
    """
    mode = read_upgrade_toggle()
    
    if venue.lower() not in MODE_MAP[mode]:
        logger.warning(f"Unknown venue '{venue}', defaulting to practice/sandbox")
        return "practice" if venue.lower() == "oanda" else "sandbox"
    
    environment = MODE_MAP[mode][venue.lower()]
    
    logger.info(f"Mode: {mode} → {venue.upper()} environment: {environment}")
    
    return environment


def get_mode_info() -> Dict[str, any]:
    """
    Get complete mode information
    
    Returns:
        dict: Mode info with current mode, environments, and description
    """
    mode = read_upgrade_toggle()
    mode_config = MODE_MAP[mode]
    
    return {
        "mode": mode,
        "oanda_environment": mode_config["oanda"],
        "coinbase_environment": mode_config["coinbase"],
        "description": mode_config["description"],
        "is_live": mode == "LIVE",
        "toggle_file": str(TOGGLE_FILE)
    }


def validate_live_mode_switch(pin: int) -> bool:
    """
    Validate PIN before switching to LIVE mode
    
    Args:
        pin: Charter PIN (841921)
    
    Returns:
        bool: True if PIN valid
    """
    REQUIRED_PIN = 841921
    
    if pin != REQUIRED_PIN:
        logger.error("Invalid PIN - LIVE mode switch rejected")
        return False
    
    logger.info("✅ PIN validated - LIVE mode switch authorized")
    return True


def switch_mode(new_mode: str, pin: Optional[int] = None) -> bool:
    """
    Switch system mode with optional PIN validation for LIVE
    
    Args:
        new_mode: Target mode ('OFF', 'GHOST', 'CANARY', 'LIVE')
        pin: Required for LIVE mode (841921)
    
    Returns:
        bool: Success
    """
    new_mode = new_mode.strip().upper()
    
    # Validate mode
    if new_mode not in MODE_MAP:
        logger.error(f"Invalid mode '{new_mode}'")
        return False
    
    # Require PIN for LIVE mode
    if new_mode == "LIVE":
        if pin is None:
            logger.error("PIN required for LIVE mode switch")
            return False
        
        if not validate_live_mode_switch(pin):
            return False
    
    # Write new mode
    if write_upgrade_toggle(new_mode):
        mode_info = get_mode_info()
        logger.info(f"🔄 Mode switched: {mode_info['description']}")
        logger.info(f"   OANDA → {mode_info['oanda_environment']}")
        logger.info(f"   Coinbase → {mode_info['coinbase_environment']}")
        return True
    
    return False


if __name__ == "__main__":
    # Test mode manager
    print("🧪 Mode Manager Test\n")
    
    info = get_mode_info()
    print(f"Current Mode: {info['mode']}")
    print(f"Description: {info['description']}")
    print(f"OANDA: {info['oanda_environment']}")
    print(f"Coinbase: {info['coinbase_environment']}")
    print(f"Is Live: {info['is_live']}")
    print(f"Toggle File: {info['toggle_file']}")
