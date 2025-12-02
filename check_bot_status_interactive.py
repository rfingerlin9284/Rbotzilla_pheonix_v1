#!/usr/bin/env python3
"""Interactive bot status checker with menu options."""

import subprocess
import json
from datetime import datetime
from pathlib import Path

print('='*80)
print('🤖 BOT STATUS CHECK')
print('='*80 + '\n')

# Check engines
engines = {'Coinbase': 'coinbase_safe_mode_engine.py', 'OANDA': 'oanda_trading_engine.py'}
status = {}

for name, script in engines.items():
    result = subprocess.run(['pgrep', '-f', script], capture_output=True)
    status[name] = 'RUNNING' if result.returncode == 0 else 'STOPPED'
    print(f"{name}: {'🟢 ' + status[name] if status[name] == 'RUNNING' else '🔴 ' + status[name]}")

print('\n' + '='*80)
print('\n📋 ACTION MENU:')
print('  1. Save status to file')
print('  2. Stop specific engine')
print('  3. Print status again')
print('  4. Create status snapshot')
print('  5. Exit')

choice = input('\nChoice (1-5): ')

if choice == '1':
    Path('results').mkdir(exist_ok=True)
    fn = input('Filename (default: status_now.json): ') or f"status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(f'results/{fn}', 'w') as f:
        json.dump({'timestamp': datetime.now().isoformat(), 'status': status}, f, indent=2)
    print(f'✅ Saved: results/{fn}')
elif choice == '2':
    print('\n🛑 STOP ENGINE:')
    print('  1. Coinbase')
    print('  2. OANDA')
    print('  3. Both')
    print('  0. Cancel')
    stop = input('Choice: ')
    if stop == '1':
        confirm = input('Type STOP to confirm stopping Coinbase: ')
        if confirm == 'STOP':
            subprocess.run(['pkill', '-f', 'coinbase_safe_mode_engine.py'])
            print('✅ Coinbase engine stopped')
    elif stop == '2':
        confirm = input('Type STOP to confirm stopping OANDA: ')
        if confirm == 'STOP':
            subprocess.run(['pkill', '-f', 'oanda_trading_engine.py'])
            print('✅ OANDA engine stopped')
    elif stop == '3':
        confirm = input('Type EMERGENCY to confirm stopping BOTH: ')
        if confirm == 'EMERGENCY':
            subprocess.run(['pkill', '-f', 'trading_engine'])
            print('✅ All engines stopped')
elif choice == '3':
    for name, s in status.items():
        print(f"{name}: {s}")
elif choice == '4':
    rb = datetime.now().strftime('%Y%m%d_%H%M%S')
    lbl = input('Snapshot label: ') or f'Status snapshot {rb}'
    Path(f'rollback_points/{rb}').mkdir(parents=True, exist_ok=True)
    with open(f'rollback_points/{rb}/metadata.json', 'w') as f:
        json.dump({'id': rb, 'label': lbl, 'task': 'Bot Status', 'status': status, 'timestamp': datetime.now().isoformat()}, f, indent=2)
    print(f'\n✅ Snapshot created: {rb}')
    print(f'   Label: {lbl}')
else:
    print('✅ Exiting')
