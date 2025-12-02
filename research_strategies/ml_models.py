"""ML model utilities for research strategies.
Use scikit-learn RandomForest as a simple tabular model if available else fallback to a mock model.
"""
from typing import Any, Dict, Optional, List
import numpy as np


def _sklearn_available():
    try:
        import sklearn
        return True
    except Exception:
        return False


def train_model(X, y, params: Optional[Dict[str, Any]] = None):
    if _sklearn_available():
        from sklearn.ensemble import RandomForestClassifier
        clf = RandomForestClassifier(n_estimators=params.get('n_estimators', 50)) if params else RandomForestClassifier(n_estimators=50)
        clf.fit(X, y)
        return {'model': clf, 'params': params}
    else:
        # simple fallback: store mean label
        return {'model': {'mean': float(np.mean(y))}, 'params': params}


def predict(model_obj, X: List[Dict[str, Any]]):
    if _sklearn_available() and hasattr(model_obj.get('model'), 'predict_proba'):
        clf = model_obj['model']
        probs = clf.predict_proba(X)
        # return probabilities for positive class
        return [p[1] for p in probs]
    # fallback: return uniform mean
    mean = model_obj.get('model', {}).get('mean', 0.5)
    return [float(mean) for _ in X]


MODEL_REGISTRY = {}


def train_models_on_backtest_data(key: str, X, y, params: Optional[Dict[str, Any]] = None):
    model = train_model(X, y, params=params)
    MODEL_REGISTRY[key] = model
    return model


def score_signals(model_key: str, signals: List[Dict[str, Any]]):
    model = MODEL_REGISTRY.get(model_key)
    if model is None:
        return [0.5 for _ in signals]
    # Build feature matrix from signals; if we can't, fallback to dummy
    try:
        X = [list(s.get('features', {}).values()) for s in signals]
        return predict(model, X)
    except Exception:
        return [0.5 for _ in signals]
