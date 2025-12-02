#!/usr/bin/env python3
import math
from datetime import datetime, timedelta
from util.trailing_engine import PositionSnapshot, compute_trailing_sl


def test_trailing_sl_ladder_long():
    now = datetime.now()
    pos = PositionSnapshot(
        symbol='EUR_USD',
        direction='LONG',
        entry_price=1.1000,
        current_price=1.1320,  # ~3R if R ~ 0.01
        initial_sl=1.0900,
        current_sl=1.0900,
        open_time=now - timedelta(hours=1),
        now=now,
        last_swing_price=1.0890,
        last_liquidity_level=1.0890,
        atr_value=0.0100,
        rr_initial=3.2,
    )
    pip = 0.0001
    new_sl = compute_trailing_sl(pos, pip)
    # Should have tightened to at least 2R locked (since current_price ~ 3.2R)
    assert new_sl > pos.current_sl


def test_trailing_sl_no_action_if_below_1r():
    now = datetime.now()
    pos = PositionSnapshot(
        symbol='EUR_USD',
        direction='LONG',
        entry_price=1.1000,
        current_price=1.1010,  # ~0.1R if R ~ 0.01
        initial_sl=1.0900,
        current_sl=1.0900,
        open_time=now - timedelta(hours=0.5),
        now=now,
        last_swing_price=1.0890,
        last_liquidity_level=1.0890,
        atr_value=0.0100,
        rr_initial=3.2,
    )
    pip = 0.0001
    new_sl = compute_trailing_sl(pos, pip)
    assert new_sl == pos.current_sl


def test_trailing_min_tightening_threshold():
    now = datetime.now()
    pos = PositionSnapshot(
        symbol='EUR_USD',
        direction='LONG',
        entry_price=1.1000,
        current_price=1.1100,  # profit about 1R
        initial_sl=1.0900,
        current_sl=1.0895,
        open_time=now - timedelta(hours=1),
        now=now,
        last_swing_price=1.0890,
        last_liquidity_level=1.0890,
        atr_value=0.0100,
        rr_initial=3.2,
    )
    pip = 0.0001
    # current_sl is 1.0895, initial_sl 1.09, so only 0.5 pip tighten available; min_tightening_pips default is 1 -> no change
    new_sl = compute_trailing_sl(pos, pip)
    assert new_sl == pos.current_sl


def test_trailing_time_soft_tightening():
    now = datetime.now()
    pos = PositionSnapshot(
        symbol='EUR_USD',
        direction='LONG',
        entry_price=1.1000,
        current_price=1.1010,  # < 1R profit
        initial_sl=1.0900,
        current_sl=1.0900,
        open_time=now - timedelta(hours=6),
        now=now,
        last_swing_price=1.0890,
        last_liquidity_level=1.0890,
        atr_value=0.0100,
        rr_initial=3.2,
    )
    pip = 0.0001
    # aged position should be softly tightened (initial_sl + 0.2 * R)
    new_sl = compute_trailing_sl(pos, pip, time_soft_tighten_hours=4.0)
    assert new_sl > pos.current_sl


def test_trailing_sl_respects_minimum_buffer():
    now = datetime.now()
    # current price very close to a proposed tighter SL; should not tighten due to buffer
    pos = PositionSnapshot(
        symbol='EUR_USD',
        direction='LONG',
        entry_price=1.1000,
        current_price=1.1005,
        initial_sl=1.0900,
        current_sl=1.0999,
        open_time=now - timedelta(hours=1),
        now=now,
        last_swing_price=1.09995,
        last_liquidity_level=1.09995,
        atr_value=0.0005,
        rr_initial=3.2,
    )
    pip = 0.0001
    new_sl = compute_trailing_sl(pos, pip)
    assert new_sl == pos.current_sl


if __name__ == '__main__':
    test_trailing_sl_ladder_long()
    test_trailing_sl_no_action_if_below_1r()
    print('Trailing engine tests passed')
