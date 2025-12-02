#!/usr/bin/env python3
"""
Create a zip snapshot of the PhoenixV2 project for pre-launch backup.
Usage: python3 scripts/create_snapshot.py
"""
import os
from pathlib import Path
import zipfile
from datetime import datetime


def should_exclude(path: Path) -> bool:
    # Ignore logs, __pycache__, and snapshots
    parts = path.parts
    if 'logs' in parts:
        return True
    if '__pycache__' in parts:
        return True
    if 'snapshots' in parts:
        return True
    return False


def create_snapshot(root: str = '.', include_env: bool = True) -> Path:
    root_path = Path(root).resolve()
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    out_dir = root_path / 'snapshots'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_name = out_dir / f"PhoenixV2_ReadyForLaunch_{ts}.zip"
    with zipfile.ZipFile(out_name, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for base, dirs, files in os.walk(root_path / 'PhoenixV2'):
            for f in files:
                full = Path(base) / f
                if should_exclude(full):
                    continue
                arcname = full.relative_to(root_path)
                zf.write(full, arcname)
        if include_env:
            env_file = root_path / '.env'
            if env_file.exists():
                zf.write(env_file, env_file.relative_to(root_path))
    return out_name


if __name__ == '__main__':
    print('Creating snapshot...')
    s = create_snapshot('.')
    print('Created snapshot:', s)
