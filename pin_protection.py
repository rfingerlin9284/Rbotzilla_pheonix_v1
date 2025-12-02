#!/usr/bin/env python3
"""
RICK PIN Protection System
Double-entry PIN verification (841921) to lock/unlock code modifications
Prevents unauthorized changes to trading system
"""

import os
import sys
import hashlib
import json
from datetime import datetime
from typing import Optional

CORRECT_PIN = 841921
LOCK_FILE = '.system_lock.json'

class PINProtection:
    """
    Double-entry PIN system for code protection
    Locks/unlocks critical files
    """
    
    CRITICAL_FILES = [
        'foundation/rick_charter.py',
        'coinbase_safe_mode_engine.py',
        'hive/rick_hive_mind.py',
        'logic/smart_logic.py',
        'safe_mode_manager.py',
        'oanda_trading_engine.py',
        'brokers/oanda_connector.py'
    ]
    
    def __init__(self):
        # If no explicit CRITICAL_FILES listed, auto-discover candidates
        if not self.CRITICAL_FILES:
            self.CRITICAL_FILES = self.discover_critical_files()
        self.lock_state = self._load_lock_state()

    def discover_critical_files(self) -> list:
        """Discover python files to protect, excluding tests/scripts/hooks and stubs/placeholders."""
        roots = ['.']
        skip_dirs = ('tests', 'scripts', 'hooks', '.venv', 'venv', '__pycache__', 'ROLLBACK_SNAPSHOTS')
        placeholder_patterns = ('_placeholder', 'PLACEHOLDER', '.stub', 'stub', 'TODO')
        files = []
        for r in roots:
            for root, dirs, filenames in os.walk(r):
                if any(sd in root for sd in skip_dirs):
                    continue
                for fname in filenames:
                    if not fname.endswith('.py'):
                        continue
                    if any(pat in fname for pat in placeholder_patterns):
                        continue
                    path = os.path.join(root, fname)
                    files.append(path)
        return sorted(files)

    def check_git_renames(self) -> bool:
        """Check staged git rename operations that affect locked files.
        Returns True if a violating rename is detected.
        """
        import subprocess
        try:
            out = subprocess.check_output(['git', 'diff', '--cached', '--name-status'], text=True)
        except Exception:
            # Not in a git repo or cannot execute git - skip
            return False
        locked_set = set(self.CRITICAL_FILES)
        for line in out.splitlines():
            if not line:
                continue
            parts = line.split('\t') if '\t' in line else line.split()
            if parts[0].startswith('R') and len(parts) >= 3:
                old = parts[-2]
                new = parts[-1]
                if old in locked_set or new in locked_set:
                    print(f"Blocked rename involving locked file: {old} -> {new}")
                    return True
        return False

    def validate_pin_noninteractive(self, pin: str) -> bool:
        """Validate PIN programmatically (for CI/hooks without interactive input)."""
        try:
            pin_int = int(pin)
        except Exception:
            return False
        return pin_int == CORRECT_PIN
    
    def _load_lock_state(self) -> dict:
        """Load current lock state"""
        if os.path.exists(LOCK_FILE):
            with open(LOCK_FILE, 'r') as f:
                return json.load(f)
        return {"locked": False, "locked_at": None, "locked_by": None}
    
    def _save_lock_state(self):
        """Save lock state to file"""
        with open(LOCK_FILE, 'w') as f:
            json.dump(self.lock_state, f, indent=2)
    
    def verify_double_pin(self) -> bool:
        """
        Require user to enter PIN twice
        Both entries must match and be correct
        """
        print("=" * 80)
        print("🔐 PIN VERIFICATION REQUIRED")
        print("=" * 80)
        print()
        print("This operation requires double PIN verification for security.")
        print()
        
        # First entry
        try:
            pin1 = int(input("Enter PIN (1st entry): "))
        except ValueError:
            print("❌ Invalid PIN format")
            return False
        
        # Second entry
        try:
            pin2 = int(input("Enter PIN (2nd entry): "))
        except ValueError:
            print("❌ Invalid PIN format")
            return False
        
        # Verify both match
        if pin1 != pin2:
            print("❌ PIN entries do not match")
            return False
        
        # Verify correct PIN
        if pin1 != CORRECT_PIN:
            print("❌ Incorrect PIN")
            return False
        
        print("✅ PIN verified successfully")
        print()
        return True
    
    def lock_system(self):
        """Lock all critical files to read-only"""
        if not self.verify_double_pin():
            print("🚫 Lock operation cancelled - PIN verification failed")
            return
        
        print("🔒 LOCKING SYSTEM...")
        print()
        
        locked_count = 0
        for file_path in self.CRITICAL_FILES:
            if os.path.exists(file_path):
                try:
                    # Make read-only (444 permissions)
                    os.chmod(file_path, 0o444)
                    print(f"✅ Locked: {file_path}")
                    locked_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to lock {file_path}: {e}")
            else:
                print(f"⏭️  Not found: {file_path}")
        
        print()
        print(f"🔒 Locked {locked_count} critical files")
        
        # Update lock state
        self.lock_state = {
            "locked": True,
            "locked_at": datetime.utcnow().isoformat(),
            "locked_by": "PIN_PROTECTION_SYSTEM",
            "files_locked": locked_count
        }
        self._save_lock_state()
        
        print("✅ System is now LOCKED")
        print("   No code modifications allowed without unlocking first")
    
    def unlock_system(self):
        """Unlock critical files for editing"""
        if not self.verify_double_pin():
            print("🚫 Unlock operation cancelled - PIN verification failed")
            return
        
        print("🔓 UNLOCKING SYSTEM...")
        print()
        
        unlocked_count = 0
        for file_path in self.CRITICAL_FILES:
            if os.path.exists(file_path):
                try:
                    # Make read-write (644 permissions)
                    os.chmod(file_path, 0o644)
                    print(f"✅ Unlocked: {file_path}")
                    unlocked_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to unlock {file_path}: {e}")
            else:
                print(f"⏭️  Not found: {file_path}")
        
        print()
        print(f"🔓 Unlocked {unlocked_count} critical files")
        
        # Update lock state
        self.lock_state = {
            "locked": False,
            "unlocked_at": datetime.utcnow().isoformat(),
            "unlocked_by": "PIN_PROTECTION_SYSTEM",
            "files_unlocked": unlocked_count
        }
        self._save_lock_state()
        
        print("✅ System is now UNLOCKED")
        print("   ⚠️  Remember to lock again after making changes")
    
    def toggle_lock(self):
        """Toggle between locked and unlocked state"""
        current_state = self.lock_state.get('locked', False)
        
        if current_state:
            print("Current state: 🔒 LOCKED")
            print()
            response = input("Unlock system? (yes/no): ")
            if response.lower() == 'yes':
                self.unlock_system()
        else:
            print("Current state: 🔓 UNLOCKED")
            print()
            response = input("Lock system? (yes/no): ")
            if response.lower() == 'yes':
                self.lock_system()
    
    def check_lock_status(self):
        """Display current lock status"""
        print("=" * 80)
        print("🔐 SYSTEM LOCK STATUS")
        print("=" * 80)
        print()
        
        locked = self.lock_state.get('locked', False)
        status_icon = "🔒 LOCKED" if locked else "🔓 UNLOCKED"
        
        print(f"Status: {status_icon}")
        print()
        
        if locked:
            locked_at = self.lock_state.get('locked_at', 'Unknown')
            files_locked = self.lock_state.get('files_locked', 0)
            print(f"Locked at: {locked_at}")
            print(f"Files locked: {files_locked}")
            print()
            print("✅ Critical files are protected from modification")
        else:
            unlocked_at = self.lock_state.get('unlocked_at', 'Never locked')
            print(f"Last unlock: {unlocked_at}")
            print()
            print("⚠️  Critical files can be modified")
            print("   Recommend locking after making authorized changes")
        
        print()
        print("Critical files monitored:")
        for file_path in self.CRITICAL_FILES:
            if os.path.exists(file_path):
                perms = oct(os.stat(file_path).st_mode)[-3:]
                locked_marker = "🔒" if perms == "444" else "🔓"
                print(f"  {locked_marker} {file_path} (perms: {perms})")
            else:
                print(f"  ⚠️  {file_path} (not found)")
        
        print()
        print("=" * 80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='RICK PIN Protection System')
    parser.add_argument('--lock', action='store_true', help='Lock system')
    parser.add_argument('--unlock', action='store_true', help='Unlock system')
    parser.add_argument('--toggle-lock', action='store_true', help='Toggle lock state')
    parser.add_argument('--status', action='store_true', help='Check lock status')
    parser.add_argument('--check-rename', action='store_true', help='Check if staged renames affect locked files')
    
    args = parser.parse_args()
    
    protection = PINProtection()
    
    if args.lock:
        protection.lock_system()
    elif args.unlock:
        protection.unlock_system()
    elif args.toggle_lock:
        protection.toggle_lock()
    elif args.status:
        protection.check_lock_status()
    elif args.check_rename:
        blocked = protection.check_git_renames()
        if blocked:
            print('Renames affecting locked files detected - blocked')
            sys.exit(1)
        else:
            print('No protected renames detected')
            sys.exit(0)
    else:
        protection.check_lock_status()
