from util.charter_config import load_charter_config


def test_load_charter_config():
    cfg = load_charter_config()
    assert isinstance(cfg, dict)
    assert 'risk' in cfg
    assert 'drawdown' in cfg
