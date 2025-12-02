#!/usr/bin/env python3
"""Simple tests for pin_protection non-interactive features."""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pin_protection import PINProtection

def test_validate_pin():
    pp = PINProtection()
    assert pp.validate_pin_noninteractive('841921') is True
    assert pp.validate_pin_noninteractive('123456') is False
    print('PASS validate_pin_noninteractive')

def test_discover_critical_files():
    pp = PINProtection()
    files = pp.discover_critical_files()
    assert isinstance(files, list)
    assert all(f.endswith('.py') for f in files)
    print('PASS discover_critical_files')

if __name__ == '__main__':
    test_validate_pin()
    test_discover_critical_files()
    print('All pin protection tests PASSED')
