#!/usr/bin/env python3
"""Interactive engine stopper with platform selection."""

import subprocess
from datetime import datetime
from pathlib import Path
import json

print('='*80)
print('🛑 STOP TRADING ENGINE')
print('='*80 + '\n')

print('🎯 SELECT ENGINE(S) TO STOP:')
print('  1. Coinbase only')
print('  2. OANDA only')
print('  3. IBKR only')
print('  4. Coinbase + OANDA')
print('  5. Coinbase + IBKR')
print('  6. OANDA + IBKR')
print('  7. ALL 3 platforms')
print('  0. Exit')

choice = input('\nChoice (0-7): ')

if choice == '0':
    print('❌ Cancelled')
    exit(0)

engines_map = {
    '1': [('Coinbase', 'coinbase_safe_mode_engine.py')],
    '2': [('OANDA', 'oanda_trading_engine.py')],
    '3': [('IBKR', 'ibkr_gateway.py')],
    '4': [('Coinbase', 'coinbase_safe_mode_engine.py'), ('OANDA', 'oanda_trading_engine.py')],
    '5': [('Coinbase', 'coinbase_safe_mode_engine.py'), ('IBKR', 'ibkr_gateway.py')],
    '6': [('OANDA', 'oanda_trading_engine.py'), ('IBKR', 'ibkr_gateway.py')],
    '7': [('Coinbase', 'coinbase_safe_mode_engine.py'), ('OANDA', 'oanda_trading_engine.py'), ('IBKR', 'ibkr_gateway.py')]
}

engines = engines_map.get(choice, [])

if engines:
    platforms = [e[0] for e in engines]
    print(f'\n⚠️ You are about to stop: {", ".join(platforms)}')
    confirm = input(f'Type STOP to confirm: ')
    
    if confirm == 'STOP':
        # Create rollback point
        print('\n💾 Creating pre-stop rollback point...')
        rb = datetime.now().strftime('%Y%m%d_%H%M%S')
        lbl = input('Rollback label: ') or f'Before stopping {", ".join(platforms)}'
        
        Path(f'rollback_points/{rb}').mkdir(parents=True, exist_ok=True)
        with open(f'rollback_points/{rb}/metadata.json', 'w') as f:
            json.dump({
                'id': rb,
                'label': lbl,
                'task': 'Stop Engine',
                'platforms': platforms,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f'✅ Rollback point: {rb}\n')
        
        # Stop engines
        for name, script in engines:
            subprocess.run(['pkill', '-f', script])
            print(f'✅ Stopped: {name}')
        
        print('\n✅ All selected engines stopped')
    else:
        print('❌ Cancelled')
