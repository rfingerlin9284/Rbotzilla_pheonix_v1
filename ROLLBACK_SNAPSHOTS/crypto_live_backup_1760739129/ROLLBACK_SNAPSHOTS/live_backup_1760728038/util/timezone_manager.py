#!/usr/bin/env python3
"""
Timezone Manager for RICK Trading System
Handles EST display with UTC tracking and forex session awareness
PIN: 841921
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Dict, Tuple, Optional

# Timezone definitions
UTC = timezone.utc
EST = ZoneInfo("America/New_York")  # Handles EST/EDT automatically
LONDON = ZoneInfo("Europe/London")  # Handles GMT/BST automatically
TOKYO = ZoneInfo("Asia/Tokyo")

class ForexSessionManager:
    """
    Manages forex trading sessions and their overlaps
    All times stored in UTC, displayed in EST
    """
    
    def __init__(self):
        self.sessions = {
            'TOKYO': {
                'open_utc': (0, 0),   # 12:00 AM UTC = 7:00 PM EST (previous day)
                'close_utc': (9, 0),  # 9:00 AM UTC = 4:00 AM EST
                'name': 'Tokyo/Asian Session'
            },
            'LONDON': {
                'open_utc': (8, 0),   # 8:00 AM UTC = 3:00 AM EST
                'close_utc': (17, 0), # 5:00 PM UTC = 12:00 PM EST
                'name': 'London Session'
            },
            'NEW_YORK': {
                'open_utc': (13, 0),  # 1:00 PM UTC = 8:00 AM EST
                'close_utc': (22, 0), # 10:00 PM UTC = 5:00 PM EST
                'name': 'New York Session'
            }
        }
    
    def get_current_sessions(self, dt: Optional[datetime] = None) -> Dict[str, bool]:
        """
        Get active sessions at given time
        
        Args:
            dt: datetime to check (defaults to now in UTC)
            
        Returns:
            Dict with session names as keys and active status as values
        """
        if dt is None:
            dt = datetime.now(UTC)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        
        # Convert to UTC if not already
        dt_utc = dt.astimezone(UTC)
        current_hour = dt_utc.hour
        current_minute = dt_utc.minute
        current_time = current_hour + current_minute / 60.0
        
        active_sessions = {}
        
        for session_name, session_info in self.sessions.items():
            open_hour, open_min = session_info['open_utc']
            close_hour, close_min = session_info['close_utc']
            
            open_time = open_hour + open_min / 60.0
            close_time = close_hour + close_min / 60.0
            
            # Handle sessions that cross midnight
            if close_time < open_time:
                # Session crosses midnight (e.g., Tokyo)
                is_active = current_time >= open_time or current_time < close_time
            else:
                is_active = open_time <= current_time < close_time
            
            active_sessions[session_name] = is_active
        
        return active_sessions
    
    def get_session_overlaps(self, dt: Optional[datetime] = None) -> list:
        """
        Get overlapping sessions at given time
        
        Returns:
            List of tuples with overlapping session pairs
        """
        active = self.get_current_sessions(dt)
        active_names = [name for name, is_active in active.items() if is_active]
        
        overlaps = []
        if 'TOKYO' in active_names and 'LONDON' in active_names:
            overlaps.append(('TOKYO', 'LONDON'))
        if 'LONDON' in active_names and 'NEW_YORK' in active_names:
            overlaps.append(('LONDON', 'NEW_YORK'))
        
        return overlaps
    
    def get_session_times_est(self, session_name: str) -> Dict[str, str]:
        """
        Get session open/close times in EST
        
        Args:
            session_name: Name of session (TOKYO, LONDON, NEW_YORK)
            
        Returns:
            Dict with open_est and close_est times as formatted strings
        """
        if session_name not in self.sessions:
            return {'open_est': 'N/A', 'close_est': 'N/A'}
        
        session = self.sessions[session_name]
        
        # Create UTC times for today
        now_utc = datetime.now(UTC)
        open_utc = now_utc.replace(hour=session['open_utc'][0], minute=session['open_utc'][1], second=0, microsecond=0)
        close_utc = now_utc.replace(hour=session['close_utc'][0], minute=session['close_utc'][1], second=0, microsecond=0)
        
        # Convert to EST
        open_est = open_utc.astimezone(EST)
        close_est = close_utc.astimezone(EST)
        
        return {
            'open_est': open_est.strftime('%I:%M %p EST'),
            'close_est': close_est.strftime('%I:%M %p EST'),
            'open_utc': open_utc.strftime('%H:%M UTC'),
            'close_utc': close_utc.strftime('%H:%M UTC')
        }
    
    def get_next_session_change(self, dt: Optional[datetime] = None) -> Dict:
        """
        Get the next session open or close event
        
        Returns:
            Dict with event info (session, action, time_est, time_utc, minutes_until)
        """
        if dt is None:
            dt = datetime.now(UTC)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        
        dt_utc = dt.astimezone(UTC)
        
        events = []
        
        for session_name, session_info in self.sessions.items():
            # Open time
            open_hour, open_min = session_info['open_utc']
            open_time = dt_utc.replace(hour=open_hour, minute=open_min, second=0, microsecond=0)
            if open_time < dt_utc:
                open_time = open_time.replace(day=open_time.day + 1)
            events.append({
                'session': session_name,
                'action': 'OPEN',
                'time_utc': open_time,
                'time_est': open_time.astimezone(EST)
            })
            
            # Close time
            close_hour, close_min = session_info['close_utc']
            close_time = dt_utc.replace(hour=close_hour, minute=close_min, second=0, microsecond=0)
            if close_time < dt_utc:
                close_time = close_time.replace(day=close_time.day + 1)
            events.append({
                'session': session_name,
                'action': 'CLOSE',
                'time_utc': close_time,
                'time_est': close_time.astimezone(EST)
            })
        
        # Sort by time and get next event
        events.sort(key=lambda x: x['time_utc'])
        next_event = events[0]
        
        minutes_until = (next_event['time_utc'] - dt_utc).total_seconds() / 60
        
        return {
            'session': next_event['session'],
            'action': next_event['action'],
            'time_est': next_event['time_est'].strftime('%I:%M %p EST'),
            'time_utc': next_event['time_utc'].strftime('%H:%M UTC'),
            'minutes_until': int(minutes_until)
        }


def utc_to_est(dt: datetime) -> datetime:
    """Convert UTC datetime to EST"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(EST)


def est_to_utc(dt: datetime) -> datetime:
    """Convert EST datetime to UTC"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=EST)
    return dt.astimezone(UTC)


def format_dual_time(dt: datetime) -> Dict[str, str]:
    """
    Format datetime with both UTC and EST
    
    Args:
        dt: datetime object (will be converted to UTC if naive)
        
    Returns:
        Dict with utc, est, date_est, time_est, date_utc, time_utc
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    
    dt_utc = dt.astimezone(UTC)
    dt_est = dt.astimezone(EST)
    
    return {
        'utc': dt_utc.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'est': dt_est.strftime('%Y-%m-%d %I:%M:%S %p EST'),
        'date_est': dt_est.strftime('%Y-%m-%d'),
        'time_est': dt_est.strftime('%I:%M:%S %p EST'),
        'date_utc': dt_utc.strftime('%Y-%m-%d'),
        'time_utc': dt_utc.strftime('%H:%M:%S UTC'),
        'timestamp_utc': dt_utc.isoformat(),
        'timestamp_est': dt_est.isoformat()
    }


def get_current_time_display() -> Dict[str, str]:
    """
    Get current time in both UTC and EST for display
    
    Returns:
        Dict with formatted times
    """
    now = datetime.now(UTC)
    return format_dual_time(now)


def get_trading_session_info() -> Dict:
    """
    Get comprehensive trading session information for current time
    
    Returns:
        Dict with active sessions, overlaps, next event, and session times
    """
    session_mgr = ForexSessionManager()
    now = datetime.now(UTC)
    
    active_sessions = session_mgr.get_current_sessions(now)
    overlaps = session_mgr.get_session_overlaps(now)
    next_event = session_mgr.get_next_session_change(now)
    
    # Get session times in EST
    session_times = {}
    for session_name in ['TOKYO', 'LONDON', 'NEW_YORK']:
        session_times[session_name] = session_mgr.get_session_times_est(session_name)
    
    return {
        'current_time': get_current_time_display(),
        'active_sessions': active_sessions,
        'overlaps': overlaps,
        'next_event': next_event,
        'session_times': session_times
    }


if __name__ == "__main__":
    # Test the timezone manager
    print("=" * 80)
    print("RICK Trading System - Timezone Manager Test")
    print("=" * 80)
    print()
    
    # Current time display
    time_info = get_current_time_display()
    print("📅 Current Time:")
    print(f"   UTC: {time_info['utc']}")
    print(f"   EST: {time_info['est']}")
    print()
    
    # Trading session info
    session_info = get_trading_session_info()
    print("🌍 Active Forex Sessions:")
    for session, is_active in session_info['active_sessions'].items():
        status = "🟢 OPEN" if is_active else "⚫ CLOSED"
        times = session_info['session_times'][session]
        print(f"   {session:10} {status:12} {times['open_est']} - {times['close_est']}")
    print()
    
    if session_info['overlaps']:
        print("🔄 Active Overlaps:")
        for overlap in session_info['overlaps']:
            print(f"   {overlap[0]} ⟷ {overlap[1]}")
        print()
    
    print("⏭️  Next Session Event:")
    next_evt = session_info['next_event']
    print(f"   {next_evt['session']} {next_evt['action']} in {next_evt['minutes_until']} minutes")
    print(f"   EST: {next_evt['time_est']}")
    print(f"   UTC: {next_evt['time_utc']}")
    print()
    
    print("=" * 80)
