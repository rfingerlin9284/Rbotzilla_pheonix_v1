#!/usr/bin/env python3
"""Interactive rollback point manager."""

import json
from pathlib import Path
from datetime import datetime
import shutil

print('='*80)
print('💾 ROLLBACK POINT MANAGER')
print('='*80 + '\n')

print('📋 MENU:')
print('  1. List all rollback points')
print('  2. Create new rollback point')
print('  3. Restore from rollback point')
print('  4. Delete rollback point')
print('  5. Export rollback point')
print('  0. Exit')

choice = input('\nChoice (0-5): ')

rollback_dir = Path('rollback_points')
rollback_dir.mkdir(exist_ok=True)

if choice == '1':
    print('\n📂 ROLLBACK POINTS:\n')
    points = sorted(rollback_dir.iterdir(), reverse=True)
    
    if not points:
        print('No rollback points found')
    else:
        for i, p in enumerate(points, 1):
            meta_file = p / 'metadata.json'
            if meta_file.exists():
                with open(meta_file) as f:
                    meta = json.load(f)
                print(f"{i}. {meta.get('id')} - {meta.get('label')}")
                print(f"   Task: {meta.get('task', 'Unknown')}")
                print(f"   Time: {meta.get('timestamp', 'Unknown')}\n")
    
    input('Press Enter to continue...')

elif choice == '2':
    print('\n💾 CREATE ROLLBACK POINT')
    lbl = input('Label: ') or f"Manual rollback {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    rb = datetime.now().strftime('%Y%m%d_%H%M%S')
    rb_path = rollback_dir / rb
    rb_path.mkdir(parents=True, exist_ok=True)
    
    # Select what to backup
    print('\n🎯 SELECT WHAT TO BACKUP:')
    print('  1. Critical files only')
    print('  2. All configuration files')
    print('  3. Full system snapshot')
    
    backup = input('Choice (1-3): ')
    
    files_map = {
        '1': ['foundation/rick_charter.py', 'logic/smart_logic.py', 'hive/rick_hive_mind.py'],
        '2': ['foundation/rick_charter.py', 'logic/smart_logic.py', 'hive/rick_hive_mind.py', '.env.coinbase_advanced', '.env.oanda_only', '.vscode/tasks.json'],
        '3': ['coinbase_safe_mode_engine.py', 'oanda_trading_engine.py', 'foundation/rick_charter.py', 'logic/smart_logic.py', 'hive/rick_hive_mind.py', '.env.coinbase_advanced', '.env.oanda_only', '.vscode/tasks.json', 'safe_mode_manager.py']
    }
    
    files = files_map.get(backup, files_map['1'])
    
    for file in files:
        src = Path(file)
        if src.exists():
            dst = rb_path / file
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    
    with open(rb_path / 'metadata.json', 'w') as f:
        json.dump({
            'id': rb,
            'label': lbl,
            'task': 'Manual Rollback',
            'backup_type': {'1': 'Critical', '2': 'Config', '3': 'Full'}.get(backup),
            'files_backed_up': files,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f'\n✅ Rollback point created:')
    print(f'   ID: {rb}')
    print(f'   Label: {lbl}')
    print(f'   Files backed up: {len(files)}')

elif choice == '3':
    print('\n♻️ RESTORE FROM ROLLBACK')
    points = sorted(rollback_dir.iterdir(), reverse=True)
    
    if not points:
        print('No rollback points found')
    else:
        for i, p in enumerate(points, 1):
            meta_file = p / 'metadata.json'
            if meta_file.exists():
                with open(meta_file) as f:
                    meta = json.load(f)
                print(f"{i}. {meta.get('label')} ({meta.get('id')})")
        
        idx = input(f'\nSelect rollback point (1-{len(points)}) or 0 to cancel: ')
        
        if idx != '0' and idx.isdigit() and 1 <= int(idx) <= len(points):
            selected = points[int(idx) - 1]
            
            with open(selected / 'metadata.json') as f:
                meta = json.load(f)
            
            print(f"\n⚠️ You are about to restore: {meta.get('label')}")
            confirm = input('Type RESTORE to confirm: ')
            
            if confirm == 'RESTORE':
                # Restore files
                for file in selected.rglob('*'):
                    if file.is_file() and file.name != 'metadata.json':
                        rel_path = file.relative_to(selected)
                        dst = Path(rel_path)
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file, dst)
                        print(f'  ✅ Restored: {rel_path}')
                
                print(f'\n✅ System restored from: {meta.get("id")}')
            else:
                print('❌ Cancelled')

elif choice == '4':
    print('\n🗑️ DELETE ROLLBACK POINT')
    points = sorted(rollback_dir.iterdir(), reverse=True)
    
    if not points:
        print('No rollback points found')
    else:
        for i, p in enumerate(points, 1):
            meta_file = p / 'metadata.json'
            if meta_file.exists():
                with open(meta_file) as f:
                    meta = json.load(f)
                print(f"{i}. {meta.get('label')} ({meta.get('id')})")
        
        idx = input(f'\nSelect point to delete (1-{len(points)}) or 0 to cancel: ')
        
        if idx != '0' and idx.isdigit() and 1 <= int(idx) <= len(points):
            selected = points[int(idx) - 1]
            
            with open(selected / 'metadata.json') as f:
                meta = json.load(f)
            
            print(f"\n⚠️ You are about to DELETE: {meta.get('label')}")
            confirm = input('Type DELETE to confirm: ')
            
            if confirm == 'DELETE':
                shutil.rmtree(selected)
                print(f'✅ Deleted: {meta.get("id")}')
            else:
                print('❌ Cancelled')

elif choice == '5':
    print('\n📦 EXPORT ROLLBACK POINT')
    points = sorted(rollback_dir.iterdir(), reverse=True)
    
    if not points:
        print('No rollback points found')
    else:
        for i, p in enumerate(points, 1):
            meta_file = p / 'metadata.json'
            if meta_file.exists():
                with open(meta_file) as f:
                    meta = json.load(f)
                print(f"{i}. {meta.get('label')} ({meta.get('id')})")
        
        idx = input(f'\nSelect point to export (1-{len(points)}) or 0 to cancel: ')
        
        if idx != '0' and idx.isdigit() and 1 <= int(idx) <= len(points):
            selected = points[int(idx) - 1]
            export_name = input('Export filename (without .tar.gz): ') or f"rollback_{selected.name}"
            
            import subprocess
            subprocess.run(['tar', '-czf', f'{export_name}.tar.gz', '-C', str(selected.parent), selected.name])
            print(f'✅ Exported: {export_name}.tar.gz')

else:
    print('✅ Exiting')
