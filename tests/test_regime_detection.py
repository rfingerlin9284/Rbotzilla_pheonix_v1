try:
    import pandas as pd
except Exception:
    pd = None

from util.regime_detector import detect_trend_regime, detect_vol_regime, detect_symbol_regime


def _bull_df():
    import pandas as pd
    df = pd.DataFrame({'close': [1 + i * 0.01 for i in range(220)]})
    return df


def _bear_df():
    import pandas as pd
    df = pd.DataFrame({'close': [2 - i * 0.01 for i in range(220)]})
    return df


def _range_df():
    import pandas as pd
    vals = [1.0, 1.02, 0.99, 1.01, 1.0, 1.03, 0.98] * 40
    df = pd.DataFrame({'close': vals})
    return df


def test_detect_trend_regime():
    if pd is None:
        import pytest
        pytest.skip('pandas not installed; skipping regime tests')
    assert detect_trend_regime(_bull_df()) == 'BULL'
    assert detect_trend_regime(_bear_df()) == 'BEAR'
    assert detect_trend_regime(_range_df()) == 'RANGE'


def test_detect_vol_regime():
    if pd is None:
        import pytest
        pytest.skip('pandas not installed; skipping regime tests')
    df = _range_df()
    assert detect_vol_regime(df, lookback=20) in ('NORMAL', 'LOW', 'HIGH')
