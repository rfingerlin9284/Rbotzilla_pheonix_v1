#!/usr/bin/env python3
"""
================================================================================
RICK LIVE CLEAN - CHANGE TRACKER v3.0
================================================================================
Purpose: Singleton class that logs every file modification with hash and auth PIN
Auth Code: 841921 required for modifications
Generated: 2025-11-26

Usage:
    from .rick_system.change_tracker import ChangeTracker
    tracker = ChangeTracker()
    tracker.log_modification("path/to/file.py", auth_pin=841921)
================================================================================
"""

import os
import sys
import json
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum


class EventType(Enum):
    """Types of trackable events."""
    FILE_CREATED = "FILE_CREATED"
    FILE_MODIFIED = "FILE_MODIFIED"
    FILE_DELETED = "FILE_DELETED"
    FILE_RENAMED = "FILE_RENAMED"
    SNAPSHOT_CREATED = "SNAPSHOT_CREATED"
    CONFIG_CHANGED = "CONFIG_CHANGED"
    TRADE_EXECUTED = "TRADE_EXECUTED"
    SYSTEM_START = "SYSTEM_START"
    SYSTEM_STOP = "SYSTEM_STOP"
    AUTH_ATTEMPT = "AUTH_ATTEMPT"
    AUTH_FAILURE = "AUTH_FAILURE"


@dataclass
class ChangeRecord:
    """Represents a single change record."""
    timestamp: str
    event_type: str
    file_path: str
    auth_pin: int
    content_hash: Optional[str]
    diff_hash: Optional[str]
    details: Dict[str, Any]
    validated: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class ChangeTracker:
    """
    Singleton class for tracking all file modifications in RICK system.
    
    Features:
    - Logs every file modification with timestamp
    - Computes content hash and diff hash
    - Requires AUTH PIN (841921) for validation
    - Thread-safe singleton pattern
    - Persists to JSONL log file
    """
    
    _instance = None
    _lock = threading.Lock()
    
    # Immutable auth code
    MASTER_AUTH_PIN = 841921
    
    def __new__(cls):
        """Thread-safe singleton implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the change tracker."""
        if self._initialized:
            return
            
        self._initialized = True
        
        # Paths
        self.workspace = Path("/home/ing/RICK/RICK_LIVE_CLEAN")
        self.system_dir = self.workspace / ".rick_system"
        self.log_file = self.system_dir / "change_log.jsonl"
        self.index_file = self.system_dir / "change_index.json"
        
        # Ensure directories exist
        self.system_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self._cache: List[ChangeRecord] = []
        self._file_hashes: Dict[str, str] = {}
        
        # Load existing index
        self._load_index()
        
        # Log system start
        self.log_event(
            event_type=EventType.SYSTEM_START,
            file_path="SYSTEM",
            auth_pin=self.MASTER_AUTH_PIN,
            details={"version": "3.0", "initialized": datetime.now().isoformat()}
        )
    
    def _load_index(self) -> None:
        """Load the file hash index from disk."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    self._file_hashes = data.get("file_hashes", {})
            except (json.JSONDecodeError, IOError):
                self._file_hashes = {}
    
    def _save_index(self) -> None:
        """Save the file hash index to disk."""
        try:
            with open(self.index_file, 'w') as f:
                json.dump({
                    "file_hashes": self._file_hashes,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)
        except IOError as e:
            print(f"WARNING: Could not save index: {e}", file=sys.stderr)
    
    def _compute_hash(self, content: bytes) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content).hexdigest()
    
    def _compute_file_hash(self, file_path: str) -> Optional[str]:
        """Compute hash of a file's contents."""
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                with open(path, 'rb') as f:
                    return self._compute_hash(f.read())
        except (IOError, PermissionError):
            pass
        return None
    
    def _compute_diff_hash(self, file_path: str, new_hash: str) -> Optional[str]:
        """Compute hash representing the diff (old_hash + new_hash)."""
        old_hash = self._file_hashes.get(file_path, "")
        if old_hash and new_hash:
            diff_content = f"{old_hash}:{new_hash}".encode()
            return self._compute_hash(diff_content)
        return None
    
    def validate_pin(self, pin: int) -> bool:
        """Validate the auth PIN."""
        valid = pin == self.MASTER_AUTH_PIN
        
        if not valid:
            # Log failed auth attempt
            self._write_record(ChangeRecord(
                timestamp=datetime.now().isoformat(),
                event_type=EventType.AUTH_FAILURE.value,
                file_path="AUTH_CHECK",
                auth_pin=pin,
                content_hash=None,
                diff_hash=None,
                details={"attempted_pin": pin, "valid": False},
                validated=False
            ))
        
        return valid
    
    def log_event(
        self,
        event_type: EventType,
        file_path: str,
        auth_pin: int,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log a generic event.
        
        Args:
            event_type: Type of event from EventType enum
            file_path: Path to the affected file or "SYSTEM" for system events
            auth_pin: Authorization PIN (must be 841921)
            details: Optional additional details
            
        Returns:
            True if logged successfully, False if auth failed
        """
        # Validate PIN
        validated = self.validate_pin(auth_pin)
        
        if not validated:
            print(f"ERROR: Invalid AUTH PIN. Event not logged.", file=sys.stderr)
            return False
        
        # Compute hashes if file exists
        content_hash = None
        diff_hash = None
        
        if file_path != "SYSTEM" and Path(file_path).exists():
            content_hash = self._compute_file_hash(file_path)
            if content_hash:
                diff_hash = self._compute_diff_hash(file_path, content_hash)
                # Update hash index
                self._file_hashes[file_path] = content_hash
        
        # Create record
        record = ChangeRecord(
            timestamp=datetime.now().isoformat(),
            event_type=event_type.value if isinstance(event_type, EventType) else event_type,
            file_path=file_path,
            auth_pin=auth_pin,
            content_hash=content_hash,
            diff_hash=diff_hash,
            details=details or {},
            validated=True
        )
        
        # Write record
        self._write_record(record)
        
        # Save index
        self._save_index()
        
        return True
    
    def log_modification(
        self,
        file_path: str,
        auth_pin: int,
        old_content: Optional[str] = None,
        new_content: Optional[str] = None,
        description: Optional[str] = None
    ) -> bool:
        """
        Log a file modification.
        
        Args:
            file_path: Path to the modified file
            auth_pin: Authorization PIN (must be 841921)
            old_content: Previous content (optional, for diff)
            new_content: New content (optional, for diff)
            description: Human-readable description of change
            
        Returns:
            True if logged successfully
        """
        details = {"description": description or "File modified"}
        
        if old_content and new_content:
            # Compute diff hash from content
            old_hash = self._compute_hash(old_content.encode())
            new_hash = self._compute_hash(new_content.encode())
            details["old_hash"] = old_hash[:16]
            details["new_hash"] = new_hash[:16]
            details["size_delta"] = len(new_content) - len(old_content)
        
        return self.log_event(
            event_type=EventType.FILE_MODIFIED,
            file_path=file_path,
            auth_pin=auth_pin,
            details=details
        )
    
    def log_creation(
        self,
        file_path: str,
        auth_pin: int,
        description: Optional[str] = None
    ) -> bool:
        """Log a file creation."""
        return self.log_event(
            event_type=EventType.FILE_CREATED,
            file_path=file_path,
            auth_pin=auth_pin,
            details={"description": description or "File created"}
        )
    
    def log_deletion(
        self,
        file_path: str,
        auth_pin: int,
        description: Optional[str] = None
    ) -> bool:
        """Log a file deletion."""
        return self.log_event(
            event_type=EventType.FILE_DELETED,
            file_path=file_path,
            auth_pin=auth_pin,
            details={"description": description or "File deleted"}
        )
    
    def _write_record(self, record: ChangeRecord) -> None:
        """Write a record to the log file."""
        try:
            with open(self.log_file, 'a') as f:
                f.write(record.to_json() + '\n')
            
            # Add to cache
            self._cache.append(record)
            
            # Trim cache if too large
            if len(self._cache) > 1000:
                self._cache = self._cache[-500:]
                
        except IOError as e:
            print(f"ERROR: Could not write to log: {e}", file=sys.stderr)
    
    def get_recent_changes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get the most recent changes from cache."""
        return [r.to_dict() for r in self._cache[-limit:]]
    
    def get_file_history(self, file_path: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get change history for a specific file."""
        history = []
        
        # Check cache first
        for record in reversed(self._cache):
            if record.file_path == file_path:
                history.append(record.to_dict())
                if len(history) >= limit:
                    break
        
        # If not enough in cache, read from file
        if len(history) < limit and self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            if data.get("file_path") == file_path:
                                if data not in history:
                                    history.append(data)
                        except json.JSONDecodeError:
                            continue
            except IOError:
                pass
        
        return history[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tracking statistics."""
        stats = {
            "total_records": 0,
            "tracked_files": len(self._file_hashes),
            "cache_size": len(self._cache),
            "log_file_size": 0,
            "events_by_type": {}
        }
        
        if self.log_file.exists():
            stats["log_file_size"] = self.log_file.stat().st_size
            
            try:
                with open(self.log_file, 'r') as f:
                    for line in f:
                        stats["total_records"] += 1
                        try:
                            data = json.loads(line)
                            event_type = data.get("event_type", "UNKNOWN")
                            stats["events_by_type"][event_type] = \
                                stats["events_by_type"].get(event_type, 0) + 1
                        except json.JSONDecodeError:
                            continue
            except IOError:
                pass
        
        return stats
    
    def verify_integrity(self, file_path: str) -> Dict[str, Any]:
        """
        Verify a file's integrity against stored hash.
        
        Returns:
            Dict with 'valid', 'stored_hash', 'current_hash', 'message'
        """
        stored_hash = self._file_hashes.get(file_path)
        current_hash = self._compute_file_hash(file_path)
        
        if not stored_hash:
            return {
                "valid": None,
                "stored_hash": None,
                "current_hash": current_hash,
                "message": "No stored hash found for this file"
            }
        
        if not current_hash:
            return {
                "valid": False,
                "stored_hash": stored_hash,
                "current_hash": None,
                "message": "File not found or unreadable"
            }
        
        valid = stored_hash == current_hash
        return {
            "valid": valid,
            "stored_hash": stored_hash,
            "current_hash": current_hash,
            "message": "File integrity verified" if valid else "FILE MODIFIED WITHOUT LOGGING"
        }


# ==============================================================================
# CLI INTERFACE
# ==============================================================================

def main():
    """CLI interface for change tracker."""
    import argparse
    
    parser = argparse.ArgumentParser(description="RICK Change Tracker v3.0")
    parser.add_argument("--stats", action="store_true", help="Show tracking statistics")
    parser.add_argument("--recent", type=int, default=0, help="Show N recent changes")
    parser.add_argument("--history", type=str, help="Show history for a file")
    parser.add_argument("--verify", type=str, help="Verify integrity of a file")
    parser.add_argument("--log", type=str, help="Log a modification (requires --pin)")
    parser.add_argument("--pin", type=int, help="Auth PIN for logging")
    parser.add_argument("--description", type=str, help="Description for log entry")
    
    args = parser.parse_args()
    
    tracker = ChangeTracker()
    
    if args.stats:
        stats = tracker.get_stats()
        print(json.dumps(stats, indent=2))
        
    elif args.recent > 0:
        changes = tracker.get_recent_changes(args.recent)
        for change in changes:
            print(json.dumps(change))
            
    elif args.history:
        history = tracker.get_file_history(args.history)
        for record in history:
            print(json.dumps(record))
            
    elif args.verify:
        result = tracker.verify_integrity(args.verify)
        print(json.dumps(result, indent=2))
        
    elif args.log:
        if not args.pin:
            print("ERROR: --pin required for logging", file=sys.stderr)
            sys.exit(1)
        
        success = tracker.log_modification(
            file_path=args.log,
            auth_pin=args.pin,
            description=args.description
        )
        
        if success:
            print(f"✅ Logged modification: {args.log}")
        else:
            print("❌ Failed to log (invalid PIN?)", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
