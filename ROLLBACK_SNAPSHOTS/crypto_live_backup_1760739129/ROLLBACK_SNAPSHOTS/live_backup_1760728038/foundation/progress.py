#!/usr/bin/env python3
"""
Progress Manager - RBOTzilla UNI Phase 3
Phase progression tracker with atomic updates.
PIN: 841921 | Generated: 2025-09-26
"""

import json
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

try:
    from .rick_charter import RickCharter
except ImportError:
    from rick_charter import RickCharter

class PhaseStatus(Enum):
    """Phase status enumeration"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS" 
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    LOCKED = "LOCKED"

@dataclass
class PhaseInfo:
    """Phase information structure"""
    phase_id: str
    status: PhaseStatus
    start_time: Optional[str] = None
    complete_time: Optional[str] = None
    progress_pct: float = 0.0
    artifacts: List[str] = None
    errors: List[str] = None

class ProgressManager:
    """
    Atomic progress tracking for RBOTzilla UNI phases
    Integrates with change tracker for audit trail
    """
    
    def __init__(self, progress_file: str = None, pin: int = None):
        """Initialize progress manager"""
        self.progress_file = Path(progress_file or "progress.json")
        self.progress_full_file = Path(str(self.progress_file).replace(".json", "_full.json"))
        
        # Validate PIN
        if pin and not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid PIN for progress manager access")
        
        self.pin_verified = pin == RickCharter.PIN if pin else False
        
        # Initialize progress if needed
        self._initialize_progress()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _get_timestamp(self) -> str:
        """Get UTC timestamp in ISO format"""
        return datetime.now(timezone.utc).isoformat()
    
    def _initialize_progress(self):
        """Initialize progress files if they don't exist"""
        if not self.progress_file.exists():
            initial_progress = {
                "phase": "init",
                "status": "PENDING",
                "pct": 0.0,
                "phases": {
                    "11": "PENDING",  # Phase 1
                    "12": "PENDING",  # Phase 2  
                    "13": "PENDING",  # Phase 3
                    "14": "PENDING",  # Phase 4
                    "15": "PENDING",  # Phase 5
                    "16": "PENDING",  # Phase 6
                    "17": "PENDING",  # Phase 7
                    "18": "PENDING"   # Phase 8
                },
                "timestamp": self._get_timestamp(),
                "initialized_by": "progress_manager"
            }
            self._atomic_write(self.progress_file, initial_progress)
        
        if not self.progress_full_file.exists():
            full_progress = {
                "system": "RBOTzilla_UNI",
                "version": "2.0",
                "pin_required": RickCharter.PIN,
                "phases": {},
                "history": [],
                "created": self._get_timestamp(),
                "last_updated": self._get_timestamp()
            }
            self._atomic_write(self.progress_full_file, full_progress)
    
    def _atomic_write(self, file_path: Path, data: Dict[str, Any]):
        """Atomic write to prevent corruption"""
        temp_file = file_path.with_suffix(f"{file_path.suffix}.tmp")
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_file.replace(file_path)
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise e
    
    def _load_progress(self) -> Dict[str, Any]:
        """Load current progress"""
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load progress: {e}")
            return {}
    
    def _load_full_progress(self) -> Dict[str, Any]:
        """Load full progress history"""
        try:
            with open(self.progress_full_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load full progress: {e}")
            return {}
    
    def start_phase(self, phase: str, pin: int = None) -> bool:
        """Start a new phase"""
        if pin and not RickCharter.validate_pin(pin):
            self.logger.error("Invalid PIN for phase start")
            return False
        
        try:
            progress = self._load_progress()
            full_progress = self._load_full_progress()
            
            timestamp = self._get_timestamp()
            
            # Update main progress
            progress["phase"] = phase
            progress["status"] = "IN_PROGRESS"
            progress["timestamp"] = timestamp
            
            # Update phase status
            phase_key = f"1{phase}"  # Convert to phase key format
            if phase_key in progress["phases"]:
                progress["phases"][phase_key] = "IN_PROGRESS"
            
            # Update full progress
            full_progress["phases"][phase] = {
                "status": "IN_PROGRESS",
                "start_time": timestamp,
                "pin_verified": bool(pin),
                "artifacts": [],
                "events": []
            }
            full_progress["last_updated"] = timestamp
            
            # Add to history
            full_progress["history"].append({
                "action": "phase_start",
                "phase": phase,
                "timestamp": timestamp,
                "pin_verified": bool(pin)
            })
            
            # Atomic writes
            self._atomic_write(self.progress_file, progress)
            self._atomic_write(self.progress_full_file, full_progress)
            
            self.logger.info(f"Phase {phase} started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start phase {phase}: {e}")
            return False
    
    def complete_phase(self, phase: str, artifacts: List[str] = None, pin: int = None) -> bool:
        """Complete a phase"""
        if pin and not RickCharter.validate_pin(pin):
            self.logger.error("Invalid PIN for phase completion")
            return False
        
        try:
            progress = self._load_progress()
            full_progress = self._load_full_progress()
            
            timestamp = self._get_timestamp()
            artifacts = artifacts or []
            
            # Calculate progress percentage
            completed_phases = sum(1 for status in progress["phases"].values() if status == "COMPLETE")
            total_phases = len(progress["phases"])
            progress_pct = (completed_phases + 1) * 100.0 / total_phases
            
            # Update main progress
            progress["phase"] = phase
            progress["status"] = "COMPLETE"
            progress["pct"] = progress_pct
            progress["timestamp"] = timestamp
            
            # Update phase status
            phase_key = f"1{phase}"  # Convert to phase key format
            if phase_key in progress["phases"]:
                progress["phases"][phase_key] = "COMPLETE"
            
            # Add artifacts if any
            if artifacts:
                if "locked_files" not in progress:
                    progress["locked_files"] = []
                if "locked_dirs" not in progress:
                    progress["locked_dirs"] = []
                progress["artifacts"] = artifacts
            
            # Update full progress
            if phase in full_progress["phases"]:
                full_progress["phases"][phase].update({
                    "status": "COMPLETE",
                    "complete_time": timestamp,
                    "progress_pct": progress_pct,
                    "artifacts": artifacts
                })
            else:
                full_progress["phases"][phase] = {
                    "status": "COMPLETE",
                    "complete_time": timestamp,
                    "progress_pct": progress_pct,
                    "artifacts": artifacts,
                    "pin_verified": bool(pin)
                }
            
            full_progress["last_updated"] = timestamp
            
            # Add to history
            full_progress["history"].append({
                "action": "phase_complete",
                "phase": phase,
                "timestamp": timestamp,
                "progress_pct": progress_pct,
                "artifacts": artifacts,
                "pin_verified": bool(pin)
            })
            
            # Atomic writes
            self._atomic_write(self.progress_file, progress)
            self._atomic_write(self.progress_full_file, full_progress)
            
            self.logger.info(f"Phase {phase} completed successfully ({progress_pct:.1f}%)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete phase {phase}: {e}")
            return False
    
    def add_artifact(self, phase: str, artifact: str, pin: int = None) -> bool:
        """Add artifact to phase"""
        if pin and not RickCharter.validate_pin(pin):
            return False
        
        try:
            full_progress = self._load_full_progress()
            
            if phase in full_progress["phases"]:
                if "artifacts" not in full_progress["phases"][phase]:
                    full_progress["phases"][phase]["artifacts"] = []
                
                if artifact not in full_progress["phases"][phase]["artifacts"]:
                    full_progress["phases"][phase]["artifacts"].append(artifact)
                    full_progress["last_updated"] = self._get_timestamp()
                    
                    self._atomic_write(self.progress_full_file, full_progress)
                    self.logger.info(f"Artifact '{artifact}' added to phase {phase}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to add artifact to phase {phase}: {e}")
            return False
    
    def get_current_phase(self) -> Optional[str]:
        """Get current active phase"""
        try:
            progress = self._load_progress()
            return progress.get("phase")
        except:
            return None
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get progress summary"""
        try:
            progress = self._load_progress()
            full_progress = self._load_full_progress()
            
            completed = sum(1 for status in progress["phases"].values() if status == "COMPLETE")
            total = len(progress["phases"])
            
            return {
                "current_phase": progress.get("phase", "unknown"),
                "current_status": progress.get("status", "unknown"),
                "progress_pct": progress.get("pct", 0.0),
                "completed_phases": completed,
                "total_phases": total,
                "phases": progress.get("phases", {}),
                "last_updated": progress.get("timestamp", "unknown"),
                "total_artifacts": sum(
                    len(phase_info.get("artifacts", [])) 
                    for phase_info in full_progress.get("phases", {}).values()
                )
            }
        except Exception as e:
            self.logger.error(f"Failed to get progress summary: {e}")
            return {"error": str(e)}
    
    def validate_phase_sequence(self) -> bool:
        """Validate phase sequence integrity"""
        try:
            progress = self._load_progress()
            phases = progress.get("phases", {})
            
            # Check that phases are completed in order
            phase_order = ["11", "12", "13", "14", "15", "16", "17", "18"]
            last_complete = None
            
            for phase in phase_order:
                status = phases.get(phase, "PENDING")
                if status == "COMPLETE":
                    last_complete = phase
                elif status == "IN_PROGRESS" and last_complete:
                    # Current phase can be in progress if previous are complete
                    prev_phase = phase_order[phase_order.index(phase) - 1]
                    if prev_phase != last_complete:
                        return False
                elif status == "PENDING":
                    # Remaining phases should be pending
                    continue
                else:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Phase sequence validation failed: {e}")
            return False

# Module-level functions for easy access
_global_manager = None

def get_progress_manager() -> ProgressManager:
    """Get global progress manager instance"""
    global _global_manager
    if _global_manager is None:
        _global_manager = ProgressManager()
    return _global_manager

def complete_phase(phase: str, artifacts: List[str] = None, pin: int = None) -> bool:
    """Module-level phase completion function"""
    return get_progress_manager().complete_phase(phase, artifacts, pin)

def get_current_phase() -> Optional[str]:
    """Module-level current phase getter"""
    return get_progress_manager().get_current_phase()

def add_artifact(phase: str, artifact: str, pin: int = None) -> bool:
    """Module-level artifact addition"""
    return get_progress_manager().add_artifact(phase, artifact, pin)

if __name__ == "__main__":
    # Self-test
    pm = ProgressManager(pin=RickCharter.PIN)
    summary = pm.get_progress_summary()
    print(f"Progress Manager self-test: {summary.get('current_phase', 'ERROR')} ✅")