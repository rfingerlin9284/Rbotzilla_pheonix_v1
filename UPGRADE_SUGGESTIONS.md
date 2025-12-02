Upgrade Suggestions and Prioritized Tasks
======================================

High Priority (Recommended before enabling LIVE trading):
- CI integration for safety & readiness checks
  - Add a GitHub Actions / GitLab CI workflow that runs `scripts/run_readiness_checks.py` and `scripts/predeployment_diagnostics.py` on every pull request.
  - Make failures block merging.

- Secrets & credentials management
  - Validate that no API keys are checked into the repo.
  - Integrate with secret storage (AWS Secrets Manager, Vault) and ensure live credentials are provided at runtime in a secure way.

- Standardize connector return types (Canonical format)
  - Use a canonical dict shape: {'success': bool, 'error': Optional[str], 'data': {...}}.
  - Update all connectors (OANDA, IBKR, Coinbase) to add 'success' & 'error' consistently.
  - Update adapters/consumers to read `data` or top-level keys accordingly.

- End-to-end integration tests (Sandbox/CI) with PAPER mode
  - Add sandbox tests that exercise the entire routing engine & order handling.
  - Add a nightly or PR test that runs a simulated trade flow end-to-end.

Medium Priority (Important enhancements):
- Full replacement of direct `.place_order` calls
  - Clean up the remaining canonical direct calls in archives & prototype code.
  - Add a pre-commit linter rule to prevent new direct `.place_order` usage.

- Logging & monitoring enhancements
  - Add log rotation, retention rules for simulated audits log and real trades logs.
  - Add dashboards & alerts for high-latency or repeated failure patterns.

- Operator runbook for enabling LIVE
  - Define exact human workflow to enable LIVE trading, including checks, approvals and emergency stop.

Low Priority (Nice to have in future updates):
- Canonical 'data' field across connectors
  - Move broker-specific return payloads under a single key (`data`) to reduce code changes in the future.

- Historical cleanup & repo pruning
  - Archive old artifacts and large logs into a separate storage and prune repository where needed.

- Performance benchmarking & optimization
  - Add more end-to-end performance tests and tracing to detect slow components and slow strategy decisions.

- Feature: automatic daily audit report integration
  - Create a scheduled job to run `scripts/daily_audit_report.py` and store deep daily metrics in a historical telemetry store (e.g., a time-series DB).

Summary
-------
Your project is ready to PAPER test and is protected from accidental live trades by the safety wrapper & pre-commit detection script. The above upgrades are suggested to reduce risk for going LIVE and to increase reliability for production operation.
