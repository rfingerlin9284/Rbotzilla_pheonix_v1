#!/usr/bin/env python3
"""
Trade Performance Analysis - Read-Only
Analyzes closed trades and identifies missed opportunities
"""

import requests
import os
import json
from datetime import datetime, timedelta

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
    print('📊 TRADE PERFORMANCE ANALYSIS')
    print('='*80)
    
    # Get closed trades from last 30 days
    since = (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z'
    
    try:
        r = requests.get(f'{api}/v3/accounts/{acct}/transactions', 
                        headers=headers, 
                        params={'from': since, 'type': 'ORDER_FILL'})
        transactions = r.json().get('transactions', [])
    except Exception as e:
        print(f"❌ API Error: {e}")
        return
    
    print(f'\n📋 Found {len(transactions)} order fills in last 30 days\n')
    
    # Analyze trades
    winning_trades = []
    losing_trades = []
    breakeven_trades = []
    
    for tx in transactions:
        if tx.get('type') == 'ORDER_FILL':
            pl = float(tx.get('pl', 0))
            instrument = tx.get('instrument', 'Unknown')
            units = tx.get('units', '0')
            price = tx.get('price', '0')
            time = tx.get('time', '')
            
            if pl > 0:
                winning_trades.append((instrument, pl, units, price, time))
            elif pl < 0:
                losing_trades.append((instrument, pl, units, price, time))
            else:
                breakeven_trades.append((instrument, pl, units, price, time))
    
    print(f'✅ Winning Trades: {len(winning_trades)}')
    print(f'❌ Losing Trades: {len(losing_trades)}')
    print(f'➖ Breakeven Trades: {len(breakeven_trades)}')
    
    if winning_trades:
        total_wins = sum(t[1] for t in winning_trades)
        avg_win = total_wins / len(winning_trades)
        print(f'\n💰 Total Profit: ${total_wins:.2f}')
        print(f'   Average Win: ${avg_win:.2f}')
        
        # Show top 5 wins
        print('\n   Top 5 Wins:')
        top_wins = sorted(winning_trades, key=lambda x: x[1], reverse=True)[:5]
        for i, (inst, pl, units, price, time) in enumerate(top_wins, 1):
            units_val = float(units)
            units_display = f"({abs(units_val):,.0f})" if units_val < 0 else f"{units_val:,.0f}"
            print(f'   {i}. {inst}: +${pl:.2f} ({units_display} units @ {price})')
    
    if losing_trades:
        total_losses = sum(t[1] for t in losing_trades)
        avg_loss = total_losses / len(losing_trades)
        loss_display = f"(-${abs(total_losses):.2f})"
        avg_loss_display = f"(-${abs(avg_loss):.2f})"
        print(f'\n💸 Total Loss: {loss_display}')
        print(f'   Average Loss: {avg_loss_display}')
        
        # Show top 5 losses
        print('\n   Top 5 Losses:')
        top_losses = sorted(losing_trades, key=lambda x: x[1])[:5]
        for i, (inst, pl, units, price, time) in enumerate(top_losses, 1):
            units_val = float(units)
            units_display = f"({abs(units_val):,.0f})" if units_val < 0 else f"{units_val:,.0f}"
            pl_display = f"(-${abs(pl):.2f})"
            print(f'   {i}. {inst}: {pl_display} ({units_display} units @ {price})')
    
    if winning_trades and losing_trades:
        win_rate = len(winning_trades) / (len(winning_trades) + len(losing_trades)) * 100
        profit_factor = abs(total_wins / total_losses) if total_losses != 0 else 0
        print(f'\n📈 Win Rate: {win_rate:.1f}%')
        print(f'📊 Profit Factor: {profit_factor:.2f}')
        
        if win_rate >= 60:
            print('   ✅ Win rate is good (>60%)')
        elif win_rate >= 50:
            print('   ⚠️  Win rate is acceptable (50-60%)')
        else:
            print('   ❌ Win rate needs improvement (<50%)')
        
        if profit_factor >= 2.0:
            print('   ✅ Profit factor is excellent (>2.0)')
        elif profit_factor >= 1.5:
            print('   ⚠️  Profit factor is acceptable (1.5-2.0)')
        else:
            print('   ❌ Profit factor needs improvement (<1.5)')
    
    print('\n' + '='*80)

if __name__ == '__main__':
    main()
