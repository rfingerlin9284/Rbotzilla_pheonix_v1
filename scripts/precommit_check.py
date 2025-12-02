#!/usr/bin/env python3
"""Run repository safety checks used in pre-commit.

This script runs detection for any direct .place_order usage that bypasses
`safe_place_order` and fails with exit code 1 if any are found.
"""
import sys
from scripts.detect_unsafe_place_order import scan

def main():
    results = scan()
    if results:
        print('Unsafe .place_order occurrences detected:')
        for p, line, snippet in results:
            print(f"  {p}:{line} -> {snippet}")
        sys.exit(1)
    print('No unsafe .place_order occurrences found (safe to commit).')

if __name__ == '__main__':
    main()
