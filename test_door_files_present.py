import os
import logging
import pytest

ROOT = os.path.dirname(os.path.abspath(__file__))

DOOR_FILES = [
    os.path.join(ROOT, 'run_autonomous.py'),
        os.path.join(ROOT, 'tools', 'safe_start_paper_trading.sh'),
            os.path.join(ROOT, 'start_paper_with_ibkr.sh'),
                os.path.join(ROOT, 'foundation', 'rick_charter.py'),
                ]


                def test_door_files_exist():
                    missing = [f for f in DOOR_FILES if not os.path.exists(f)]
                        assert not missing, f"Missing door files: {missing}"


                        def test_run_autonomous_readable():
                            path = os.path.join(ROOT, 'run_autonomous.py')
                                assert os.access(path, os.R_OK), 'run_autonomous.py must be readable'


                                def test_logging_output(caplog):
                                    """Test that the logging output contains the expected messages."""
                                        from run_autonomous import main  # Import here to avoid issues with pytest discovering the file as a test

                                            with caplog.at_level(logging.INFO):
                                                    main()

                                                        assert "OANDA practice credentials validated" in caplog.text
                                                            assert "✅ OANDA Practice API - CONNECTED" in caplog.text
                                                                assert "💰 Current Capital:" in caplog.text
                                                    