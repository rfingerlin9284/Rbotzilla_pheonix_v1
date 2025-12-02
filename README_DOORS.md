# CRITICAL DOOR FILES

The following files are **DOOR FILES**. They are the entry points for the autonomous trading system.

**DO NOT DELETE, RENAME, OR MOVE THESE FILES WITHOUT UPDATING DEPLOYMENT SCRIPTS.**

## List of Door Files

1.  `run_autonomous.py`: The main Python entry point. It attempts to import the real trading engine and falls back to a stub if it fails.
2.  `tools/safe_start_paper_trading.sh`: The primary script for starting paper trading safely.
3.  `start_paper_with_ibkr.sh`: The script to launch paper trading with IBKR integration.
4.  `foundation/rick_charter.py`: The core charter definition file.

## Testing

We have automated tests to ensure these files are present and functional:

*   `test_door_files_present.py`: Verifies that all door files exist on the filesystem.
*   `test_run_autonomous_entrypoint.py`: Verifies that `run_autonomous.py` can be imported and exposes the expected `_Engine` class with a `start_ghost_trading` method.

If you change the startup logic or engine entry points, you **MUST** update `run_autonomous.py` and these tests to match.
