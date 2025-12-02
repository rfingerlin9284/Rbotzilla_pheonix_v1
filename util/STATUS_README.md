# Engine Status Checker

Utility to check engine & hive status by scanning `narration.jsonl`.

Usage:
  python3 util/check_engine_status.py --narration-file narration.jsonl --last-minutes 30 --min-trades 1

Flags:
- --narration-file: Path to narration file to analyze (defaults to repository `narration.jsonl`).
- --last-minutes: Window size to look for recent events (default 30).
- --min-trades: Minimum number of trades (TRADE_OPENED + TRADE_EXECUTED) within the window to consider the engine "active" (default 1).
- --json: print JSON output.
- --quiet: only return exit code for CI hooks (0 = healthy).

Returns:
- Exit code 0 if engine is healthy (recent heartbeats + trades), else exit code 1.

Notes:
- This is a conservative health check for use in cron jobs, health monitors, and CI checks.
- It reads the narration file directly and uses timestamps to determine recency.
