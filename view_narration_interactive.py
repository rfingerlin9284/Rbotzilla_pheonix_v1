#!/usr/bin/env python3
"""Interactive narration viewer with multiple viewing options."""

import subprocess
from pathlib import Path
import json
from datetime import datetime

print('='*80)
print('📊 VIEW NARRATION')
print('='*80 + '\n')

print('🎯 SELECT NARRATION SOURCE:')
print('  1. Live stream (real-time)')
print('  2. Last 20 events')
print('  3. Last 50 events')
print('  4. Save current narration to file')
print('  5. Search narration')
print('  0. Exit')

choice = input('\nChoice (0-5): ')

if choice == '1':
    print('\n📡 LIVE NARRATION STREAM')
    print('Press Ctrl+C to stop\n')
    subprocess.run(['tail', '-f', 'logs/narration.jsonl'])
elif choice == '2':
    print('\n📋 LAST 20 EVENTS:\n')
    subprocess.run(['tail', '-20', 'logs/narration.jsonl'])
    input('\nPress Enter to continue...')
elif choice == '3':
    print('\n📋 LAST 50 EVENTS:\n')
    subprocess.run(['tail', '-50', 'logs/narration.jsonl'])
    input('\nPress Enter to continue...')
elif choice == '4':
    fn = input('Save to filename: ') or f"narration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    Path('results').mkdir(exist_ok=True)
    subprocess.run(['cp', 'logs/narration.jsonl', f'results/{fn}'])
    print(f'✅ Saved: results/{fn}')
elif choice == '5':
    term = input('Search term: ')
    print(f'\n🔍 Searching for "{term}"...\n')
    subprocess.run(['grep', '-i', term, 'logs/narration.jsonl'])
    input('\nPress Enter to continue...')
else:
    print('✅ Exiting')
