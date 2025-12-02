#!/usr/bin/env python3
"""
Lightweight Terminal Display for RICK Trading System (minimal subset)
This runtime-friendly variant provides the display functions used by engines
and avoids heavy terminal dependencies.
"""
import os
import time


class Colors:
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    WHITE = '\033[37m'
    RESET = '\033[0m'


class TerminalDisplay:
    @staticmethod
    def header(title: str, subtitle: str = None):
        print(f"\n{title} - {subtitle if subtitle else ''}\n")

    @staticmethod
    def section(title: str):
        print(f"\n== {title} ==\n")

    @staticmethod
    def info(label: str, value: str, color=Colors.WHITE):
        print(f"  • {label}: {value}")

    @staticmethod
    def success(message: str):
        print(f"[OK] {message}")

    @staticmethod
    def error(message: str):
        print(f"[ERR] {message}")

    @staticmethod
    def warning(message: str):
        print(f"[WARN] {message}")

    @staticmethod
    def trade_open(symbol: str, direction: str, price: float, details: str = ""):
        print(f"OPEN {symbol} {direction} @ {price:.5f} -- {details}")

    @staticmethod
    def trade_win(symbol: str, pnl: float, details: str = ""):
        print(f"WIN  {symbol} +${pnl:.2f} {details}")

    @staticmethod
    def trade_loss(symbol: str, pnl: float, details: str = ""):
        print(f"LOSS {symbol} -${abs(pnl):.2f} {details}")

    @staticmethod
    def connection_status(broker: str, status: str):
        print(f"{broker} -> {status}")

    @staticmethod
    def market_data(symbol: str, bid: float, ask: float, spread: float):
        print(f"{symbol} BID:{bid:.5f} ASK:{ask:.5f} SPREAD:{spread}")

    @staticmethod
    def alert(message: str, level: str = "INFO"):
        print(f"[{level}] {message}")

    @staticmethod
    def rick_says(message: str):
        print(f"RICK: {message}")

    @staticmethod
    def clear_screen():
        os.system('clear' if os.name != 'nt' else 'cls')

    @staticmethod
    def divider(char='─', length=80):
        print(char * length)

    @staticmethod
    def stats_panel(stats: dict):
        for k, v in stats.items():
            print(f"{k}: {v}")
