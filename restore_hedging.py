import os

files = [
    'hive/quant_hedge_rules.py',
    'logic/regime_detector.py',
    'rbotzilla_engine.py',
]

print('Restore Hedging: Verifying hedge architecture files...')
for f in files:
    exists = os.path.exists(f)
    print(f, '->', 'OK' if exists else 'MISSING')

print('\nYou can start the engine using:')
print('nohup python3 rbotzilla_engine.py > engine.log 2>&1 &')
print('tail -f engine.log')
