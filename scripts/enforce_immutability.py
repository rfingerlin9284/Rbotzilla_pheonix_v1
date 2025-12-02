#!/usr/bin/env python3
"""
Charter and Gated Logic Immutability Enforcement
Ensures critical trading system files remain clean and immutable
PIN: 841921 | Generated: 2025-10-20
"""

import os
import sys
import hashlib
import logging
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
import stat
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/immutability_enforcer.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("immutability_enforcer")

# Critical files that must remain immutable
CRITICAL_FILES = [
    {
        "path": "foundation/rick_charter.py",
        "description": "Charter enforcement with immutable trading constants",
        "required_constants": [
            "PIN", "CHARTER_VERSION", "MAX_HOLD_DURATION_HOURS", 
            "MIN_RISK_REWARD_RATIO", "DAILY_LOSS_BREAKER_PCT",
            "DAILY_INCOME_TARGET_USD", "SMART_AGGRESSION_ENABLED"
        ],
        "validation_method": "validate_pin",
        "severity": "critical"
    },
    {
        "path": "logic/smart_logic.py",
        "description": "Gated logic for signal validation",
        "required_constants": [
            "MIN_RISK_REWARD_RATIO", "PIN", "FilterResult", 
            "SignalStrength", "SmartLogicFilter"
        ],
        "validation_method": "validate_signal",
        "severity": "critical"
    },
    {
        "path": "util/mode_manager.py",
        "description": "Trading mode management",
        "required_constants": [
            "PIN", "validate_live_mode_switch", "get_mode_info"
        ],
        "validation_method": None,
        "severity": "high"
    },
    {
        "path": "trading_engine.py",
        "description": "Unified trading engine",
        "required_constants": [
            "PAPER", "LIVE", "api", "broker_environment"
        ],
        "validation_method": None,
        "severity": "high"
    },
    {
        "path": "control_trading_mode.sh",
        "description": "Trading mode control script",
        "required_constants": [
            "PAPER", "LIVE", "PIN", "841921"
        ],
        "validation_method": None,
        "severity": "medium"
    }
]

# Checksum file location
CHECKSUM_FILE = ".charter_checksums.json"
BACKUP_DIR = "charter_backups"
VIOLATION_LOG = "logs/charter_violations.log"
LAST_CHECK_FILE = ".last_immutability_check"

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file"""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash
    except Exception as e:
        logger.error(f"Failed to calculate hash for {file_path}: {e}")
        return None

def verify_file_constants(file_path, required_constants):
    """Verify that required constants exist in the file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        missing_constants = []
        for const in required_constants:
            if const not in content:
                missing_constants.append(const)
        
        if missing_constants:
            logger.error(f"Missing required constants in {file_path}: {', '.join(missing_constants)}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Failed to verify constants in {file_path}: {e}")
        return False

def make_file_readonly(file_path):
    """Make file read-only to prevent modifications"""
    try:
        # Get current permissions
        current_mode = os.stat(file_path).st_mode
        
        # Remove write permissions for all users
        new_mode = current_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
        
        # Apply new permissions
        os.chmod(file_path, new_mode)
        logger.info(f"Made {file_path} read-only")
        return True
    except Exception as e:
        logger.error(f"Failed to make {file_path} read-only: {e}")
        return False

def create_backup(file_path):
    """Create backup of critical file"""
    try:
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), BACKUP_DIR)
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
        
        # Copy file to backup
        with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        
        logger.info(f"Created backup of {file_path} at {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup of {file_path}: {e}")
        return None

def load_checksums():
    """Load saved checksums from file"""
    try:
        checksum_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CHECKSUM_FILE)
        if os.path.exists(checksum_path):
            with open(checksum_path, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Failed to load checksums: {e}")
        return {}

def save_checksums(checksums):
    """Save checksums to file"""
    try:
        checksum_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CHECKSUM_FILE)
        with open(checksum_path, 'w') as f:
            json.dump(checksums, f, indent=2)
        
        # Make checksum file read-only
        make_file_readonly(checksum_path)
        
        logger.info(f"Saved checksums to {checksum_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save checksums: {e}")
        return False

def log_violation(file_path, violation_type, details):
    """Log a charter violation to the violation log"""
    try:
        violation_log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), VIOLATION_LOG)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(violation_log_path, 'a') as f:
            f.write(f"[{timestamp}] VIOLATION: {violation_type} in {file_path}\n")
            f.write(f"Details: {details}\n")
            f.write("-" * 80 + "\n")
        
        logger.warning(f"Violation logged to {violation_log_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to log violation: {e}")
        return False

def restore_from_backup(file_path, backup_path=None):
    """Restore a file from its most recent backup"""
    try:
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), BACKUP_DIR)
        filename = os.path.basename(file_path)
        
        if not backup_path:
            # Find the most recent backup
            backups = [f for f in os.listdir(backup_dir) if f.startswith(filename) and f.endswith('.bak')]
            if not backups:
                logger.error(f"No backups found for {file_path}")
                return False
            
            # Sort by timestamp (newest first)
            backups.sort(reverse=True)
            backup_path = os.path.join(backup_dir, backups[0])
        
        # Make the file writable if it's read-only
        if os.path.exists(file_path):
            current_mode = os.stat(file_path).st_mode
            os.chmod(file_path, current_mode | stat.S_IWUSR)
        
        # Copy backup to original location
        shutil.copy2(backup_path, file_path)
        
        # Make it read-only again
        make_file_readonly(file_path)
        
        logger.info(f"Restored {file_path} from backup {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to restore from backup: {e}")
        return False

def verify_file_integrity(file_info, saved_checksums, auto_restore=False):
    """Verify integrity of a critical file"""
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), file_info["path"])
    
    if not os.path.exists(file_path):
        logger.error(f"Critical file not found: {file_path}")
        log_violation(file_info["path"], "MISSING_FILE", "File does not exist")
        return False
    
    # Calculate current hash
    current_hash = calculate_file_hash(file_path)
    if not current_hash:
        return False
    
    # Check if we have a saved hash
    if file_info["path"] in saved_checksums:
        saved_hash = saved_checksums[file_info["path"]]
        
        if current_hash != saved_hash:
            logger.error(f"INTEGRITY VIOLATION: {file_path} has been modified!")
            logger.error(f"Expected hash: {saved_hash}")
            logger.error(f"Current hash: {current_hash}")
            
            # Log the violation
            log_violation(file_info["path"], "MODIFIED_FILE", 
                         f"Hash mismatch: expected {saved_hash}, got {current_hash}")
            
            # Auto-restore if enabled and it's a critical file
            if auto_restore and file_info["severity"] == "critical":
                logger.warning(f"Attempting to auto-restore {file_path} from backup")
                restore_from_backup(file_path)
            
            return False
        
        logger.info(f"Integrity verified for {file_path}")
    else:
        # First time seeing this file, save its hash
        logger.info(f"First-time integrity check for {file_path}")
        saved_checksums[file_info["path"]] = current_hash
    
    # Verify required constants
    if not verify_file_constants(file_path, file_info["required_constants"]):
        log_violation(file_info["path"], "MISSING_CONSTANTS", 
                     f"Required constants missing from {file_path}")
        return False
    
    return True

def check_for_unauthorized_modifications():
    """Check for any unauthorized modifications to critical files"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    last_check_file = os.path.join(root_dir, LAST_CHECK_FILE)
    
    # Get the last check time
    last_check_time = 0
    if os.path.exists(last_check_file):
        try:
            with open(last_check_file, 'r') as f:
                last_check_time = float(f.read().strip())
        except:
            pass
    
    # Check all critical files for modifications since last check
    modified_files = []
    for file_info in CRITICAL_FILES:
        file_path = os.path.join(root_dir, file_info["path"])
        if os.path.exists(file_path):
            mod_time = os.path.getmtime(file_path)
            if mod_time > last_check_time:
                modified_files.append((file_info["path"], mod_time))
    
    # Update the last check time
    with open(last_check_file, 'w') as f:
        f.write(str(time.time()))
    
    return modified_files

def enforce_immutability(auto_restore=False):
    """Main function to enforce immutability of critical files"""
    logger.info("Starting charter and gated logic immutability enforcement")
    
    # Check for unauthorized modifications
    modified_files = check_for_unauthorized_modifications()
    if modified_files:
        logger.warning(f"Detected {len(modified_files)} modified files since last check:")
        for file_path, mod_time in modified_files:
            mod_time_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
            logger.warning(f"  - {file_path} (modified at {mod_time_str})")
    
    # Load saved checksums
    checksums = load_checksums()
    
    # Track if all files are valid
    all_valid = True
    
    # Verify each critical file
    for file_info in CRITICAL_FILES:
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), file_info["path"])
        
        logger.info(f"Checking {file_info['description']}: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"Critical file not found: {file_path}")
            all_valid = False
            continue
        
        # Create backup
        backup_path = create_backup(file_path)
        
        # Verify integrity
        if not verify_file_integrity(file_info, checksums, auto_restore):
            all_valid = False
            logger.error(f"Integrity check failed for {file_path}")
            
            # Attempt to restore from backup if available and not already tried
            if backup_path and not auto_restore and file_info["severity"] == "critical":
                logger.warning(f"File integrity violation detected. Backup created at {backup_path}")
                logger.warning(f"Consider manual restoration with: ./enforce_charter_immutability.sh --restore {file_info['path']}")
            
            continue
        
        # Make file read-only
        make_file_readonly(file_path)
    
    # Save updated checksums
    if all_valid:
        save_checksums(checksums)
        logger.info("All charter and gated logic files verified and protected")
    else:
        logger.error("Some charter or gated logic files failed verification!")
    
    return all_valid

def verify_charter_pin(pin):
    """Verify charter PIN for authentication"""
    try:
        # Import the charter module
        from foundation.rick_charter import RickCharter
        return pin == RickCharter.PIN
    except Exception as e:
        logger.error(f"Failed to verify PIN: {e}")
        return False

def main():
    """Main entry point with command-line argument handling"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create backups directory if it doesn't exist
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), BACKUP_DIR)
    os.makedirs(backup_dir, exist_ok=True)
    
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Charter and Gated Logic Immutability Enforcement")
    parser.add_argument("pin", nargs="?", type=int, help="Charter PIN for authentication")
    parser.add_argument("--verify-only", action="store_true", help="Verify files without making changes")
    parser.add_argument("--auto-restore", action="store_true", help="Automatically restore modified critical files")
    parser.add_argument("--restore", metavar="FILE_PATH", help="Restore a specific file from backup")
    parser.add_argument("--list-backups", action="store_true", help="List all available backups")
    
    args = parser.parse_args()
    
    # Handle --list-backups
    if args.list_backups:
        print("Available backups:")
        for backup in sorted(os.listdir(backup_dir)):
            backup_path = os.path.join(backup_dir, backup)
            backup_time = datetime.fromtimestamp(os.path.getmtime(backup_path)).strftime("%Y-%m-%d %H:%M:%S")
            print(f"  - {backup} (created: {backup_time})")
        return 0
    
    # Handle --restore
    if args.restore:
        if not args.pin:
            logger.error("PIN required for restoration")
            return 1
        
        if not verify_charter_pin(args.pin):
            logger.error("Invalid PIN. Access denied.")
            return 1
        
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), args.restore)
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return 1
        
        if restore_from_backup(file_path):
            print(f"✅ Successfully restored {args.restore} from backup")
            return 0
        else:
            print(f"❌ Failed to restore {args.restore}")
            return 1
    
    # Check if PIN was provided for normal operation
    if args.pin:
        if not verify_charter_pin(args.pin):
            logger.error("Invalid PIN. Access denied.")
            return 1
    else:
        logger.warning("No PIN provided. Running in verification-only mode.")
        args.verify_only = True
    
    # Run enforcement
    if args.verify_only:
        logger.info("Running in verification-only mode")
        success = enforce_immutability(auto_restore=False)
    else:
        success = enforce_immutability(auto_restore=args.auto_restore)
    
    if success:
        print("✅ Charter and gated logic files verified and protected")
        return 0
    else:
        print("❌ Some charter or gated logic files failed verification!")
        return 1

if __name__ == "__main__":
    sys.exit(main())