from research_strategies.ml_models import train_model, predict
try:
    import numpy as np
except Exception:
    np = None


def test_train_and_predict():
    if np is None:
        import pytest
        pytest.skip('numpy is not installed; skipping ML model test')
    X = np.random.rand(100, 5)
    y = (np.random.rand(100) > 0.5).astype(int)
    model = train_model(X, y, params={'n_estimators': 10})
    preds = predict(model, X[:5])
    assert len(preds) == 5
    assert all(isinstance(p, float) for p in preds)


def test_train_models_on_backtest_data():
    if np is None:
        import pytest
        pytest.skip('numpy not installed; skipping')
    X = np.random.rand(50, 3)
    y = (np.random.rand(50) > 0.5).astype(int)
    from research_strategies.ml_models import train_models_on_backtest_data, score_signals
    model = train_models_on_backtest_data('fx_bull', X, y, params={'n_estimators': 5})
    signals = [{'features': {'a': 1.0, 'b': 2.0}}, {'features': {'a': 0.5}}]
    scores = score_signals('fx_bull', signals)
    assert isinstance(scores, list) and len(scores) == 2
