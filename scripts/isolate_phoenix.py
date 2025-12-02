#!/usr/bin/env python3
"""
Safe isolation script to move legacy files into a _LEGACY_ARCHIVE_DO_NOT_RUN folder.
Dry-run by default; provide --force to actually move files.
"""
import os
import shutil
import datetime
import sys
import argparse

KEEP = {
    'PhoenixV2',
    '.env',
    'requirements.txt',
    'README.md',
    'venv',
    '.git',
    '.gitignore',
    'scripts',
    'legacy_relocate'
}

ARCHIVE_DIR = 'legacy_relocate'


def isolate(force=False, zipit=False, dest_dir=None):
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
        print(f"Created archive: {ARCHIVE_DIR}")

    dest = ARCHIVE_DIR if dest_dir is None else dest_dir
    # Ensure dest exists if --force (actual move); or ensure mention in dry-run
    items = os.listdir('.')
    moved = []
    skipped = []
    for item in items:
        # Skip whitelisted
        if item in KEEP:
            skipped.append(item)
            continue

        # Don't move this script itself
        if item == os.path.basename(__file__):
            skipped.append(item)
            continue

        # Dry-run behavior
        if not force:
            print(f"[DRY-RUN] Would move: {item} -> {dest}/{item}")
            moved.append(item)
            continue

        try:
            src = item
            dst = os.path.join(dest, item)
            if os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)
            shutil.move(src, dst)
            print(f"Moved: {item}")
            moved.append(item)
        except Exception as e:
            print(f"Failed to move {item}: {e}")

    print(f"\n✅ ISOLATION COMPLETE. Processed: {len(items)} items; Dry-run: {not force}")
    print(f"Moved: {len(moved)}; Skipped/Kept: {len(skipped)}")
    # Optionally compress the archive directory into a single zip file for easy storage
    if zipit and force and len(moved) > 0:
        ts = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        zip_name = f"legacy_relocate_{ts}"
        print(f"Creating zip: {zip_name}.zip")
        shutil.make_archive(zip_name, 'zip', root_dir=dest)
        print(f"Created zip {zip_name}.zip")


def main(argv=None):
    parser = argparse.ArgumentParser(description='Isolate everything except PhoenixV2 and a small whitelist into an archive folder.')
    parser.add_argument('--force', action='store_true', help='Actually move files (default is dry-run)')
    parser.add_argument('--zip', action='store_true', dest='zipit', help='Create a timestamped zip of the relocated folder after moving')
    parser.add_argument('--dest', dest='dest_dir', default=None, help='Destination folder name (default legacy_relocate)')
    args = parser.parse_args(argv)
    isolate(force=args.force, zipit=args.zipit, dest_dir=args.dest_dir)


if __name__ == '__main__':
    main()
