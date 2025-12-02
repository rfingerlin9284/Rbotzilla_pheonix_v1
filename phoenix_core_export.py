#!/usr/bin/env python3
"""
phoenix_core_export.py

Generate a single-file core export PHOENIX_CORE_EXPORT_FOR_GEMINI.md
from the RICK_PHOENIX repo by selecting canonical, active core modules.

Rules enforced: NO changes to the repository. All output in PHOENIX_EXPORT/
"""
from __future__ import annotations
import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

ROOT = Path(os.getcwd())
EXPORT_DIR = ROOT / "PHOENIX_EXPORT"
EXPORT_FILE = EXPORT_DIR / "PHOENIX_CORE_EXPORT_FOR_GEMINI.md"
TASK_LOG = EXPORT_DIR / "PHOENIX_TASK_LOG.md"
PART2_FILE = EXPORT_DIR / "PHOENIX_CORE_EXPORT_FOR_GEMINI_PART2.md"

IGNORE_PATTERNS = [
    r"^tmp", r"/tmp", r"\.log$", r"\.pid$", r"\.tar", r"\.zip$", r"\.gpg$",
    r"\.bak", r"BACKUP", r"archive", r"archived_simulations", r"_legacy", r"_archive", r"sent_to_windows_files_and_folders",
]

PRIORITY_CATEGORIES = {
    "charters": ["charter", "CHARTER", "IMMUTABLE", "CHARTER"],
    "engines": ["engine", "engines", "trading_engine", "unified_engine", "rbotzilla"],
    "brokers": ["oanda", "ibkr", "coinbase", "broker", "connector"],
    "strategies_and_wolfpacks": ["strategy", "wolf_pack", "wolfpack", "rbot", "research_strategies"],
    "risk_and_gates": ["risk", "execution_gate", "position_manager", "micro_trade_filter", "capital_manager"],
    "rick_and_hive": ["hive", "rick", "hive_mind", "hive_mind_bridge", "hive_position_advisor"],
    "diagnostics": ["verify_130", "verify_", "test_", "diagnos", "validate_system", "verify"],
}

# Files to automatically prefer as 'canonical' (common well-named entrypoints)
ENTRYPOINT_NAMES = [
    "run_autonomous.py", "run_autonomous_full.py", "ignite_phoenix.py", "start_trading.sh", "start_full_system.sh",
    "trading_engine.py", "paper_trading_engine.py", "multi_broker_engine.py", "rbotzilla_engine.py", "launch_smart.sh"
]

def is_ignored(path: Path) -> bool:
    s = str(path)
    for patt in IGNORE_PATTERNS:
        if re.search(patt, s, re.I):
            return True
    # skip hidden venv or .git
    if "/.venv" in s or "site-packages" in s or "/.git/" in s:
        return True
    return False

def load_manifest(name: str) -> List[str]:
    try:
        with open(ROOT / name, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Some manifests are dicts mapping name->true
                return list(data.keys())
    except Exception:
        return []
    return []

def category_for_path(path: str) -> str:
    lower = path.lower()
    for cat, keys in PRIORITY_CATEGORIES.items():
        for k in keys:
            if k in lower:
                return cat
    return "others"

def score_file(path: Path, active_manifest: List[str], legacy_manifest: List[str]) -> float:
    score = 0.0
    s = str(path)
    p = s.lower()
    # Bad patterns reduce score
    if p.endswith('.pyc') or p.endswith('.jsonl'):
        score -= 100
    # prefer entrypoints
    if os.path.basename(s) in ENTRYPOINT_NAMES:
        score += 50
    # older vs newer
    try:
        m = path.stat().st_mtime
        age_bonus = (m / (24 * 3600)) % 1000
        score += age_bonus * 0.01
    except Exception:
        score += 0
    # manifest boosts
    if any(Path(x).name == Path(s).name for x in active_manifest):
        score += 50
    if any(Path(x).name == Path(s).name for x in legacy_manifest):
        score -= 50
    # penalize backups
    if re.search(r"\.bak|backup|OLD|DEPRECATED|proto|\.broken|\.before|\.backup", s, re.I):
        score -= 40
    # penalize huge binary / data files with certain extensions
    if re.search(r"\.tar|\.gz|\.zip|\.bin|\.db|\.tgz", s, re.I):
        score -= 200
    # filenames with 'test' are allowed but lower priority
    if re.search(r"test_", s, re.I):
        score -= 5
    # prefer python files
    if s.endswith('.py'):
        score += 10
    if s.endswith('.md'):
        score += 5
    return score

def collect_files(root: Path, include_tests: bool) -> List[Path]:
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        pdir = Path(dirpath)
        if is_ignored(pdir):
            continue
        for fname in filenames:
            fp = pdir / fname
            if is_ignored(fp):
                continue
            # ignore compiled
            if fp.suffix in ['.pyc', '.pkl', '.bin', '.tar', '.gz', '.zip', '.db']:
                continue
            # skip tests by default unless include_tests
            if not include_tests and re.match(r"test_.*|.*_test.*", fname, re.I):
                continue
            files.append(fp)
    return files

def pick_canonical(files: List[Path], active_manifest: List[str], legacy_manifest: List[str]) -> Dict[str, List[Path]]:
    buckets: Dict[str, List[Tuple[Path, float]]] = {}
    for fp in files:
        cat = category_for_path(str(fp))
        buckets.setdefault(cat, []).append((fp, score_file(fp, active_manifest, legacy_manifest)))
    canonical: Dict[str, List[Path]] = {}
    for cat, items in buckets.items():
        items.sort(key=lambda x: x[1], reverse=True)
        selected = []
        seen_names = set()
        for fp, score in items:
            # Avoid duplicates with same base name
            name = fp.name
            if name in seen_names:
                continue
            # skip backup-looking files
            if re.search(r"\.bak|backup|OLD|DEPRECATED|proto|\.before|\.backup", str(fp), re.I):
                continue
            seen_names.add(name)
            selected.append(fp)
            # For certain categories we prefer a small selection
            if cat in ['charters', 'brokers', 'risk_and_gates', 'rick_and_hive'] and len(selected) >= 5:
                break
            if cat in ['engines'] and len(selected) >= 8:
                break
        canonical[cat] = selected
    return canonical

def read_file_safe(fp: Path, max_bytes: int = 1024 * 200) -> Tuple[str, bool]:
    """Return content and a boolean whether it was truncated (True if truncated)."""
    try:
        size = fp.stat().st_size
        with open(fp, 'r', errors='replace') as f:
            if size <= max_bytes:
                return f.read(), False
            else:
                # read first chunk and note truncation
                data = f.read(max_bytes)
                return data, True
    except Exception as e:
        return f"# ERROR reading {fp}: {e}\n", False

def write_md_export(canonical: Dict[str, List[Path]], task_log_entries: List[str], include_tests: bool):
    EXPORT_DIR.mkdir(exist_ok=True)
    toc = []
    with open(EXPORT_FILE, 'w', encoding='utf-8') as out:
        out.write(f"# PHOENIX CORE EXPORT (RICK_PHOENIX)\n\n")
        out.write(f"- GENERATED BY: phoenix_core_export.py ({os.name})\n")
        out.write(f"- GENERATED AT: {datetime.utcnow().isoformat()}Z\n")
        out.write("- PURPOSE: Single-file export of the active, canonical source required to understand and rebuild the trading system.\n\n")
        out.write("## 0. SYSTEM OVERVIEW\n")
        out.write("- Brokers: OANDA, IBKR, Coinbase\n")
        out.write("- Modes: PAPER vs LIVE, Safe Mode / Ghost mode\n")
        out.write("- RICK & HIVE: control plane & brain logic\n\n")
        out.write("NOTE: This export ignores backups and legacy files. See selection log at the bottom.\n\n")
        # Sections
        idx = 1
        for category, paths in canonical.items():
            if not paths:
                continue
            out.write(f"## {idx}. {category.replace('_', ' ').upper()}\n\n")
            for i, fp in enumerate(paths, start=1):
                rel = fp.relative_to(ROOT)
                stat = fp.stat()
                score = 0
                out.write(f"### {idx}.{i} [{rel}] - {stat.st_size} bytes\n")
                out.write(f"- path: {rel}\n")
                out.write(f"- mtime: {datetime.utcfromtimestamp(stat.st_mtime).isoformat()}Z\n")
                out.write(f"- reason: selected by score / heuristics\n\n")
                if fp.suffix.lower() in ['.py']:
                    content, truncated = read_file_safe(fp, max_bytes=1024 * 500)
                    out.write("```python\n")
                    out.write(content)
                    if truncated:
                        out.write("\n# ... FILE TRUNCATED FOR EXPORT (too large) ...\n")
                    out.write("\n```\n\n")
                elif fp.suffix.lower() in ['.md', '.txt']:
                    content, truncated = read_file_safe(fp, max_bytes=1024 * 500)
                    out.write("```text\n")
                    out.write(content)
                    if truncated:
                        out.write("\n# ... FILE TRUNCATED FOR EXPORT (too large) ...\n")
                    out.write("\n```\n\n")
                else:
                    content, truncated = read_file_safe(fp, max_bytes=1024 * 100)
                    out.write("```text\n")
                    out.write(content)
                    if truncated:
                        out.write("\n# ... FILE TRUNCATED FOR EXPORT (too large) ...\n")
                    out.write("\n```\n\n")
            idx += 1
        # Selection log
        out.write("## 8. SELECTION LOG (INCLUSIONS & EXCLUSIONS)\n\n")
        for e in task_log_entries:
            out.write(f"- {e}\n")
    # Write task log separately
    with open(TASK_LOG, 'a', encoding='utf-8') as t:
        t.write(f"# Phoenix Core Export run: {datetime.utcnow().isoformat()}Z\n")
        for e in task_log_entries:
            t.write(f"- {e}\n")
        t.write('\n')

def create_selection_log(canonical: Dict[str, List[Path]], considered: List[Path], excluded: List[Tuple[Path, str]]) -> List[str]:
    entries = []
    entries.append(f"Files scanned: {len(considered)}")
    total_selected = sum(len(v) for v in canonical.values())
    entries.append(f"Total canonical selected: {total_selected}")
    for cat, lst in canonical.items():
        entries.append(f"Category {cat}: {len(lst)} selected")
    entries.append("Duplication & exclusion list (some examples):")
    for fp, reason in excluded[:50]:
        entries.append(f"EXCLUDED {fp.relative_to(ROOT)} -> {reason}")
    return entries

def main(argv=None):
    parser = argparse.ArgumentParser(description='Phoenix core export generator')
    parser.add_argument('--include-tests', action='store_true', help='Include test files in the scan')
    parser.add_argument('--limit-cat', type=int, default=10, help='Limit selection per category (default 10)')
    args = parser.parse_args(argv)
    include_tests = args.include_tests

    active_manifest = load_manifest('manifest_active.json')
    legacy_manifest = load_manifest('manifest_legacy.json')

    files = collect_files(ROOT, include_tests)
    considered = [p for p in files if p.suffix]
    canonical = pick_canonical(files, active_manifest, legacy_manifest)

    excluded = []
    # Build excluded list by checking low-scored files
    for p in files:
        if p not in sum(canonical.values(), []):
            excluded.append((p, 'not canonical based on heuristics / backup / legacy'))

    # Now limit per category
    for cat, lst in canonical.items():
        canonical[cat] = lst[:args.limit_cat]

    task_log = create_selection_log(canonical, considered, excluded)
    write_md_export(canonical, task_log, include_tests)
    print('Export created at:', EXPORT_FILE)
    print('Task log at:', TASK_LOG)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error:', e)
        sys.exit(2)
