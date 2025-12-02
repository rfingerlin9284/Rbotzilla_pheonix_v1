#!/usr/bin/env python3
"""
Threshold Backtest - SIMULATION ONLY
Tests different momentum thresholds against historical trade data
Does NOT modify live bot - pure analysis
"""

import requests
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

def calculate_indicators(closes):
    """Calculate SMA20, SMA50, and momentum from price data"""
    if len(closes) < 50:
        return None, None, None
    
    sma20 = sum(closes[-20:]) / 20
    sma50 = sum(closes[-50:]) / 50
    
    if len(closes) >= 11:
        momentum = ((closes[-1] - closes[-11]) / closes[-11]) * 100
    else:
        momentum = 0
    
    return sma20, sma50, momentum

def would_trigger_at_threshold(sma20, sma50, momentum, threshold):
    """Check if signal would trigger at given threshold"""
    if sma20 > sma50 and momentum > threshold:
        return 'BUY'
    elif sma20 < sma50 and momentum < -threshold:
        return 'SELL'
    return None

def main():
    # Load credentials
    api = 'https://api-fxpractice.oanda.com'
    token = os.environ.get('OANDA_PRACTICE_TOKEN', '')
    acct = os.environ.get('OANDA_PRACTICE_ACCOUNT_ID', '')
    
    if not token or not acct:
        print("❌ ERROR: OANDA credentials not found")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    print('='*80)
    print('🧪 MOMENTUM THRESHOLD BACKTEST (SIMULATION)')
    print('='*80)
    print('\nTesting thresholds: 0.10%, 0.12%, 0.13%, 0.15% (current), 0.18%')
    print('Looking back: 30 days of historical data\n')
    
    # Test thresholds
    thresholds = [0.10, 0.12, 0.13, 0.15, 0.18]
    
    # Get historical transactions
    since = (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z'
    
    try:
        r = requests.get(f'{api}/v3/accounts/{acct}/transactions', 
                        headers=headers, 
                        params={'from': since})
        transactions = r.json().get('transactions', [])
    except Exception as e:
        print(f"❌ API Error: {e}")
        return
    
    # Get list of traded instruments
    instruments = set()
    for tx in transactions:
        if tx.get('type') == 'ORDER_FILL':
            inst = tx.get('instrument')
            if inst:
                instruments.add(inst)
    
    if not instruments:
        instruments = {'EUR_USD', 'GBP_USD', 'USD_JPY', 'NZD_CHF'}
    
    print(f"Analyzing {len(instruments)} instruments from trade history...")
    print(f"Instruments: {', '.join(sorted(instruments))}\n")
    
    # Results per threshold
    results = {th: {'signals': 0, 'trades': [], 'near_misses': 0} for th in thresholds}
    
    # Analyze each instrument
    for instrument in sorted(instruments):
        try:
            # Get historical candles (M15, 500 max)
            r = requests.get(f'{api}/v3/instruments/{instrument}/candles', 
                            headers=headers, 
                            params={'granularity': 'M15', 'count': 500})
            candles = r.json().get('candles', [])
            
            if len(candles) < 60:
                continue
            
            # Analyze each candle for signal potential
            for i in range(60, len(candles)):
                window = candles[i-60:i]
                closes = [float(c['mid']['c']) for c in window if c.get('complete')]
                
                if len(closes) < 50:
                    continue
                
                sma20, sma50, momentum = calculate_indicators(closes)
                
                if sma20 is None:
                    continue
                
                # Test each threshold
                for threshold in thresholds:
                    signal = would_trigger_at_threshold(sma20, sma50, momentum, threshold)
                    if signal:
                        results[threshold]['signals'] += 1
                        results[threshold]['trades'].append({
                            'instrument': instrument,
                            'signal': signal,
                            'momentum': momentum,
                            'time': candles[i].get('time')
                        })
        
        except Exception as e:
            continue
    
    # Display results
    print('='*80)
    print('📊 BACKTEST RESULTS BY THRESHOLD')
    print('='*80)
    
    for threshold in thresholds:
        current_marker = " ⬅️ CURRENT" if threshold == 0.15 else ""
        signal_count = results[threshold]['signals']
        
        print(f"\n{'─'*80}")
        print(f"Threshold: {threshold:.2f}%{current_marker}")
        print(f"{'─'*80}")
        print(f"Total signals generated: {signal_count}")
        
        if signal_count > 0:
            # Count by instrument
            by_instrument = defaultdict(int)
            for trade in results[threshold]['trades']:
                by_instrument[trade['instrument']] += 1
            
            print(f"\nTop 5 most active pairs:")
            sorted_pairs = sorted(by_instrument.items(), key=lambda x: x[1], reverse=True)[:5]
            for pair, count in sorted_pairs:
                pct = (count / signal_count) * 100
                print(f"  {pair}: {count} signals ({pct:.1f}%)")
            
            # Calculate signal density
            signals_per_day = signal_count / 30
            print(f"\nAverage signals per day: {signals_per_day:.1f}")
            
            # Compare to current threshold
            if threshold != 0.15:
                current_signals = results[0.15]['signals']
                if current_signals > 0:
                    pct_change = ((signal_count - current_signals) / current_signals) * 100
                    if pct_change > 0:
                        print(f"⬆️  +{pct_change:.1f}% MORE signals than current threshold")
                    else:
                        print(f"⬇️  ({abs(pct_change):.1f}%) FEWER signals than current threshold")
    
    # Recommendations
    print('\n' + '='*80)
    print('💡 RECOMMENDATIONS')
    print('='*80)
    
    current_signals = results[0.15]['signals']
    
    for threshold in [0.10, 0.12, 0.13]:
        signals = results[threshold]['signals']
        increase = signals - current_signals
        pct_increase = (increase / current_signals * 100) if current_signals > 0 else 0
        
        print(f"\n{threshold:.2f}% threshold:")
        if increase >= 0:
            print(f"  • Would generate {increase} additional signals (+{pct_increase:.1f}%)")
            print(f"  • Approximately +{increase/30:.1f} extra signals per day")
        else:
            print(f"  • Would generate {abs(increase)} fewer signals (({abs(pct_increase):.1f}%))")
            print(f"  • Approximately ({abs(increase)/30:.1f}) fewer signals per day")
        
        if pct_increase > 50:
            print(f"  ⚠️  WARNING: >50% increase may flood with false signals")
        elif pct_increase > 30:
            print(f"  ⚠️  CAUTION: Significant increase - test carefully")
        elif pct_increase > 15:
            print(f"  ✅ REASONABLE: Moderate increase worth testing")
        else:
            print(f"  ℹ️  MINIMAL: Small impact")
    
    print('\n' + '='*80)
    print('🚨 IMPORTANT NOTES')
    print('='*80)
    print('• This is SIMULATION ONLY - no live trades affected')
    print('• More signals ≠ more profit (may include false signals)')
    print('• Must backtest with actual P&L to determine optimal threshold')
    print('• Recommended: Test 0.12% in paper trading for 1 week minimum')
    print('• Never change live threshold without testing first')
    print('\n' + '='*80)
    
    # Save to CSV
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    csv_file = f'logs/analysis/threshold_backtest_{timestamp}.csv'
    
    try:
        with open(csv_file, 'w') as f:
            f.write('threshold,total_signals,signals_per_day,pct_vs_current\n')
            for threshold in thresholds:
                signals = results[threshold]['signals']
                per_day = signals / 30
                pct_vs_current = ((signals - current_signals) / current_signals * 100) if current_signals > 0 else 0
                f.write(f'{threshold:.2f},{signals},{per_day:.2f},{pct_vs_current:.1f}\n')
        
        print(f'📁 Results saved to: {csv_file}')
    except:
        print('⚠️  Could not save CSV (logs/analysis directory may not exist)')

if __name__ == '__main__':
    main()
