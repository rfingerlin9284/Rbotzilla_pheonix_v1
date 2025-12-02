from research_strategies.pack_manager import compute_triage_allowed_from_results
import json, os


def test_compute_triage_allowed_from_results(tmp_path):
    # create a fake results JSON expected by model_selection
    results = {
        'FX_BULL_PACK': {
            'ema_scalper': {'sharpe': 0.8, 'max_dd': 0.15},
            'breakout_volume_expansion': {'sharpe': 1.5, 'max_dd': 0.18}
        }
    }
    p = tmp_path / 'results.json'
    with open(p, 'w') as f:
        json.dump(results, f)
    out = compute_triage_allowed_from_results(str(p))
    assert 'FX_BULL_PACK' in out
    assert out['FX_BULL_PACK'] == ['breakout_volume_expansion']
