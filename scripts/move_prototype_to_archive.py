#!/usr/bin/env python3
"""Move a prototype directory into the repo archives for cleanup.

Usage: python3 scripts/move_prototype_to_archive.py RICK_LIVE_PROTOTYPE

The script will:
- Verify the directory exists
- Create an `archives/` directory if missing
- Move the directory into `archives/NAME_TIMESTAMP` to preserve history
- Update `manifest_legacy.json` to remove the path reference (optional)
"""
import os
import sys
import shutil
import time
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ARCHIVES_DIR = os.path.join(ROOT, 'archives')

def maybe_update_manifest(name):
    manifest_path = os.path.join(ROOT, 'manifest_legacy.json')
    if not os.path.exists(manifest_path):
        return
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    except Exception:
        return
    changed = False
    if isinstance(manifest, list):
        new_manifest = [m for m in manifest if not (isinstance(m, dict) and m.get('path', '') == name + '/')]
        if len(new_manifest) != len(manifest):
            with open(manifest_path, 'w') as f:
                json.dump(new_manifest, f, indent=2)
            print(f"Updated manifest_legacy.json: removed {name}/")
            changed = True
    return changed

def main():
    if len(sys.argv) < 2:
        print('Usage: move_prototype_to_archive.py <dir_name>')
        sys.exit(1)
    name = sys.argv[1]
    src = os.path.join(ROOT, name)
    if not os.path.exists(src):
        print(f'Path not found: {src}')
        sys.exit(1)
    if not os.path.isdir(src):
        print(f'Not a directory: {src}')
        sys.exit(1)
    os.makedirs(ARCHIVES_DIR, exist_ok=True)
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    dest = os.path.join(ARCHIVES_DIR, f"{name}_{timestamp}")
    print(f'Moving {src} -> {dest}...')
    shutil.move(src, dest)
    print('Move complete.')
    updated = maybe_update_manifest(name)
    if not updated:
        print('Manifest not updated (or not present).')
    print('NOTE: You may wish to update any documentation or external references to this path.')

if __name__ == '__main__':
    main()
