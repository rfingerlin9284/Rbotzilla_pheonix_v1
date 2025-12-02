import os
import tempfile
import logging
from PhoenixV2.core.auth import AuthManager


def test_auth_manager_logs_env_loading(caplog):
    caplog.set_level(logging.INFO)
    # Create a temporary env file
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(b"MODE=PAPER\n")
    tmp.close()
    try:
        a = AuthManager(env_path=tmp.name)
        # There should be an info log indicating the env_file was loaded and mode was set
        found = False
        for rec in caplog.records:
            if 'AuthManager: Loaded env_path' in rec.getMessage():
                found = True
                break
        assert found, "AuthManager did not log env_file load"
    finally:
        os.unlink(tmp.name)
