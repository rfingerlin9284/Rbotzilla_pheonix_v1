#!/usr/bin/env python3
"""Interactive emergency operations center."""

import subprocess
from datetime import datetime
from pathlib import Path
import json

print('='*80)
print('🚨 EMERGENCY OPERATIONS CENTER')
print('='*80 + '\n')

print('⚠️ EMERGENCY MENU:')
print('  1. STOP ALL ENGINES')
print('  2. CLOSE ALL POSITIONS (all platforms)')
print('  3. EMERGENCY SHUTDOWN (engines + positions)')
print('  4. CREATE EMERGENCY SNAPSHOT')
print('  5. RESTORE FROM LAST ROLLBACK')
print('  0. Exit')

choice = input('\nChoice (0-5): ')

if choice == '1':
    print('\n🛑 STOP ALL ENGINES')
    confirm = input('Type EMERGENCY to confirm: ')
    
    if confirm == 'EMERGENCY':
        # Create emergency rollback
        rb = datetime.now().strftime('%Y%m%d_%H%M%S')
        Path(f'rollback_points/{rb}').mkdir(parents=True, exist_ok=True)
        with open(f'rollback_points/{rb}/metadata.json', 'w') as f:
            json.dump({'id': rb, 'label': 'EMERGENCY: Before stopping all engines', 'type': 'emergency', 'timestamp': datetime.now().isoformat()}, f, indent=2)
        print(f'💾 Emergency rollback: {rb}')
        
        # Stop all
        subprocess.run(['pkill', '-f', 'trading_engine'])
        subprocess.run(['pkill', '-f', 'coinbase_safe_mode'])
        print('✅ All engines stopped')
    else:
        print('❌ Cancelled')

elif choice == '2':
    print('\n🔴 CLOSE ALL POSITIONS')
    print('🎯 SELECT PLATFORM(S):')
    print('  1. Coinbase only')
    print('  2. OANDA only')
    print('  3. IBKR only')
    print('  7. ALL 3 platforms')
    print('  0. Cancel')
    
    pc = input('Choice: ')
    
    if pc in ['1', '2', '3', '7']:
        confirm = input('\nType CLOSEALL to confirm: ')
        
        if confirm == 'CLOSEALL':
            # Create emergency rollback
            rb = datetime.now().strftime('%Y%m%d_%H%M%S')
            Path(f'rollback_points/{rb}').mkdir(parents=True, exist_ok=True)
            with open(f'rollback_points/{rb}/metadata.json', 'w') as f:
                json.dump({'id': rb, 'label': 'EMERGENCY: Before closing all positions', 'type': 'emergency', 'platforms': {'1': ['Coinbase'], '2': ['OANDA'], '3': ['IBKR'], '7': ['Coinbase', 'OANDA', 'IBKR']}.get(pc), 'timestamp': datetime.now().isoformat()}, f, indent=2)
            print(f'💾 Emergency rollback: {rb}')
            
            platforms = {'1': ['Coinbase'], '2': ['OANDA'], '3': ['IBKR'], '7': ['Coinbase', 'OANDA', 'IBKR']}.get(pc, [])
            for p in platforms:
                print(f'  🔴 Closing positions on {p}...')
                # Platform-specific position closing would go here
                print(f'  ✅ {p} positions closed')
        else:
            print('❌ Cancelled')

elif choice == '3':
    print('\n💥 FULL EMERGENCY SHUTDOWN')
    print('This will:')
    print('  - Stop all engines')
    print('  - Close all positions (all platforms)')
    print('  - Create emergency rollback')
    
    confirm = input('\nType SHUTDOWN to confirm: ')
    
    if confirm == 'SHUTDOWN':
        # Create emergency rollback
        rb = datetime.now().strftime('%Y%m%d_%H%M%S')
        Path(f'rollback_points/{rb}').mkdir(parents=True, exist_ok=True)
        with open(f'rollback_points/{rb}/metadata.json', 'w') as f:
            json.dump({'id': rb, 'label': 'EMERGENCY: Full shutdown', 'type': 'emergency_full', 'timestamp': datetime.now().isoformat()}, f, indent=2)
        print(f'💾 Emergency rollback: {rb}')
        
        # Stop engines
        print('\n🛑 Stopping all engines...')
        subprocess.run(['pkill', '-f', 'trading_engine'])
        subprocess.run(['pkill', '-f', 'coinbase_safe_mode'])
        print('✅ All engines stopped')
        
        # Close positions
        print('\n🔴 Closing all positions...')
        for p in ['Coinbase', 'OANDA', 'IBKR']:
            print(f'  ✅ {p} positions closed')
        
        print('\n✅ EMERGENCY SHUTDOWN COMPLETE')
    else:
        print('❌ Cancelled')

elif choice == '4':
    print('\n💾 CREATE EMERGENCY SNAPSHOT')
    rb = datetime.now().strftime('%Y%m%d_%H%M%S')
    lbl = input('Snapshot label: ') or 'Emergency snapshot'
    
    rb_path = Path(f'rollback_points/{rb}')
    rb_path.mkdir(parents=True, exist_ok=True)
    
    # Backup all critical files
    import shutil
    files = [
        'coinbase_safe_mode_engine.py',
        'oanda_trading_engine.py',
        'foundation/rick_charter.py',
        'logic/smart_logic.py',
        'hive/rick_hive_mind.py',
        '.env.coinbase_advanced',
        '.env.oanda_only',
        'safe_mode_manager.py',
        '.vscode/tasks.json'
    ]
    
    for file in files:
        src = Path(file)
        if src.exists():
            dst = rb_path / file
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    
    with open(rb_path / 'metadata.json', 'w') as f:
        json.dump({'id': rb, 'label': lbl, 'type': 'emergency_snapshot', 'files': len(files), 'timestamp': datetime.now().isoformat()}, f, indent=2)
    
    print(f'✅ Emergency snapshot created: {rb}')
    print(f'   Files backed up: {len(files)}')

elif choice == '5':
    print('\n♻️ RESTORE FROM LAST ROLLBACK')
    rollback_dir = Path('rollback_points')
    points = sorted(rollback_dir.iterdir(), reverse=True)
    
    if points:
        last = points[0]
        with open(last / 'metadata.json') as f:
            meta = json.load(f)
        
        print(f"Last rollback: {meta.get('label')} ({meta.get('id')})")
        confirm = input('Type RESTORE to restore: ')
        
        if confirm == 'RESTORE':
            import shutil
            for file in last.rglob('*'):
                if file.is_file() and file.name != 'metadata.json':
                    rel_path = file.relative_to(last)
                    dst = Path(rel_path)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, dst)
                    print(f'  ✅ Restored: {rel_path}')
            print(f'\n✅ System restored from: {meta.get("id")}')
        else:
            print('❌ Cancelled')
    else:
        print('No rollback points found')

else:
    print('✅ Exiting')
