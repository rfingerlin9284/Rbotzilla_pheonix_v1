# Secure env workflow

This repository stores a read-only `env_new.env` and an encrypted copy `env_new.env.gpg` for secure local storage.

Files added:
- `env_new.env` - canonical read-only copy (do not edit directly)
- `env_new.env.gpg` - encrypted copy of the env (binary)
- `scripts/unlock_env.sh` - decrypts and prints the env to stdout (PIN required)
- `scripts/edit_env.sh` - decrypts to a temp file, opens $EDITOR for edits, then re-encrypts (PIN required)

How it works
1. To view the env (read-only):

```bash
./scripts/unlock_env.sh
```

2. To edit securely:

```bash
./scripts/edit_env.sh
```

You will be prompted for a PIN. The PIN is used as the symmetric passphrase for GPG symmetric encryption. The plaintext env is only present in a secure temporary file and shredded after re-encryption.

Security notes
- The scripts use GPG symmetric encryption (AES256). The security of the encrypted file depends on the secrecy and strength of your PIN.
- For better security, use a long random passphrase rather than a short PIN.
- Consider using GPG public-key encryption with your private key for multi-user workflows.
- The scripts require `gpg` installed and available in PATH.
