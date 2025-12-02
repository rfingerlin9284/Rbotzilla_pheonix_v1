"""Small JSON-structured logger used across the project.

Provides a lightweight logger that writes newline-delimited JSON to stdout and
optionally to a per-run file under an artifacts directory.
"""
import json
import sys
import os
import time
from typing import Optional, Dict, Any


class Logger:
    def __init__(self, run_id: Optional[str] = None, out_dir: Optional[str] = None, module: Optional[str] = None):
        self.run_id = run_id
        self.out_dir = out_dir
        self.module = module
        self._file = None
        if out_dir and run_id:
            try:
                os.makedirs(os.path.join(out_dir, run_id), exist_ok=True)
                self._file = open(os.path.join(out_dir, run_id, "logs.jsonl"), "a", encoding="utf-8")
            except Exception:
                self._file = None

    def _write(self, level: str, msg: str, ctx: Optional[Dict[str, Any]] = None):
        entry = {
            "ts": time.time(),
            "level": level,
            "run_id": self.run_id,
            "module": self.module,
            "msg": msg,
            "ctx": ctx or {},
        }
        line = json.dumps(entry, default=str, separators=(',', ':'))
        # stdout
        print(line, file=sys.stdout)
        sys.stdout.flush()
        # file
        if self._file:
            try:
                self._file.write(line + "\n")
                self._file.flush()
            except Exception:
                pass

    def info(self, msg: str, ctx: Optional[Dict[str, Any]] = None):
        self._write("INFO", msg, ctx)

    def error(self, msg: str, ctx: Optional[Dict[str, Any]] = None):
        self._write("ERROR", msg, ctx)

    def debug(self, msg: str, ctx: Optional[Dict[str, Any]] = None):
        self._write("DEBUG", msg, ctx)


def get_logger(run_id: Optional[str] = None, out_dir: Optional[str] = None, module: Optional[str] = None) -> Logger:
    return Logger(run_id=run_id, out_dir=out_dir, module=module)
