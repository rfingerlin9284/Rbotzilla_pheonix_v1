#!/usr/bin/env python3
"""
Market Opportunities Analysis - Read-Only
Identifies current signals and near-miss opportunities
"""

import requests
import os
import json

def main():
    # Load credentials
    api = 'https://api-fxpractice.oanda.com'
    token = os.environ.get('OANDA_PRACTICE_TOKEN', '')
    acct = os.environ.get('OANDA_PRACTICE_ACCOUNT_ID', '')
    
    if not token or not acct:
        print("❌ ERROR: OANDA credentials not found")
        print("Run: source .env.oanda_only")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    print('='*80)
    print('🔍 CURRENT MARKET OPPORTUNITIES ANALYSIS')
    print('='*80)
    print('\nAnalyzing momentum signals (SMA 20/50 + momentum threshold 0.15%)...\n')
    
    # Major forex pairs
    instruments = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD', 'NZD_USD', 
                   'USD_CHF', 'EUR_GBP', 'NZD_CHF', 'AUD_JPY', 'GBP_JPY']
    
    active_signals = []
    near_misses = []
    
    for instrument in instruments:
        try:
            # Get M15 candles (need 60 to calculate SMA50)
            r = requests.get(f'{api}/v3/instruments/{instrument}/candles', 
                            headers=headers, 
                            params={'granularity': 'M15', 'count': 60})
            candles = r.json().get('candles', [])
            
            if len(candles) < 50:
                continue
            
            # Calculate indicators
            closes = [float(c['mid']['c']) for c in candles if c.get('complete')]
            
            if len(closes) < 50:
                continue
            
            # SMA 20 and SMA 50
            sma20 = sum(closes[-20:]) / 20
            sma50 = sum(closes[-50:]) / 50
            
            # Momentum (10-period rate of change)
            if len(closes) >= 11:
                momentum = ((closes[-1] - closes[-11]) / closes[-11]) * 100
            else:
                momentum = 0
            
            current_price = closes[-1]
            
            # Check if signal would trigger
            signal = None
            if sma20 > sma50 and momentum > 0.15:
                signal = 'BUY'
                active_signals.append({
                    'instrument': instrument,
                    'signal': signal,
                    'price': current_price,
                    'sma20': sma20,
                    'sma50': sma50,
                    'momentum': momentum
                })
            elif sma20 < sma50 and momentum < -0.15:
                signal = 'SELL'
                active_signals.append({
                    'instrument': instrument,
                    'signal': signal,
                    'price': current_price,
                    'sma20': sma20,
                    'sma50': sma50,
                    'momentum': momentum
                })
            
            # Check near-miss (almost triggered but didn't meet threshold)
            near_miss = None
            near_miss_type = None
            if sma20 > sma50 and 0 < momentum < 0.15:
                near_miss = f'momentum {momentum:.3f}% < 0.15%'
                near_miss_type = 'ALMOST BUY'
                near_misses.append({
                    'instrument': instrument,
                    'type': near_miss_type,
                    'reason': near_miss,
                    'price': current_price,
                    'sma20': sma20,
                    'sma50': sma50,
                    'momentum': momentum
                })
            elif sma20 < sma50 and -0.15 < momentum < 0:
                near_miss = f'momentum {momentum:.3f}% > -0.15%'
                near_miss_type = 'ALMOST SELL'
                near_misses.append({
                    'instrument': instrument,
                    'type': near_miss_type,
                    'reason': near_miss,
                    'price': current_price,
                    'sma20': sma20,
                    'sma50': sma50,
                    'momentum': momentum
                })
                
        except Exception as e:
            continue
    
    # Display results
    if active_signals:
        print(f'🎯 ACTIVE SIGNALS ({len(active_signals)}):')
        print('-' * 80)
        for s in active_signals:
            print(f"\n{s['instrument']}: {s['signal']}")
            print(f"  Price: {s['price']:.5f}")
            print(f"  SMA20: {s['sma20']:.5f}")
            print(f"  SMA50: {s['sma50']:.5f}")
            print(f"  Momentum: {s['momentum']:.3f}%")
    else:
        print('🎯 ACTIVE SIGNALS: None')
    
    print('\n' + '='*80)
    
    if near_misses:
        print(f'\n⚠️  NEAR-MISS OPPORTUNITIES ({len(near_misses)}):')
        print('-' * 80)
        print('These would have triggered with a lower momentum threshold:\n')
        for nm in near_misses:
            print(f"{nm['instrument']}: {nm['type']}")
            print(f"  Price: {nm['price']:.5f}")
            print(f"  SMA20: {nm['sma20']:.5f}")
            print(f"  SMA50: {nm['sma50']:.5f}")
            print(f"  Momentum: {nm['momentum']:.3f}% ({nm['reason']})")
            
            # Calculate what threshold would have caught this
            abs_momentum = abs(nm['momentum'])
            print(f"  💡 Would trigger with threshold: {abs_momentum:.3f}%\n")
    else:
        print('\n⚠️  NEAR-MISS OPPORTUNITIES: None')
    
    # Analysis summary
    print('\n' + '='*80)
    print('📋 ANALYSIS SUMMARY:')
    print('-' * 80)
    print(f'Total pairs analyzed: {len(instruments)}')
    print(f'Active signals found: {len(active_signals)}')
    print(f'Near-miss opportunities: {len(near_misses)}')
    
    if near_misses:
        avg_near_miss_momentum = sum(abs(nm['momentum']) for nm in near_misses) / len(near_misses)
        print(f'\n💡 Average near-miss momentum: {avg_near_miss_momentum:.3f}%')
        print(f'   Current threshold: 0.15%')
        print(f'   Suggestion: Test threshold between 0.10% - 0.13% in backtest')
    
    print('\n' + '='*80)

if __name__ == '__main__':
    main()
