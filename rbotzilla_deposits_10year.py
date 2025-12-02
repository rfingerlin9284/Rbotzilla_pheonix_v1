#!/usr/bin/env python3
"""
Monthly Deposit Simulation for 10 years without hedging
"""

from datetime import datetime
from typing import Optional
from enhanced_rick_engine import EnhancedStochasticEngine
import asyncio

class RBOTzillaMonthlyDeposits:
    def __init__(self,
                 initial_capital: float = 30000.0,
                 monthly_deposit: float = 1000.0,
                 reinvestment_rate: float = 0.85,
                 pin: int = 841921):

        self.capital = initial_capital
        self.monthly_deposit = monthly_deposit
        self.reinvestment_rate = reinvestment_rate
        self.withdrawal_rate = 1.0 - reinvestment_rate

        self.total_deposited = initial_capital
        self.total_withdrawn = 0.0

        self.engine = EnhancedStochasticEngine(pin)

    def process_monthly_deposit(self, month: int):
        """Add monthly deposit and withdraw according to rules"""
        self.capital += self.monthly_deposit
        self.total_deposited += self.monthly_deposit

        monthly_profit = self.capital - self.total_deposited + self.total_withdrawn

        if monthly_profit > 0:
            withdrawal = monthly_profit * self.withdrawal_rate
            self.capital -= withdrawal
            self.total_withdrawn += withdrawal

    async def run_10_years(self):
        total_months = 120

        for month in range(total_months):
            self.process_monthly_deposit(month)

            # Simulate 30 trading days per month -> 14 trades/day
            for day in range(30):
                for _ in range(14):
                    await self.engine.execute_enhanced_trade()

        return {
            'final_capital': self.engine.current_capital,
            'total_deposited': self.total_deposited,
            'total_withdrawn': self.total_withdrawn
        }

if __name__ == '__main__':
    import asyncio
    async def main():
        sim = RBOTzillaMonthlyDeposits(initial_capital=30000.0, monthly_deposit=1000.0, reinvestment_rate=0.85, pin=841921)
        res = await sim.run_10_years()
        print('DONE', res)
    asyncio.run(main())
