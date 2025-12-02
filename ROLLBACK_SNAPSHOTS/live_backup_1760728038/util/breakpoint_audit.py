"""
Breakpoint Audit Logger
-----------------------
Captures structured BREAKPOINT events (and key engine lifecycle logs) into a JSONL file
for permanent pre-live trace mapping.

Usage:
    from util.breakpoint_audit import attach_audit_handler, audit_event
    attach_audit_handler(engine_mode="CANARY")
    audit_event("SESSION_START", {"mode": "CANARY"})
"""

from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path("/home/ing/RICK/RICK_LIVE_CLEAN")
LOGS_DIR = PROJECT_ROOT / "pre_upgrade" / "headless" / "logs"
TRACE_FILE = LOGS_DIR / "pre_live_trace.jsonl"

LOGS_DIR.mkdir(parents=True, exist_ok=True)

class _JsonlAuditHandler(logging.Handler):
    def __init__(self, engine_mode: str = "UNKNOWN"):
        super().__init__(level=logging.INFO)
        self.engine_mode = engine_mode
        self.file = TRACE_FILE

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = record.getMessage()
            event_type = None

            # Derive event type
            if "BREAKPOINT" in msg:
                # Extract label text after BREAKPOINT
                event_type = "BREAKPOINT"
            elif any(k in msg for k in ("CANARY MODE", "CHARTER-COMPLIANT GHOST")):
                event_type = "ENGINE_BANNER"

            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "engine_mode": self.engine_mode,
                "message": msg,
                "event_type": event_type or "LOG"
            }

            with open(self.file, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload) + "\n")
        except Exception:
            # Never raise from audit path
            pass


_attached = False

def attach_audit_handler(engine_mode: str = "UNKNOWN") -> None:
    """Attach the JSONL audit handler to root logging once."""
    global _attached
    if _attached:
        return
    handler = _JsonlAuditHandler(engine_mode=engine_mode)
    logging.getLogger().addHandler(handler)
    _attached = True


def audit_event(kind: str, details: Dict[str, Any] | None = None, engine_mode: str = "UNKNOWN") -> None:
    """Write a structured audit event directly to the JSONL trace."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": kind,
        "engine_mode": engine_mode,
        "details": details or {}
    }
    try:
        with open(TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass
