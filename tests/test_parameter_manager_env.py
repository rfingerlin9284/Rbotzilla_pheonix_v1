import os
from util.parameter_manager import get_parameter_manager


def test_parameter_manager_reads_env_override(tmp_path, monkeypatch):
    # Create a temp config file to avoid writing in repo
    cfg_path = tmp_path / 'params.json'
    cfg_path.write_text('{}')
    # Ensure env var isn't present for the initial check
    monkeypatch.delenv('OANDA_PRACTICE_TOKEN', raising=False)
    # Ensure a fresh ParameterManager instance is used for test isolation
    import util.parameter_manager as pm_module
    try:
        pm_module._instance = None
    except Exception:
        pass
    # Reset the real/rigorous parameter manager module if present (rick_clean_live implementation)
    try:
        import rick_clean_live.util.parameter_manager as rpm
        rpm._instance = None
    except Exception:
        pass
    # Ensure we're using the wrapper around the rick_clean_live ParameterManager (not a test stub left in sys.modules)
    try:
        import importlib, sys
        # Reload the util.parameter_manager wrapper to avoid any earlier test-injected stubs
        importlib.reload(importlib.import_module('util.parameter_manager'))
        real_pm = importlib.import_module('rick_clean_live.util.parameter_manager')
        sys.modules['rick_clean_live.util.parameter_manager'] = real_pm
        sys.modules['util.parameter_manager'] = importlib.import_module('util.parameter_manager')
    except Exception:
        pass
    # Re-import the get_parameter_manager from the active util.parameter_manager wrapper to avoid using a stub
    import importlib
    get_parameter_manager = importlib.import_module('util.parameter_manager').get_parameter_manager
    pm = get_parameter_manager(str(cfg_path))
    # ensure reads default behavior
    assert pm.get('oanda.practice.token', None) is None
    # now set env override and assert get returns it
    monkeypatch.setenv('OANDA_PRACTICE_TOKEN', 'TEST_TOKEN')
    assert pm.get('oanda.practice.token') == 'TEST_TOKEN'
