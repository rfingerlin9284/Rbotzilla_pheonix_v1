from research_strategies._model_selection_core import select_strategies_for_triage


def test_select_strategies_for_triage():
    sample_results = {
        'FX_BULL_PACK': {
            'ema_scalper': {'sharpe': 0.8, 'max_dd': 0.15},
            'breakout_volume_expansion': {'sharpe': 1.5, 'max_dd': 0.18},
            'other_strategy': {'sharpe': 1.1, 'max_dd': 0.35}
        },
        'CRYPTO_BULL_PACK': {
            'breakout_volume_expansion': {'sharpe': 1.3, 'max_dd': 0.22},
            'scalper': {'sharpe': 1.6, 'max_dd': 0.12}
        }
    }
    out = select_strategies_for_triage(sample_results, min_sharpe=1.0, max_dd=0.3, top_n=1)
    assert 'FX_BULL_PACK' in out and out['FX_BULL_PACK'] == ['breakout_volume_expansion']
    assert 'CRYPTO_BULL_PACK' in out and out['CRYPTO_BULL_PACK'] == ['scalper']
