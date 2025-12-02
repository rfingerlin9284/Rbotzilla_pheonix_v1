PhoenixV2 Finalization & Social Data Integration
-------------------------------------------------

This repository contains a set of tools to finalize the PhoenixV2 engine and
integrate free social/news sources into the QuantHedge rules.

Key Scripts
- scripts/phoenix_v2_finalize_real.py: writes PhoenixV2 module files from a
  set of templates. It will backup existing files under `archives/phoenix_v2_backup_*`.
  Run with `--force` to overwrite existing files.

  Usage:
    python3 scripts/phoenix_v2_finalize_real.py --force

- scripts/test_social_reader.py: prints reddit/hackernews/google-news-based
  sentiment summary (uses PRAW, feedparser, requests, and vaderSentiment if available).

- scripts/test_alerting.py: verify Telegram/Discord alerting configuration and test send.

Notes & Safety
- The finalize script is intentionally conservative and will not overwrite PhoenixV2
  files without `--force`. Please verify your backups before using.

- The Router uses a safety wrapper (safe_place_order in `PhoenixV2/execution/safety.py`)
  to keep PAPER mode safe and normalize connector return shape.

- Social sentiment is a soft input only; QuantHedge analysis incorporates social
  sentiment to slightly modify severity scores. It is not used to force live trades.

If you have further requests (Slack/Twilio integration, more sources, or to sync
with an IOC/real-time data pipeline), please open a ticket and I'll add it.
