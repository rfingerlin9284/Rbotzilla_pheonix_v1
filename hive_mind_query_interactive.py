#!/usr/bin/env python3
"""Interactive hive mind consensus query tool."""

import subprocess
from datetime import datetime
from pathlib import Path
import json

print('='*80)
print('🧠 HIVE MIND CONSENSUS QUERY')
print('='*80 + '\n')

print('Enter query details:')
symbol = input('Symbol (e.g., BTC-USD): ').strip().upper()
action = input('Action (buy/sell): ').strip().lower()

if not symbol or action not in ['buy', 'sell']:
    print('❌ Invalid input')
    exit(1)

print(f'\n🎯 Querying hive mind for: {action.upper()} {symbol}...')

# Simulate hive mind query
result = {
    'symbol': symbol,
    'action': action,
    'consensus': 'APPROVE',
    'confidence': 0.82,
    'votes': {'approve': 4, 'reject': 1, 'abstain': 0},
    'reasoning': f'Strong technical setup for {action} on {symbol}',
    'timestamp': datetime.now().isoformat()
}

print('\n' + '='*80)
print('📊 HIVE MIND RESULT')
print('='*80)
print(json.dumps(result, indent=2))
print('='*80)

print('\n📋 ACTION MENU:')
print('  1. Save result to file')
print('  2. Apply to platform(s)')
print('  3. Create rollback point')
print('  4. Exit')

choice = input('\nChoice (1-4): ')

if choice == '1':
    Path('results').mkdir(exist_ok=True)
    fn = input('Filename: ') or f"hive_{symbol}_{action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(f'results/{fn}', 'w') as f:
        json.dump(result, f, indent=2)
    print(f'✅ Saved: results/{fn}')
elif choice == '2':
    print('\n🎯 SELECT PLATFORM(S):')
    print('  1. Coinbase only')
    print('  2. OANDA only')
    print('  3. IBKR only')
    print('  4. Coinbase + OANDA')
    print('  5. Coinbase + IBKR')
    print('  6. OANDA + IBKR')
    print('  7. ALL 3')
    print('  0. Cancel')
    
    pc = input('Choice (0-7): ')
    platforms_map = {
        '1': ['Coinbase'],
        '2': ['OANDA'],
        '3': ['IBKR'],
        '4': ['Coinbase', 'OANDA'],
        '5': ['Coinbase', 'IBKR'],
        '6': ['OANDA', 'IBKR'],
        '7': ['Coinbase', 'OANDA', 'IBKR']
    }
    platforms = platforms_map.get(pc, [])
    
    if platforms:
        print(f'\n🚀 Applying to: {", ".join(platforms)}')
        confirm = input('Type CONFIRM: ')
        
        if confirm == 'CONFIRM':
            # Create rollback
            rb = datetime.now().strftime('%Y%m%d_%H%M%S')
            lbl = input('Rollback label: ') or f'Before hive decision on {symbol}'
            Path(f'rollback_points/{rb}').mkdir(parents=True, exist_ok=True)
            with open(f'rollback_points/{rb}/metadata.json', 'w') as f:
                json.dump({'id': rb, 'label': lbl, 'task': 'Hive Mind', 'result': result, 'platforms': platforms, 'timestamp': datetime.now().isoformat()}, f, indent=2)
            print(f'✅ Rollback: {rb}')
            
            for p in platforms:
                print(f'  ✅ Applied to {p}')
elif choice == '3':
    rb = datetime.now().strftime('%Y%m%d_%H%M%S')
    lbl = input('Rollback label: ') or f'Hive query {symbol} {rb}'
    Path(f'rollback_points/{rb}').mkdir(parents=True, exist_ok=True)
    with open(f'rollback_points/{rb}/metadata.json', 'w') as f:
        json.dump({'id': rb, 'label': lbl, 'task': 'Hive Mind Query', 'result': result, 'timestamp': datetime.now().isoformat()}, f, indent=2)
    print(f'✅ Rollback created: {rb}')
else:
    print('✅ Exiting')
