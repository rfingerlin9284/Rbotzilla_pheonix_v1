#!/usr/bin/env python3
"""Interactive safe mode progression viewer."""

import json
from pathlib import Path
from datetime import datetime

print('='*80)
print('📈 SAFE MODE PROGRESSION')
print('='*80 + '\n')

perf_file = Path('logs/safe_mode_performance.json')

if perf_file.exists():
    with open(perf_file) as f:
        data = json.load(f)
    
    print(f"Win Rate: {data.get('win_rate', 0):.1%} (need: 65%)")
    print(f"Profit Factor: {data.get('profit_factor', 0):.2f} (need: 1.8)")
    print(f"Total Trades: {data.get('total_trades', 0)} (need: 50)")
    print(f"Consecutive Days: {data.get('consecutive_days', 0)} (need: 7)")
    print(f"\nCurrent Status: {data.get('status', 'PAPER')}")
else:
    data = {'win_rate': 0, 'profit_factor': 0, 'total_trades': 0, 'consecutive_days': 0, 'status': 'PAPER'}
    print('No performance data yet')
    print('Start trading to build track record')

print('\n' + '='*80)
print('\n📋 ACTION MENU:')
print('  1. Save progress report')
print('  2. View detailed statistics')
print('  3. Export for analysis')
print('  4. Reset progress (requires PIN)')
print('  5. Exit')

choice = input('\nChoice (1-5): ')

if choice == '1':
    Path('results').mkdir(exist_ok=True)
    fn = input('Report filename: ') or f"progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(f'results/{fn}', 'w') as f:
        json.dump({'timestamp': datetime.now().isoformat(), 'progress': data}, f, indent=2)
    print(f'✅ Saved: results/{fn}')
elif choice == '2':
    print('\n📊 DETAILED STATISTICS:\n')
    print(json.dumps(data, indent=2))
    input('\nPress Enter to continue...')
elif choice == '3':
    fn = input('Export filename (.csv): ') or f"progress_export_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(f'results/{fn}', 'w') as f:
        f.write('Metric,Value,Threshold,Status\n')
        f.write(f"Win Rate,{data.get('win_rate', 0):.1%},65%,{'✅' if data.get('win_rate', 0) >= 0.65 else '❌'}\n")
        f.write(f"Profit Factor,{data.get('profit_factor', 0):.2f},1.8,{'✅' if data.get('profit_factor', 0) >= 1.8 else '❌'}\n")
        f.write(f"Total Trades,{data.get('total_trades', 0)},50,{'✅' if data.get('total_trades', 0) >= 50 else '❌'}\n")
        f.write(f"Consecutive Days,{data.get('consecutive_days', 0)},7,{'✅' if data.get('consecutive_days', 0) >= 7 else '❌'}\n")
    print(f'✅ Exported: results/{fn}')
elif choice == '4':
    pin = input('Enter PIN to reset: ')
    if pin == '841921':
        confirm = input('Type RESET to confirm: ')
        if confirm == 'RESET':
            # Backup current progress
            rb = datetime.now().strftime('%Y%m%d_%H%M%S')
            Path(f'rollback_points/{rb}').mkdir(parents=True, exist_ok=True)
            with open(f'rollback_points/{rb}/metadata.json', 'w') as f:
                json.dump({'id': rb, 'label': 'Before progress reset', 'old_progress': data, 'timestamp': datetime.now().isoformat()}, f, indent=2)
            
            # Reset
            new_data = {'win_rate': 0, 'profit_factor': 0, 'total_trades': 0, 'consecutive_days': 0, 'status': 'PAPER'}
            with open(perf_file, 'w') as f:
                json.dump(new_data, f, indent=2)
            
            print(f'✅ Progress reset')
            print(f'💾 Rollback created: {rb}')
        else:
            print('❌ Cancelled')
    else:
        print('❌ Invalid PIN')
else:
    print('✅ Exiting')
