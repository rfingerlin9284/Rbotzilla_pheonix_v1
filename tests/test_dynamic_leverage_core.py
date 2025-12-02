#!/usr/bin/env python3
import os
from util.dynamic_leverage import compute_dynamic_leverage


def test_compute_dynamic_leverage_basic():
    base = 1.0
    # mid-range approval
    lev, expl = compute_dynamic_leverage(base, approval_score=0.5, max_leverage=3.0, aggressiveness=2.0)
    assert lev >= 1.0
    assert isinstance(expl, str)
    assert 'approval_score' in expl


def test_compute_dynamic_leverage_caps():
    base = 2.0
    # Very high approval should be capped by max_leverage
    lev, expl = compute_dynamic_leverage(base, approval_score=1.0, max_leverage=3.0, aggressiveness=2.0)
    assert lev <= 3.0
    assert 'capped=True' in expl or 'capped=True' in expl


def test_compute_approval_score_env_weights(monkeypatch):
    # Set environment weights to make technical dominant
    monkeypatch.setenv('RICK_WT_TECHNICAL', '0.9')
    monkeypatch.setenv('RICK_WT_HIVE', '0.05')
    monkeypatch.setenv('RICK_WT_RR', '0.05')
    from util.dynamic_leverage import compute_approval_score
    s = compute_approval_score(technical_score=1.0, hive_confidence=0.0, ml_confidence=0.0, rick_approval=False, rr_factor=0.0)
    assert s > 0.8


def test_compute_dynamic_leverage_minimum():
    base = 1.0
    # Zero approval -> base leverage remains
    lev, expl = compute_dynamic_leverage(base, approval_score=0.0, max_leverage=5.0, aggressiveness=2.0)
    assert lev >= 1.0
    assert lev == 1.0 or lev == base


if __name__ == '__main__':
    test_compute_dynamic_leverage_basic()
    test_compute_dynamic_leverage_caps()
    test_compute_dynamic_leverage_minimum()
    print('PASS dynamic_leverage_core')
