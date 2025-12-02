#!/usr/bin/env python3
"""
Dry run test for alerting channels: prints the alert destinations and optionally
attempts a test send if the env var TEST_ALERTING_SEND=1 (by default it's dry-run).
"""
import os
import sys
import time
sys.path.append(os.path.abspath('.'))
from foundation.env_manager import get_alert_config, redact

try:
    import requests
except Exception:
    requests = None

def main():
    cfg = get_alert_config()
    print('Alerting configuration (redacted):')
    for k, v in cfg.items():
        print(f"- {k}: {redact(v) if v else '<MISSING>'}")

    send = os.getenv('TEST_ALERTING_SEND', '0') == '1'
    if not send:
        print('\nDRY RUN: Not sending test messages. To actually send, set TEST_ALERTING_SEND=1 and ensure credentials are configured. After testing, remove credentials or rotate them.')
        return
    if not requests:
        print('\nSEND MODE: requests module not available; cannot send. Install `requests` or add it to requirements.txt')
        return

    print('\nSEND MODE: Sending test messages now (attempting Telegram + Discord if configured).')
    # Build a short test message
    ts = time.strftime('%Y-%m-%d %H:%M:%S %Z')
    text = f"RICK PHOENIX Test Alert - {ts}: This confirms TEST_ALERTING_SEND=1 and TESTING_ALERT_SENT=1 were set."

    # Telegram
    tg_token = cfg.get('TELEGRAM_BOT_TOKEN')
    tg_chat = cfg.get('TELEGRAM_CHAT_ID')
    if tg_token and tg_chat:
        try:
            url = f'https://api.telegram.org/bot{tg_token}/sendMessage'
            resp = requests.post(url, json={'chat_id': tg_chat, 'text': text}, timeout=10)
            if resp.status_code == 200:
                print('Telegram: Message sent successfully.')
            else:
                print(f'Telegram: Failed to send ({resp.status_code}): {resp.text[:256]}')
                if resp.status_code == 401:
                    print(' -> Telegram 401 Unauthorized: token may be invalid or revoked. Re-create the bot with @BotFather and re-issue token. Also check bot permissions and chat id.')
        except Exception as e:
            print(f'Telegram: Exception sending message: {e}')
    else:
        print('Telegram: Not configured (missing token or chat id)')

    # Discord
    discord_url = cfg.get('DISCORD_WEBHOOK_URL')
    if discord_url:
        try:
            resp = requests.post(discord_url, json={'content': text}, timeout=10)
            if resp.status_code in (200, 204):
                print('Discord: Webhook sent successfully.')
            else:
                print(f'Discord: Failed to send ({resp.status_code}): {resp.text[:256]}')
                if resp.status_code == 404:
                    print(' -> Discord 404: webhook not found. Recreate webhook in channel Integrations and paste the full URL into .env')
        except Exception as e:
            print(f'Discord: Exception sending webhook: {e}')
    else:
        print('Discord: Not configured (missing webhook URL)')

if __name__ == '__main__':
    main()
