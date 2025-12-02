#!/usr/bin/env python3
"""
RICK Change Tracker - Self-Documenting Modification Logger
============================================================
PIN: 841921 | Version: 1.0 | 2025-11-25

This module provides automatic tracking of ALL file modifications
with detailed logging, diffs, and rollback capability.

IMMUTABLE PROTOCOL:
- Every change creates a timestamped diff record
- Changes are logged to .rick_system/change_log/
- Each session creates a new timeline file
- File dependencies are tracked automatically
"""

import os
import sys
import json
import hashlib
import difflib
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ChangeType(Enum):
    """Types of changes that can occur"""
    CREATED = "CREATED"
    MODIFIED = "MODIFIED"
    DELETED = "DELETED"
    RENAMED = "RENAMED"
    EXTRACTED = "EXTRACTED"  # Code extracted from another file
    CONSOLIDATED = "CONSOLIDATED"  # Multiple files merged


@dataclass
class FileChange:
    """Record of a single file change"""
    timestamp: str
    file_path: str
    change_type: str
    line_count_before: int
    line_count_after: int
    hash_before: str
    hash_after: str
    description: str
    source_files: List[str]  # Files this was extracted from
    diff_preview: str  # First 50 lines of diff
    session_id: str
    

@dataclass
class SessionRecord:
    """Record of a development session"""
    session_id: str
    start_time: str
    end_time: Optional[str]
    changes: List[Dict]
    files_modified: List[str]
    files_created: List[str]
    files_deleted: List[str]
    total_lines_changed: int
    description: str


class RickChangeTracker:
    """
    Self-documenting change tracking system for RICK
    
    Features:
    - Automatic diff generation for all file changes
    - Session-based grouping of changes
    - Source file tracking (where code came from)
    - Rollback capability via stored snapshots
    - JSON timeline logs for debugging
    """
    
    # IMMUTABLE FOLDER STRUCTURE
    BASE_DIR = Path("/home/ing/RICK/RICK_LIVE_CLEAN/.rick_system")
    CHANGE_LOG_DIR = BASE_DIR / "change_log"
    SNAPSHOTS_DIR = BASE_DIR / "snapshots"
    DIFFS_DIR = BASE_DIR / "diffs"
    MANIFESTS_DIR = BASE_DIR / "manifests"
    
    def __init__(self):
        """Initialize the change tracker"""
        self._ensure_directories()
        self.session_id = self._generate_session_id()
        self.session_record = SessionRecord(
            session_id=self.session_id,
            start_time=datetime.now(timezone.utc).isoformat(),
            end_time=None,
            changes=[],
            files_modified=[],
            files_created=[],
            files_deleted=[],
            total_lines_changed=0,
            description=""
        )
        self._file_cache: Dict[str, str] = {}  # Path -> content before changes
        
    def _ensure_directories(self):
        """Create required directories if they don't exist"""
        for dir_path in [self.CHANGE_LOG_DIR, self.SNAPSHOTS_DIR, 
                         self.DIFFS_DIR, self.MANIFESTS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        now = datetime.now(timezone.utc)
        return f"session_{now.strftime('%Y%m%d_%H%M%S')}"
    
    def _file_hash(self, content: str) -> str:
        """Generate SHA256 hash of file content"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _count_lines(self, content: str) -> int:
        """Count lines in content"""
        return len(content.splitlines()) if content else 0
    
    def cache_file(self, file_path: str):
        """
        Cache file content BEFORE modification
        Call this before making any changes to a file
        """
        path = Path(file_path)
        if path.exists():
            try:
                self._file_cache[str(path)] = path.read_text(encoding='utf-8')
            except Exception as e:
                self._file_cache[str(path)] = f"[READ ERROR: {e}]"
        else:
            self._file_cache[str(path)] = ""
    
    def record_change(
        self,
        file_path: str,
        change_type: ChangeType,
        description: str,
        source_files: List[str] = None,
        new_content: str = None
    ) -> FileChange:
        """
        Record a file change with full documentation
        
        Args:
            file_path: Path to the changed file
            change_type: Type of change (CREATED, MODIFIED, etc.)
            description: Human-readable description of what changed
            source_files: List of files this code was extracted from
            new_content: New file content (if not reading from disk)
        
        Returns:
            FileChange record
        """
        path = Path(file_path)
        now = datetime.now(timezone.utc)
        
        # Get before content from cache
        before_content = self._file_cache.get(str(path), "")
        
        # Get after content
        if new_content is not None:
            after_content = new_content
        elif path.exists():
            try:
                after_content = path.read_text(encoding='utf-8')
            except Exception:
                after_content = ""
        else:
            after_content = ""
        
        # Generate diff
        diff_lines = list(difflib.unified_diff(
            before_content.splitlines(keepends=True),
            after_content.splitlines(keepends=True),
            fromfile=f"a/{path.name}",
            tofile=f"b/{path.name}",
            lineterm=""
        ))
        diff_text = "\n".join(diff_lines)
        diff_preview = "\n".join(diff_lines[:50]) if diff_lines else "[No changes]"
        
        # Create change record
        change = FileChange(
            timestamp=now.isoformat(),
            file_path=str(path),
            change_type=change_type.value,
            line_count_before=self._count_lines(before_content),
            line_count_after=self._count_lines(after_content),
            hash_before=self._file_hash(before_content) if before_content else "NONE",
            hash_after=self._file_hash(after_content) if after_content else "NONE",
            description=description,
            source_files=source_files or [],
            diff_preview=diff_preview,
            session_id=self.session_id
        )
        
        # Update session record
        self.session_record.changes.append(asdict(change))
        self.session_record.total_lines_changed += abs(
            change.line_count_after - change.line_count_before
        )
        
        if change_type == ChangeType.CREATED:
            self.session_record.files_created.append(str(path))
        elif change_type == ChangeType.DELETED:
            self.session_record.files_deleted.append(str(path))
        else:
            self.session_record.files_modified.append(str(path))
        
        # Save full diff to file
        diff_filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{path.name}.diff"
        diff_path = self.DIFFS_DIR / diff_filename
        diff_path.write_text(diff_text, encoding='utf-8')
        
        # Update cache with new content
        self._file_cache[str(path)] = after_content
        
        return change
    
    def save_session(self, description: str = ""):
        """
        Save the session record to disk
        Call this at the end of a development session
        """
        self.session_record.end_time = datetime.now(timezone.utc).isoformat()
        self.session_record.description = description
        
        # Save session log
        log_file = self.CHANGE_LOG_DIR / f"{self.session_id}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.session_record), f, indent=2)
        
        # Append to master timeline
        timeline_file = self.CHANGE_LOG_DIR / "TIMELINE.jsonl"
        with open(timeline_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "session_id": self.session_id,
                "timestamp": self.session_record.end_time,
                "files_count": len(self.session_record.changes),
                "description": description
            }) + "\n")
        
        print(f"✅ Session saved: {log_file}")
        return log_file
    
    def generate_manifest(self, root_dir: str, output_name: str = None) -> Path:
        """
        Generate a manifest of all active files with line counts
        
        Format: filename_LINES.ext
        """
        root = Path(root_dir)
        now = datetime.now(timezone.utc)
        
        if output_name is None:
            output_name = f"manifest_{now.strftime('%Y%m%d_%H%M%S')}.md"
        
        manifest_path = self.MANIFESTS_DIR / output_name
        
        # Collect all Python files
        files_info = []
        for py_file in root.rglob("*.py"):
            # Skip legacy, pycache, venv
            if any(skip in str(py_file) for skip in 
                   ['_legacy_code', '__pycache__', 'venv', '.git', 'L-']):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                line_count = self._count_lines(content)
                rel_path = py_file.relative_to(root)
                files_info.append({
                    'path': str(rel_path),
                    'lines': line_count,
                    'hash': self._file_hash(content),
                    'size_kb': py_file.stat().st_size / 1024
                })
            except Exception as e:
                files_info.append({
                    'path': str(py_file.relative_to(root)),
                    'lines': 0,
                    'hash': 'ERROR',
                    'error': str(e)
                })
        
        # Sort by path
        files_info.sort(key=lambda x: x['path'])
        
        # Generate markdown manifest
        manifest_content = f"""# RICK Active Files Manifest
## Generated: {now.isoformat()}
## Root: {root}
## Total Files: {len(files_info)}

---

| File Path | Lines | Size (KB) | Hash |
|-----------|-------|-----------|------|
"""
        
        total_lines = 0
        for f in files_info:
            manifest_content += f"| `{f['path']}` | {f['lines']:,} | {f.get('size_kb', 0):.1f} | {f['hash']} |\n"
            total_lines += f['lines']
        
        manifest_content += f"\n---\n\n**Total Lines:** {total_lines:,}\n"
        
        manifest_path.write_text(manifest_content, encoding='utf-8')
        
        # Also save JSON version
        json_path = self.MANIFESTS_DIR / output_name.replace('.md', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'generated': now.isoformat(),
                'root': str(root),
                'total_files': len(files_info),
                'total_lines': total_lines,
                'files': files_info
            }, f, indent=2)
        
        print(f"✅ Manifest saved: {manifest_path}")
        return manifest_path
    
    def create_snapshot(self, name: str, directories: List[str]) -> Path:
        """
        Create a frozen snapshot of specified directories
        
        Args:
            name: Snapshot name (e.g., "frozen-v2")
            directories: List of directories to snapshot
        """
        now = datetime.now(timezone.utc)
        snapshot_dir = self.SNAPSHOTS_DIR / f"{name}_{now.strftime('%Y%m%d_%H%M%S')}"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        for dir_path in directories:
            src = Path(dir_path)
            if src.exists():
                dst = snapshot_dir / src.name
                if src.is_dir():
                    shutil.copytree(src, dst, 
                                    ignore=shutil.ignore_patterns(
                                        '__pycache__', '*.pyc', '.git', 'venv'
                                    ))
                else:
                    shutil.copy2(src, dst)
        
        # Create snapshot metadata
        meta = {
            'name': name,
            'created': now.isoformat(),
            'directories': directories,
            'snapshot_path': str(snapshot_dir)
        }
        
        meta_file = snapshot_dir / 'SNAPSHOT_META.json'
        with open(meta_file, 'w') as f:
            json.dump(meta, f, indent=2)
        
        print(f"✅ Snapshot created: {snapshot_dir}")
        return snapshot_dir


# ============================================================================
# CONVENIENCE FUNCTIONS FOR QUICK USAGE
# ============================================================================

_tracker: Optional[RickChangeTracker] = None

def get_tracker() -> RickChangeTracker:
    """Get or create the global tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = RickChangeTracker()
    return _tracker

def log_change(file_path: str, change_type: str, description: str, 
               source_files: List[str] = None):
    """Quick function to log a change"""
    tracker = get_tracker()
    tracker.cache_file(file_path)
    return tracker.record_change(
        file_path=file_path,
        change_type=ChangeType(change_type),
        description=description,
        source_files=source_files
    )

def save_session(description: str = ""):
    """Quick function to save current session"""
    tracker = get_tracker()
    return tracker.save_session(description)

def create_manifest(root_dir: str = "/home/ing/RICK/RICK_LIVE_CLEAN/rick_clean_live"):
    """Quick function to create a manifest"""
    tracker = get_tracker()
    return tracker.generate_manifest(root_dir)


if __name__ == "__main__":
    # Demo usage
    tracker = RickChangeTracker()
    
    print("📊 RICK Change Tracker Initialized")
    print(f"   Session ID: {tracker.session_id}")
    print(f"   Log Directory: {tracker.CHANGE_LOG_DIR}")
    print(f"   Diffs Directory: {tracker.DIFFS_DIR}")
    
    # Generate manifest
    manifest = tracker.generate_manifest("/home/ing/RICK/RICK_LIVE_CLEAN/rick_clean_live")
    print(f"\n✅ Manifest generated: {manifest}")
