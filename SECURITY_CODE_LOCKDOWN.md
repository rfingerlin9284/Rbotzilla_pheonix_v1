## Code Lockdown & PIN Protection

This document describes how to harden the repository for production by denying code edits and requiring PIN approval for any modifications to critical files. It covers renames, edits, and adding hooks.

Key elements:
- `pin_protection.py`: Interactively lock and unlock critical files using the Charter PIN.
- `hooks/pre-commit`: A pre-commit hook template that blocks commits touching locked files unless a valid `RICK_PIN` env var is supplied and validated.
- `lock_all_code.sh`: A script to set read-only permissions across the repo's code files.
- `scripts/unlock_repo.py`: A script that restores write permissions when a proper PIN is provided.

How to lock the code (recommended):
1. Run `python3 pin_protection.py --lock` and follow double-PIN verification. This sets permissions and records lock state in `.system_lock.json`.
2. Optionally, run `./lock_all_code.sh` to set a broader locking state for the repository.

How to unlock:
1. Run `python3 pin_protection.py --unlock` and follow double-PIN verification.
2. Alternatively, provide `RICK_PIN` env var and run `python3 scripts/unlock_repo.py`. This is convenient for automated admin tasks.

Pre-commit hooks (rename protection):
- The hook checks for staged renames that affect locked files; if found, it will require `RICK_PIN` to be set and validated.
- To install the hook for your repo, copy `hooks/pre-commit` to `.git/hooks/pre-commit` and ensure it's executable.

Security notes:
- These measures prevent casual code edits and make sure that key files can only be edited under a validated, auditable process.
- They are not a substitute for server-side CI enforcement — for full guarantee, add a server-side gate as part of your CI/CD pipeline.

Contact: rick_security@localhost
