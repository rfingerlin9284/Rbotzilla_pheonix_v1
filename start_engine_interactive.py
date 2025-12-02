#!/usr/bin/env python3
"""Interactive engine starter with platform selection."""

import subprocess
from datetime import datetime
from pathlib import Path
import json

print('='*80)
print('🚀 START TRADING ENGINE')
print('='*80 + '\n')

print('🎯 SELECT PLATFORM TO START:')
print('  1. Coinbase (Safe Mode)')
print('  2. OANDA (Practice)')
print('  3. IBKR Gateway')
print('  0. Exit')

platform = input('\nChoice (0-3): ')

if platform == '0':
    print('❌ Cancelled')
    exit(0)

if platform in ['1', '2', '3']:
    print('\n💾 CREATE PRE-START ROLLBACK POINT')
    rb = datetime.now().strftime('%Y%m%d_%H%M%S')
    lbl = input('Rollback label: ') or f'Before starting engine {rb}'
    
    Path(f'rollback_points/{rb}').mkdir(parents=True, exist_ok=True)
    with open(f'rollback_points/{rb}/metadata.json', 'w') as f:
        json.dump({
            'id': rb,
            'label': lbl,
            'task': 'Start Engine',
            'platform': {'1': 'Coinbase', '2': 'OANDA', '3': 'IBKR'}.get(platform),
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f'✅ Rollback point: {rb} - {lbl}\n')
    
    if platform == '1':
        print('🚀 Starting Coinbase Safe Mode Engine...')
        print('\n⚠️ Options:')
        print('  1. Paper mode (safe)')
        print('  2. Live mode (requires PIN 841921)')
        mode = input('Choice: ')
        
        if mode == '1':
            print('\nStarting in PAPER mode...')
            subprocess.Popen(['python3', 'coinbase_safe_mode_engine.py'])
            print('✅ Coinbase engine started (paper mode)')
        elif mode == '2':
            pin = input('Enter PIN: ')
            if pin == '841921':
                print('\nStarting with LIVE authorization...')
                subprocess.Popen(['python3', 'coinbase_safe_mode_engine.py', '--pin', '841921'])
                print('✅ Coinbase engine started (LIVE mode)')
            else:
                print('❌ Invalid PIN')
    elif platform == '2':
        print('🚀 Starting OANDA Practice Engine...')
        subprocess.Popen(['bash', '-c', 'cd /home/ing/RICK/RICK_LIVE_CLEAN && . .env.oanda_only && python3 oanda_trading_engine.py'])
        print('✅ OANDA engine started')
    elif platform == '3':
        print('🚀 Starting IBKR Gateway...')
        print('⚠️ IBKR gateway not yet configured')

print('\n' + '='*80)
