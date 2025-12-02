#!/usr/bin/env python3
from util.confidence import normalize_confidence, format_confidence, is_confidence_above

def test_normalize_confidence_decimal():
    assert normalize_confidence(0.093) == 0.093
    assert normalize_confidence(1.0) == 1.0
    assert normalize_confidence(0) == 0.0

def test_normalize_confidence_percent():
    assert round(normalize_confidence(9.3), 6) == 0.093
    assert round(normalize_confidence(93), 6) == 0.93

def test_format_confidence():
    assert format_confidence(0.093) == '9.3%'
    assert format_confidence(0.93) == '93.0%'
    assert format_confidence(9.3) == '9.3%'

def test_is_confidence_above():
    assert is_confidence_above(0.6, 0.5)
    assert is_confidence_above(60, 0.5)
    assert not is_confidence_above(0.4, 0.5)

if __name__ == '__main__':
    test_normalize_confidence_decimal()
    test_normalize_confidence_percent()
    test_format_confidence()
    test_is_confidence_above()
    print('All confidence util tests passed')
