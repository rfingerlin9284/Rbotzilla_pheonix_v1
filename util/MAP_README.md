Map OANDA Orders to AMM Trades
=================================

This small CLI tool heuristically maps OANDA order ids (OCO_PLACED / TRADE_OPENED) to internal AMM trade ids (TRADE_EXECUTED events).

Usage:

python3 util/map_oanda_to_amm.py narration.jsonl --threshold 60 --topn 3 --out json --out-file /tmp/mapping.json

Options:
- --threshold: acceptance threshold for heuristic match (default 60.0). Lower is stricter.
- --topn: how many top candidate matches to display for each order (default 3).
- --out: optional output format (json, csv, or none).
- --out-file: output filename (default map_oanda_to_amm_output.json).
- --write: when set, accepted matches will be written back as BROKER_MAPPING events into the narration log (dry-run by default without this flag).
- --narration-file: optional explicit narration file to write BROKER_MAPPING events to (useful for testing). When omitted, writes to the main narration.jsonl (or use NARRATION_FILE_OVERRIDE env var).

Notes:
- The tool detects per-symbol scale mappings (AMM prices may be scaled relative to raw OANDA prices) and uses a combined time + price (pips) score.
- If a BROKER_MAPPING event already exists in narration.jsonl, the script will report it as authoritative and skip heuristics.
- The script prints top-N candidates with scores to help manual verification.
- By default, the script only prints results (dry-run). Use --write to persist authoritative BROKER_MAPPING events; exercise caution and prefer reviewing the JSON output before writing.

Suggested next step: write an automated nightly job to generate a mapping report and store it in logs/ or JSON for audit.
