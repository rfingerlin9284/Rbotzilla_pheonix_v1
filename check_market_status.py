import datetime
import pytz

# Define market hours and holidays
MARKET_TIMEZONE = pytz.timezone('America/New_York')
MARKET_OPEN = datetime.time(9, 30)  # 9:30 AM EST
MARKET_CLOSE = datetime.time(16, 0)  # 4:00 PM EST

HOLIDAYS = [
    datetime.date(2025, 1, 1),   # New Year's Day
    datetime.date(2025, 7, 4),   # Independence Day
    datetime.date(2025, 11, 27), # Thanksgiving Day
    datetime.date(2025, 12, 25), # Christmas Day
]

def is_market_open():
    """Check if the market is open based on time and holidays."""
    now = datetime.datetime.now(MARKET_TIMEZONE)
    today = now.date()
    current_time = now.time()

    # Check if today is a holiday
    if today in HOLIDAYS:
        return False, "Market is closed today due to a holiday."

    # Check if current time is within market hours
    if MARKET_OPEN <= current_time <= MARKET_CLOSE:
        return True, "Market is open."
    else:
        return False, "Market is closed."

if __name__ == "__main__":
    status, message = is_market_open()
    print(message)