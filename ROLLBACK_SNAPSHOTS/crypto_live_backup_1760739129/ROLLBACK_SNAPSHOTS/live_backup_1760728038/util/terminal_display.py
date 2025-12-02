#!/usr/bin/env python3
"""
Beautiful Terminal Display for RICK Trading System
Color-coded, organized, easy-to-read output
"""
import os


class Colors:
    """ANSI color codes for terminal"""
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Reset
    RESET = '\033[0m'
    
    @staticmethod
    def rgb(r, g, b):
        """Custom RGB color"""
        return f'\033[38;2;{r};{g};{b}m'


class TerminalDisplay:
    """Beautifully formatted terminal output"""
    
    @staticmethod
    def header(title: str, subtitle: str = None):
        """Display main header"""
        width = 80
        print("\n" + "=" * width)
        print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{title.center(width)}{Colors.RESET}")
        if subtitle:
            print(f"{Colors.BRIGHT_BLACK}{subtitle.center(width)}{Colors.RESET}")
        print("=" * width + "\n")
    
    @staticmethod
    def section(title: str):
        """Display section header"""
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_YELLOW}{'▶ ' + title}{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}{'─' * 78}{Colors.RESET}")
    
    @staticmethod
    def subsection(title: str):
        """Display subsection"""
        print(f"\n{Colors.CYAN}{'  ► ' + title}{Colors.RESET}")
    
    @staticmethod
    def info(label: str, value: str, color=Colors.WHITE):
        """Display labeled information"""
        print(f"{Colors.BRIGHT_BLACK}  • {Colors.RESET}{Colors.WHITE}{label}:{Colors.RESET} {color}{value}{Colors.RESET}")
    
    @staticmethod
    def success(message: str):
        """Display success message"""
        print(f"{Colors.BRIGHT_GREEN}✅ {message}{Colors.RESET}")
    
    @staticmethod
    def error(message: str):
        """Display error message"""
        print(f"{Colors.BRIGHT_RED}❌ {message}{Colors.RESET}")
    
    @staticmethod
    def warning(message: str):
        """Display warning message"""
        print(f"{Colors.BRIGHT_YELLOW}⚠️  {message}{Colors.RESET}")
    
    @staticmethod
    def trade_win(symbol: str, pnl: float, details: str = ""):
        """Display winning trade"""
        print(f"\n{Colors.BG_GREEN}{Colors.BLACK} WIN {Colors.RESET} "
              f"{Colors.BRIGHT_GREEN}{Colors.BOLD}{symbol}{Colors.RESET} "
              f"{Colors.GREEN}+${pnl:.2f}{Colors.RESET}")
        if details:
            print(f"      {Colors.BRIGHT_BLACK}{details}{Colors.RESET}")
    
    @staticmethod
    def trade_loss(symbol: str, pnl: float, details: str = ""):
        """Display losing trade"""
        print(f"\n{Colors.BG_RED}{Colors.WHITE} LOSS {Colors.RESET} "
              f"{Colors.BRIGHT_RED}{Colors.BOLD}{symbol}{Colors.RESET} "
              f"{Colors.RED}-${abs(pnl):.2f}{Colors.RESET}")
        if details:
            print(f"      {Colors.BRIGHT_BLACK}{details}{Colors.RESET}")
    
    @staticmethod
    def trade_open(symbol: str, direction: str, price: float, details: str = ""):
        """Display trade opened"""
        dir_color = Colors.BRIGHT_GREEN if direction == "BUY" else Colors.BRIGHT_RED
        dir_symbol = "📈" if direction == "BUY" else "📉"
        print(f"\n{Colors.BG_BLUE}{Colors.WHITE} OPEN {Colors.RESET} "
              f"{dir_color}{Colors.BOLD}{symbol} {direction}{Colors.RESET} "
              f"{Colors.CYAN}@ {price:.5f}{Colors.RESET} {dir_symbol}")
        if details:
            print(f"      {Colors.BRIGHT_BLACK}{details}{Colors.RESET}")
    
    @staticmethod
    def stats_panel(stats: dict):
        """Display statistics panel"""
        print(f"\n{Colors.BG_CYAN}{Colors.BLACK} STATISTICS {Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}┌{'─' * 76}┐{Colors.RESET}")
        
        for key, value in stats.items():
            # Determine color based on key
            if "pnl" in key.lower() or "profit" in key.lower():
                color = Colors.BRIGHT_GREEN if float(value.replace('$','').replace('%','').replace(',','')) >= 0 else Colors.BRIGHT_RED
            elif "win" in key.lower():
                color = Colors.BRIGHT_GREEN
            elif "loss" in key.lower():
                color = Colors.BRIGHT_RED
            else:
                color = Colors.BRIGHT_CYAN
            
            print(f"{Colors.BRIGHT_BLACK}│{Colors.RESET} {Colors.WHITE}{key:30}{Colors.RESET} {color}{value:>44}{Colors.RESET} {Colors.BRIGHT_BLACK}│{Colors.RESET}")
        
        print(f"{Colors.BRIGHT_BLACK}└{'─' * 76}┘{Colors.RESET}\n")
    
    @staticmethod
    def rick_says(message: str):
        """Display Rick's commentary"""
        print(f"\n{Colors.BRIGHT_MAGENTA}💬 Rick:{Colors.RESET} {Colors.ITALIC}{Colors.WHITE}{message}{Colors.RESET}")
    
    @staticmethod
    def market_data(symbol: str, bid: float, ask: float, spread: float):
        """Display market data"""
        print(f"  {Colors.BRIGHT_CYAN}📊 {symbol}{Colors.RESET} "
              f"{Colors.GREEN}BID: {bid:.5f}{Colors.RESET} | "
              f"{Colors.RED}ASK: {ask:.5f}{Colors.RESET} | "
              f"{Colors.YELLOW}Spread: {spread:.1f} pips{Colors.RESET}")
    
    @staticmethod
    def connection_status(broker: str, status: str):
        """Display connection status"""
        if status.upper() == "CONNECTED":
            icon = "🟢"
            color = Colors.BRIGHT_GREEN
        elif status.upper() == "CONNECTING":
            icon = "🟡"
            color = Colors.BRIGHT_YELLOW
        else:
            icon = "🔴"
            color = Colors.BRIGHT_RED
        
        print(f"  {icon} {Colors.WHITE}{broker:20}{Colors.RESET} {color}{status.upper()}{Colors.RESET}")
    
    @staticmethod
    def divider(char='─', length=80):
        """Display divider line"""
        print(f"{Colors.BRIGHT_BLACK}{char * length}{Colors.RESET}")
    
    @staticmethod
    def progress_bar(current: int, total: int, label: str = "Progress"):
        """Display progress bar"""
        percentage = (current / total) * 100
        filled = int(percentage / 2)
        bar = '█' * filled + '░' * (50 - filled)
        
        color = Colors.BRIGHT_GREEN if percentage >= 70 else Colors.BRIGHT_YELLOW if percentage >= 40 else Colors.BRIGHT_RED
        
        print(f"\r{Colors.WHITE}{label}:{Colors.RESET} [{color}{bar}{Colors.RESET}] {color}{percentage:.1f}%{Colors.RESET} ({current}/{total})", end='', flush=True)
    
    @staticmethod
    def table_header(columns: list):
        """Display table header"""
        print(f"\n{Colors.BG_CYAN}{Colors.BLACK}", end='')
        for col in columns:
            print(f" {col:^15}", end='')
        print(f"{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}{'─' * (len(columns) * 16)}{Colors.RESET}")
    
    @staticmethod
    def table_row(values: list, colors: list = None):
        """Display table row"""
        if colors is None:
            colors = [Colors.WHITE] * len(values)
        
        for value, color in zip(values, colors):
            print(f"{color} {str(value):^15}{Colors.RESET}", end='')
        print()
    
    @staticmethod
    def alert(message: str, level: str = "INFO"):
        """Display alert"""
        if level == "INFO":
            icon = "ℹ️"
            color = Colors.BRIGHT_CYAN
        elif level == "WARNING":
            icon = "⚠️"
            color = Colors.BRIGHT_YELLOW
        elif level == "ERROR":
            icon = "❌"
            color = Colors.BRIGHT_RED
        elif level == "SUCCESS":
            icon = "✅"
            color = Colors.BRIGHT_GREEN
        else:
            icon = "•"
            color = Colors.WHITE
        
        print(f"\n{color}{icon} {message}{Colors.RESET}")
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    @staticmethod
    def countdown(seconds: int, message: str = "Next action in"):
        """Display countdown timer"""
        for i in range(seconds, 0, -1):
            print(f"\r{Colors.YELLOW}{message}: {i}s{Colors.RESET}", end='', flush=True)
            time.sleep(1)
        print(f"\r{' ' * 50}\r", end='', flush=True)


# Example usage
if __name__ == "__main__":
    import time
    
    display = TerminalDisplay()
    
    # Header
    display.header("🤖 RICK TRADING SYSTEM", "Live Paper Trading Session")
    
    # Connections
    display.section("BROKER CONNECTIONS")
    display.connection_status("OANDA Practice API", "CONNECTED")
    display.connection_status("Coinbase Sandbox", "CONNECTED")
    
    # Market Data
    display.section("MARKET DATA")
    display.market_data("EUR_USD", 1.00564, 1.00567, 0.3)
    display.market_data("GBP_USD", 1.26543, 1.26547, 0.4)
    
    # Trade Example
    display.section("TRADE ACTIVITY")
    display.trade_open("EUR_USD", "BUY", 1.00564, "Entry: 1.00564 | Stop: 1.00514 | Target: 1.00714")
    time.sleep(1)
    display.trade_win("EUR_USD", 2.16, "Exit: 1.00584 | Duration: 23s | R:R 3.2:1")
    
    # Rick's Commentary
    display.rick_says("Nice! EUR_USD closed with $2.16 profit. That's what I'm talking about.")
    
    # Statistics
    display.section("SESSION STATISTICS")
    stats = {
        "Capital": "$2,273.54",
        "Total Trades": "2",
        "Win Rate": "100.0%",
        "Total P&L": "+$4.32",
        "Wins / Losses": "2 / 0",
        "Avg R:R Ratio": "3.1:1"
    }
    display.stats_panel(stats)
    
    # Progress
    display.section("SESSION PROGRESS")
    display.progress_bar(2, 10, "Trades to promotion")
    print()
    
    print("\n")
