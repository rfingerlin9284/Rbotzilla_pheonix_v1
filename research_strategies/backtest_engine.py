from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import statistics
from util.execution_gate import can_place_order, set_risk_manager
from util.risk_manager import RiskManager
from util.trailing_engine import compute_trailing_sl, PositionSnapshot
from datetime import datetime, timezone
import pandas as pd


@dataclass
class BacktestConfig:
    initial_equity: float = 10000.0
    pip_value: float = 0.0001
    slippage: float = 0.0
    commission_pct: float = 0.0002
    timeframe: str = "M15"


@dataclass
class BacktestResult:
    trades: List[Dict[str, Any]]
    equity_curve: List[float]
    metrics: Dict[str, Any]


def apply_signals(df, signals: List[Dict[str, Any]]):
    # super naive backtest: every signal becomes a market entry at 'entry' then exit 1R later
    trades = []
    for s in signals:
        entry = s.get('entry')
        if entry is None:
            continue
        stop = s.get('stop')
        tp = s.get('take') or s.get('tp')
        # default to naive 1R stop and 3.2R take
        if stop is None:
            stop = entry - 0.01 if s['side'] == 'BUY' else entry + 0.01
        if tp is None:
            tp = entry + 0.032 if s['side'] == 'BUY' else entry - 0.032
        side = s.get('side') or s.get('direction') or s.get('direction')
        # attach timestamp if missing: default to last available time
        ts = s.get('timestamp', None)
        if ts is None and df is not None and 'time' in df.columns:
            try:
                ts = df['time'].iloc[-1]
            except Exception:
                ts = None
        trades.append({
            'entry': entry,
            'stop': stop,
            'tp': tp,
            'side': side,
            'timestamp': ts,
            'strategy': s.get('strategy'),
            'pack': s.get('pack'),
            'asset_class': s.get('asset_class'),
            'effective_risk_pct': s.get('effective_risk_pct'),
            'tps': s.get('tps'),
            'atr': s.get('atr'),
            'last_swing_price': s.get('last_swing_price'),
            'last_liquidity_level': s.get('last_liquidity_level'),
        })
    return trades


def compute_metrics(trades: List[Dict[str, Any]]):
    if not trades:
        return { 'cagr': 0, 'sharpe': 0, 'max_dd': 0 }
    # fake metrics
    pnl_list = [((t['tp'] - t['entry']) if t['side'] == 'BUY' else (t['entry'] - t['tp'])) * 1000 for t in trades]
    total = sum(pnl_list)
    returns = [p / 1000 for p in pnl_list]
    mean_r = statistics.mean(returns) if returns else 0
    sd = statistics.pstdev(returns) if len(returns) > 1 else 0.0001
    sharpe = mean_r / sd if sd else 0
    max_dd = max(0.1, abs(min(returns)))
    cagr = (1 + mean_r) ** (1/1) - 1
    return {'cagr': cagr, 'sharpe': sharpe, 'max_dd': max_dd}


def simulate_trades(trades: List[Dict[str, Any]], initial_equity: float = 10000.0, risk_manager: RiskManager | None = None, slippage: float = 0.0001, commission_pct: float = 0.0002):
    """Simulate trades sequentially and update risk_manager; returns equity history and final metrics.

    This is a naive sequential simulation: assume each trade occurs at market with given entry/stop/tp and is resolved on next bar (i.e., no partial fills).
    The PnL of each trade is applied immediately and equity updated subsequently.
    ExecutionGate checks are done before starting each trade based on risk_manager state.
    """
    if risk_manager is None:
        risk_manager = RiskManager()
    # Ensure global execution gate uses this risk manager for checks
    try:
        set_risk_manager(risk_manager)
    except Exception:
        pass
    equity = initial_equity
    equity_history = [equity]
    executed_trades = []
    open_trades_count = 0
    total_open_risk_pct = 0.0
    # For each trade, check gate, then apply PnL
    for t in trades:
        proposed_risk = t.get('effective_risk_pct') or risk_manager.config.get('default_risk_per_trade_pct', 0.0075)
        # For simulated backtests, ignore live market schedule; pass theme=None to avoid is_market_open checks
        allowed = can_place_order(proposed_risk_pct=proposed_risk, open_trades_count=open_trades_count, total_open_risk_pct=total_open_risk_pct, strategy_name=t.get('strategy'), pack_name=t.get('pack'), theme=None, open_theme_count=0)
        if not allowed:
            continue
        # register open
        try:
            sym = t.get('symbol')
            plat = t.get('asset_class')
            side = t.get('side')
            if sym and plat and side:
                risk_manager.state.register_open(sym, plat, side)
        except Exception:
            pass
        # compute PnL using dynamic position sizing based on effective_risk_pct
        entry = float(t['entry'])
        tp = float(t['tp'])
        sl = float(t['stop'])
        side = t.get('side')
        # naive: assume TP is hit (best-case), else loss is applied; for test, toggle behavior by presence of 'hit_tp'
        hit_tp = t.get('hit_tp', True)
        # Determine effective risk used for position sizing
        effective_risk_pct = float(t.get('effective_risk_pct') or risk_manager.config.get('default_risk_per_trade_pct', 0.0075))
        # distance to stop
        stop_distance = abs(entry - sl)
        if stop_distance <= 0:
            continue
        # Size in price units such that worst-case loss = equity * effective_risk_pct
        position_size = (equity * effective_risk_pct) / stop_distance
        if hit_tp:
            pnl = (tp - entry) if side == 'BUY' else (entry - tp)
        else:
            pnl = (entry - sl) if side == 'BUY' else (entry - sl)
        # apply slippage and commission
        # slippage is applied as fraction of price move for simplicity
        pnl = pnl - slippage * abs(pnl)
        trade_value = position_size * entry
        commission = trade_value * commission_pct
        pnl_cash = pnl * position_size - commission
        # already computed above
        equity += pnl_cash
        executed_trades.append({'entry': entry, 'tp': tp, 'sl': sl, 'side': side, 'pnl': pnl_cash})
        open_trades_count = max(0, open_trades_count)
        total_open_risk_pct = 0.0
        risk_manager.update_equity(equity)
        equity_history.append(equity)
        try:
            symc = t.get('symbol')
            platc = t.get('asset_class')
            sidec = t.get('side')
            if symc and platc and sidec:
                risk_manager.state.register_close(symc, platc, sidec)
        except Exception:
            pass
    metrics = compute_metrics(executed_trades)
    return {'equity_history': equity_history, 'final_equity': equity, 'trades': executed_trades, 'metrics': metrics}


def simulate_trades_bar_by_bar(trades: List[Dict[str, Any]], df: pd.DataFrame, initial_equity: float = 10000.0, risk_manager: RiskManager | None = None, pip_value: float = 0.0001, slippage: float = 0.0, commission_pct: float = 0.0002):
    """Simulate trades bar-by-bar using a DataFrame timeline (columns: time, open, high, low, close, volume).

    For each trade, find entry index time in df and iterate subsequent bars, applying trailing logic and checking TP/SL on each bar.
    This is a naive simulation suitable for intraday strategies and tests.
    """
    if pd is None:
        raise RuntimeError('pandas must be available for bar-by-bar simulation')
    if risk_manager is None:
        risk_manager = RiskManager()
    equity = initial_equity
    equity_history = [equity]
    executed = []
    for t in trades:
        # ensure we have time index and that df contains the starting point
        ts = t.get('timestamp')
        if ts is None:
            continue
        # find index where df time equals timestamp; accept string time format
        try:
            idx = df.index[df['time'] == ts].tolist()
            if not idx:
                # find first index greater than timestamp
                idx = df.index[df['time'] > ts].tolist()
            if not idx:
                continue
            start_idx = int(idx[0])
        except Exception:
            continue
        entry = float(t['entry'])
        tp = float(t['tp'])
        sl = float(t['stop'])
        side = t.get('side')
        # compute position_size
        effective_risk_pct = float(t.get('effective_risk_pct') or risk_manager.config.get('default_risk_per_trade_pct', 0.0075))
        stop_distance = abs(entry - sl)
        if stop_distance <= 0:
            continue
        position_size = (equity * effective_risk_pct) / stop_distance

        current_sl = sl
        open_time = datetime.now(tz=timezone.utc)
        last_liq = t.get('last_liquidity_level')
        last_swing = t.get('last_swing_price')
        atr_val = t.get('atr')
        closed = False
        entry_executed = False
        entry_price = None
        entry_bar_index = None
        remaining_size = position_size
        partial_tps = t.get('tps') or []
        remaining_tps = list(partial_tps) if partial_tps else []
        # if tps is list of prices
        if partial_tps and isinstance(partial_tps, list):
            # split remaining size equally per target unless sizes specified
            per_tp_size = position_size / len(partial_tps)
        else:
            per_tp_size = position_size
        for j in range(start_idx, len(df)):
            row = df.iloc[j]
            o = float(row['open'])
            h = float(row['high'])
            l = float(row['low'])
            c = float(row['close'])
            current_price = float(row['close'])
            # Entry logic: execute market or limit orders
            if not entry_executed:
                order_type = t.get('order_type', 'market')
                # market orders execute at next bar open
                if order_type == 'market':
                    actual_entry = o + (slippage * (1 if side == 'BUY' else -1))
                    entry = actual_entry
                    entry_executed = True
                    entry_bar_index = j
                else:
                    # limit orders: execute if entry falls within bar range
                    if side == 'BUY' and l <= entry <= h:
                        entry_executed = True
                        entry_bar_index = j
                    elif side == 'SELL' and l <= entry <= h:
                        entry_executed = True
                        entry_bar_index = j
                if entry_executed:
                    # recompute position size based on actual entry (if market order changed it)
                    stop_distance = abs(entry - sl)
                    if stop_distance <= 0:
                        break
                    remaining_size = (equity * effective_risk_pct) / stop_distance
                    position_size = remaining_size
                    per_tp_size = remaining_size / len(remaining_tps) if remaining_tps else remaining_size
                else:
                    # not yet entered, continue to next bar
                    continue
            # compute trailing sl suggestion
            pos_snap = PositionSnapshot(
                symbol=t.get('symbol'),
                direction=side,
                entry_price=entry,
                current_price=current_price,
                initial_sl=sl,
                current_sl=current_sl,
                open_time=open_time,
                now=datetime.now(tz=timezone.utc),
                last_swing_price=last_swing,
                last_liquidity_level=last_liq,
                atr_value=atr_val,
            )
            new_sl = compute_trailing_sl(pos_snap, pip_value)
            if new_sl != current_sl:
                current_sl = new_sl
            # check bar for TP/SL hits
            high = float(row['high'])
            low = float(row['low'])
            hit_tp = False
            hit_sl = False
            if side == 'BUY':
                if high >= tp:
                    hit_tp = True
                elif low <= current_sl:
                    hit_sl = True
            else:
                if low <= tp:
                    hit_tp = True
                elif high >= current_sl:
                    hit_sl = True
            # Determine which target(s) or stop hit during the bar using price path: open -> high -> low -> close (long)
            #                       or open -> low -> high -> close (short)
            def _resolve_path(o, h, l, c, side):
                # returns (hit_tp_price_or_none, hit_sl_price_or_none, midpoint_price)
                if side == 'BUY':
                    # assume first check high then low
                    if h >= tp and l <= current_sl:
                        # both hit; assume high (tp) first - conservative? We choose worse outcome for safety: assume SL first
                        return (None, current_sl)
                    if h >= tp:
                        return (tp, None)
                    if l <= current_sl:
                        return (None, current_sl)
                else:
                    if l <= tp and h >= current_sl:
                        return (None, current_sl)
                    if l <= tp:
                        return (tp, None)
                    if h >= current_sl:
                        return (None, current_sl)
                return (None, None)

            tp_hit_price, sl_hit_price = _resolve_path(o, high, low, c, side)
            # First, check partial TPs specifically (if provided)
            if remaining_tps:
                # For buys, check smallest->largest; for sells, check largest->smallest
                tps_to_check = sorted(remaining_tps) if side == 'BUY' else sorted(remaining_tps, reverse=True)
                for tp_price in tps_to_check:
                    if side == 'BUY' and high >= tp_price:
                        # partial tp hit
                        pnl_unit = (tp_price - entry)
                        part_size = per_tp_size
                        pnl_cash_part = pnl_unit * part_size
                        pnl_cash_part = pnl_cash_part - slippage * abs(pnl_cash_part)
                        trade_value_part = part_size * entry
                        comm_part = trade_value_part * commission_pct
                        pnl_cash_part -= comm_part
                        equity += pnl_cash_part
                        executed.append({'entry': entry, 'tp': tp_price, 'sl': current_sl, 'side': side, 'pnl': pnl_cash_part, 'hit_tp': True})
                        remaining_tps.remove(tp_price)
                        remaining_size -= part_size
                        if remaining_size <= 0:
                            risk_manager.update_equity(equity)
                            equity_history.append(equity)
                            closed = True
                            break
                        # else continue checking other TPs this bar
                    elif side == 'SELL' and low <= tp_price:
                        pnl_unit = (entry - tp_price)
                        part_size = per_tp_size
                        pnl_cash_part = pnl_unit * part_size
                        pnl_cash_part = pnl_cash_part - slippage * abs(pnl_cash_part)
                        trade_value_part = part_size * entry
                        comm_part = trade_value_part * commission_pct
                        pnl_cash_part -= comm_part
                        equity += pnl_cash_part
                        executed.append({'entry': entry, 'tp': tp_price, 'sl': current_sl, 'side': side, 'pnl': pnl_cash_part, 'hit_tp': True})
                        remaining_tps.remove(tp_price)
                        remaining_size -= part_size
                        if remaining_size <= 0:
                            risk_manager.update_equity(equity)
                            equity_history.append(equity)
                            closed = True
                            break
                if closed:
                    break
                # if no partial TP was triggered, fall through to normal tp/sl hit checks
            if tp_hit_price is not None or sl_hit_price is not None:
                if tp_hit_price is not None:
                    # handle partial tps: if tps list provided we reduce remaining size by per_tp_size
                    pnl_unit = (tp - entry) if side == 'BUY' else (entry - tp)
                    # compute part size
                    if partial_tps:
                        part_size = per_tp_size
                    else:
                        part_size = remaining_size
                    pnl_cash_part = pnl_unit * part_size
                    pnl_cash_part = pnl_cash_part - slippage * abs(pnl_cash_part)
                    trade_value_part = part_size * entry
                    comm_part = trade_value_part * commission_pct
                    pnl_cash_part -= comm_part
                    equity += pnl_cash_part
                    executed.append({'entry': entry, 'tp': tp, 'sl': current_sl, 'side': side, 'pnl': pnl_cash_part, 'hit_tp': True})
                    if partial_tps:
                        remaining_size -= part_size
                        # if still size remains, continue simulation with new position size
                        if remaining_size <= 0:
                            risk_manager.update_equity(equity)
                            equity_history.append(equity)
                            closed = True
                            break
                        else:
                            # continue still opened position for remaining_size; update position snapshot and continue
                            continue
                    else:
                        risk_manager.update_equity(equity)
                        equity_history.append(equity)
                        closed = True
                        break
                else:
                    pnl_unit = (current_sl - entry) if side == 'BUY' else (entry - current_sl)
                    pnl_cash = pnl_unit * remaining_size
                    pnl_cash = pnl_cash - slippage * abs(pnl_cash)
                    trade_value = remaining_size * entry
                    commission = trade_value * commission_pct
                    pnl_cash -= commission
                    equity += pnl_cash
                    executed.append({'entry': entry, 'sl': current_sl, 'tp': tp, 'side': side, 'pnl': pnl_cash, 'hit_tp': False})
                    risk_manager.update_equity(equity)
                    equity_history.append(equity)
                    closed = True
                    break
                equity += pnl_cash
                executed.append({'entry': entry, 'tp': tp, 'sl': current_sl, 'side': side, 'pnl': pnl_cash, 'hit_tp': hit_tp})
                risk_manager.update_equity(equity)
                equity_history.append(equity)
                closed = True
                break
            # time cap: assume max_hold_hours in pos_snap
        if not closed:
            # enforce time-based exit at last bar value: treat as market close
            final_px = float(df.iloc[-1]['close'])
            pnl_unit = (final_px - entry) if side == 'BUY' else (entry - final_px)
            pnl_cash = pnl_unit * remaining_size
            # apply slippage and commission on last-bar exit
            pnl_cash = pnl_cash - slippage * abs(pnl_cash)
            trade_value = position_size * entry
            commission = trade_value * commission_pct
            pnl_cash -= commission
            equity += pnl_cash
            executed.append({'entry': entry, 'sl': current_sl, 'tp': tp, 'side': side, 'pnl': pnl_cash, 'hit_tp': False})
            risk_manager.update_equity(equity)
            equity_history.append(equity)
    metrics = compute_metrics(executed)
    return {'equity_history': equity_history, 'final_equity': equity, 'trades': executed, 'metrics': metrics}


def run_backtest(df, signals: List[Dict[str, Any]], config: BacktestConfig | None = None, risk_manager: RiskManager | None = None) -> BacktestResult:
    """Canonical backtest entry: accepts OHLCV DataFrame and a list of signals (dicts).

    This uses bar-by-bar simulation, handles partial TPs, trailing SL, fees & slippage, and returns a BacktestResult.
    """
    if config is None:
        config = BacktestConfig()
    trades = apply_signals(df, signals)
    sim_res = simulate_trades_bar_by_bar(trades, df, initial_equity=config.initial_equity, risk_manager=risk_manager, pip_value=config.pip_value, slippage=config.slippage, commission_pct=config.commission_pct)
    bres = BacktestResult(trades=sim_res['trades'], equity_curve=sim_res['equity_history'], metrics=sim_res['metrics'])
    return bres
