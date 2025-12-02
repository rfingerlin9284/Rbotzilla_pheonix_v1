from typing import List


def moving_average(series: List[float], period: int) -> List[float]:
    if not series or period <= 0:
        return []
    out = []
    s = 0.0
    for i, v in enumerate(series):
        s += v
        if i >= period:
            s -= series[i - period]
        if i >= period - 1:
            out.append(s / period)
    return out


def atr_from_ohlcv(highs, lows, closes, period=14):
    # Very simple ATR calculation returning last ATR value
    if not highs or len(highs) < period:
        return None
    tr_list = []
    for i in range(1, len(highs)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        tr_list.append(tr)
    if not tr_list:
        return None
    atr = sum(tr_list[-period:]) / min(len(tr_list), period)
    return atr
