#!/usr/bin/env python3
"""
Advanced Market Hours Manager for RICK Trading System
Properly handles Forex (Sunday 5pm - Friday 5pm EST) and Crypto (24/7)
PIN: 841921
"""

from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, Tuple, Optional, List
from enum import Enum

# Timezone definitions
UTC = timezone.utc
EST = ZoneInfo("America/New_York")  # Handles EST/EDT automatically

class MarketType(Enum):
    FOREX = "forex"
    CRYPTO = "crypto"

class ForexSession(Enum):
    """Forex major session times (in EST)"""
    ASIAN = "asian"      # 7:00 PM - 4:00 AM EST
    LONDON = "london"    # 3:00 AM - 12:00 PM EST
    NEW_YORK = "newyork" # 8:00 AM - 5:00 PM EST

class MarketHoursManager:
    """
    Comprehensive market hours manager
    - Forex: Sunday 5pm EST to Friday 5pm EST (continuous 24h Mon-Fri)
    - Crypto: 24/7/365 (never closes)
    - Session overlaps for optimal trading
    - 6-8 hour position time limits
    """
    
    def __init__(self):
        # Forex session times in EST (24-hour format)
        self.forex_sessions = {
            'ASIAN': {
                'open_hour': 19,   # 7:00 PM EST
                'open_minute': 0,
                'close_hour': 4,   # 4:00 AM EST (next day)
                'close_minute': 0,
                'description': 'Tokyo/Asian Session',
                'major_pairs': ['USD/JPY', 'AUD/USD', 'NZD/USD']
            },
            'LONDON': {
                'open_hour': 3,    # 3:00 AM EST
                'open_minute': 0,
                'close_hour': 12,  # 12:00 PM EST
                'close_minute': 0,
                'description': 'London Session',
                'major_pairs': ['EUR/USD', 'GBP/USD', 'EUR/GBP']
            },
            'NEW_YORK': {
                'open_hour': 8,    # 8:00 AM EST
                'open_minute': 0,
                'close_hour': 17,  # 5:00 PM EST
                'close_minute': 0,
                'description': 'New York Session',
                'major_pairs': ['USD/CAD', 'USD/MXN', 'EUR/USD']
            }
        }
        
        # Session overlaps (most volatile periods)
        self.session_overlaps = {
            'ASIAN_LONDON': {
                'sessions': ('ASIAN', 'LONDON'),
                'start_hour': 3,
                'end_hour': 4,
                'volatility': 'MEDIUM'
            },
            'LONDON_NEWYORK': {
                'sessions': ('LONDON', 'NEW_YORK'),
                'start_hour': 8,
                'end_hour': 12,
                'volatility': 'HIGH'  # Most liquid period
            }
        }
        
        # Position time limits
        self.max_position_hours = 8
        self.recommended_position_hours = 6
    
    def is_forex_open(self, dt: Optional[datetime] = None) -> bool:
        """
        Check if Forex market is open
        Forex: Sunday 5pm EST - Friday 5pm EST
        
        Args:
            dt: datetime to check (defaults to now in EST)
            
        Returns:
            True if Forex is open, False if closed
        """
        if dt is None:
            dt = datetime.now(EST)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=EST)
        else:
            dt = dt.astimezone(EST)
        
        weekday = dt.weekday()  # 0=Monday, 6=Sunday
        hour = dt.hour
        
        # Friday after 5pm EST - CLOSED
        if weekday == 4 and hour >= 17:  # Friday
            return False
        
        # Saturday all day - CLOSED
        if weekday == 5:  # Saturday
            return False
        
        # Sunday before 5pm EST - CLOSED
        if weekday == 6 and hour < 17:  # Sunday
            return False
        
        # Sunday after 5pm EST through Friday 5pm - OPEN
        return True
    
    def is_crypto_open(self, dt: Optional[datetime] = None) -> bool:
        """
        Check if Crypto market is open
        Crypto: ALWAYS OPEN 24/7/365
        
        Returns:
            Always True
        """
        return True  # Crypto never closes!
    
    def get_active_forex_sessions(self, dt: Optional[datetime] = None) -> Dict[str, bool]:
        """
        Get currently active Forex trading sessions
        
        Args:
            dt: datetime to check (defaults to now)
            
        Returns:
            Dict with session names and their active status
        """
        if dt is None:
            dt = datetime.now(EST)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=EST)
        else:
            dt = dt.astimezone(EST)
        
        # If Forex is closed, no sessions are active
        if not self.is_forex_open(dt):
            return {session: False for session in self.forex_sessions.keys()}
        
        current_hour = dt.hour
        current_minute = dt.minute
        current_time = current_hour + current_minute / 60.0
        
        active_sessions = {}
        
        for session_name, session_info in self.forex_sessions.items():
            open_time = session_info['open_hour'] + session_info['open_minute'] / 60.0
            close_time = session_info['close_hour'] + session_info['close_minute'] / 60.0
            
            # Handle sessions that cross midnight (ASIAN session)
            if close_time < open_time:
                # Session crosses midnight
                is_active = current_time >= open_time or current_time < close_time
            else:
                # Normal session within same day
                is_active = open_time <= current_time < close_time
            
            active_sessions[session_name] = is_active
        
        return active_sessions
    
    def get_session_overlap(self, dt: Optional[datetime] = None) -> Optional[Dict]:
        """
        Get current session overlap (if any)
        Overlaps are the most volatile and liquid trading periods
        
        Returns:
            Dict with overlap info or None if no overlap
        """
        active_sessions = self.get_active_forex_sessions(dt)
        active_names = [name for name, is_active in active_sessions.items() if is_active]
        
        if dt is None:
            dt = datetime.now(EST)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=EST)
        else:
            dt = dt.astimezone(EST)
        
        current_hour = dt.hour
        
        for overlap_name, overlap_info in self.session_overlaps.items():
            start = overlap_info['start_hour']
            end = overlap_info['end_hour']
            
            if start <= current_hour < end:
                return {
                    'name': overlap_name,
                    'sessions': overlap_info['sessions'],
                    'volatility': overlap_info['volatility'],
                    'start_hour': start,
                    'end_hour': end
                }
        
        return None
    
    def get_next_forex_event(self, dt: Optional[datetime] = None) -> Dict:
        """
        Get the next significant Forex event (market open/close, session change)
        
        Returns:
            Dict with event information
        """
        if dt is None:
            dt = datetime.now(EST)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=EST)
        else:
            dt = dt.astimezone(EST)
        
        # Check if we're approaching weekend close
        weekday = dt.weekday()
        hour = dt.hour
        
        # Friday approaching 5pm
        if weekday == 4 and hour < 17:
            close_time = dt.replace(hour=17, minute=0, second=0, microsecond=0)
            minutes_until = (close_time - dt).total_seconds() / 60
            return {
                'event': 'FOREX_CLOSE',
                'description': 'Forex market closes for weekend',
                'time_est': close_time.strftime('%I:%M %p EST'),
                'minutes_until': int(minutes_until)
            }
        
        # Weekend - waiting for Sunday open
        if weekday == 5 or (weekday == 6 and hour < 17):
            # Calculate next Sunday 5pm
            days_until_sunday = (6 - weekday) % 7
            if days_until_sunday == 0 and hour >= 17:
                days_until_sunday = 7
            
            open_time = dt.replace(hour=17, minute=0, second=0, microsecond=0) + timedelta(days=days_until_sunday)
            minutes_until = (open_time - dt).total_seconds() / 60
            
            return {
                'event': 'FOREX_OPEN',
                'description': 'Forex market opens for the week',
                'time_est': open_time.strftime('%I:%M %p EST on %A'),
                'minutes_until': int(minutes_until)
            }
        
        # Find next session change
        active_sessions = self.get_active_forex_sessions(dt)
        events = []
        
        for session_name, session_info in self.forex_sessions.items():
            # Next open
            open_hour = session_info['open_hour']
            open_minute = session_info['open_minute']
            open_time = dt.replace(hour=open_hour, minute=open_minute, second=0, microsecond=0)
            
            if open_time <= dt:
                open_time += timedelta(days=1)
            
            events.append({
                'event': f'{session_name}_OPEN',
                'description': f'{session_info["description"]} opens',
                'time': open_time
            })
            
            # Next close
            close_hour = session_info['close_hour']
            close_minute = session_info['close_minute']
            close_time = dt.replace(hour=close_hour, minute=close_minute, second=0, microsecond=0)
            
            if close_time <= dt:
                close_time += timedelta(days=1)
            
            events.append({
                'event': f'{session_name}_CLOSE',
                'description': f'{session_info["description"]} closes',
                'time': close_time
            })
        
        # Sort by time and get next
        events.sort(key=lambda x: x['time'])
        next_event = events[0]
        
        minutes_until = (next_event['time'] - dt).total_seconds() / 60
        
        return {
            'event': next_event['event'],
            'description': next_event['description'],
            'time_est': next_event['time'].strftime('%I:%M %p EST'),
            'minutes_until': int(minutes_until)
        }
    
    def get_position_time_warning(self, position_open_time: datetime, dt: Optional[datetime] = None) -> Dict:
        """
        Check if position is approaching time limit
        Max: 8 hours, Recommended: 6 hours
        
        Args:
            position_open_time: When position was opened
            dt: Current time (defaults to now)
            
        Returns:
            Dict with warning info
        """
        if dt is None:
            dt = datetime.now(UTC)
        
        if position_open_time.tzinfo is None:
            position_open_time = position_open_time.replace(tzinfo=UTC)
        
        dt_utc = dt.astimezone(UTC) if dt.tzinfo else dt.replace(tzinfo=UTC)
        position_open_utc = position_open_time.astimezone(UTC)
        
        hours_open = (dt_utc - position_open_utc).total_seconds() / 3600
        
        status = "OK"
        warning_level = "GREEN"
        
        if hours_open >= self.max_position_hours:
            status = "CRITICAL"
            warning_level = "RED"
        elif hours_open >= self.recommended_position_hours:
            status = "WARNING"
            warning_level = "YELLOW"
        
        return {
            'hours_open': round(hours_open, 2),
            'max_hours': self.max_position_hours,
            'recommended_hours': self.recommended_position_hours,
            'status': status,
            'warning_level': warning_level,
            'should_close': hours_open >= self.max_position_hours
        }
    
    def get_market_status(self, dt: Optional[datetime] = None) -> Dict:
        """
        Get comprehensive market status for both Forex and Crypto
        
        Returns:
            Complete market status dict
        """
        if dt is None:
            dt = datetime.now(EST)
        
        forex_open = self.is_forex_open(dt)
        crypto_open = self.is_crypto_open(dt)
        
        active_forex_sessions = self.get_active_forex_sessions(dt) if forex_open else {}
        session_overlap = self.get_session_overlap(dt)
        next_forex_event = self.get_next_forex_event(dt)
        
        dt_utc = dt.astimezone(UTC)
        
        return {
            'timestamp': {
                'est': dt.strftime('%Y-%m-%d %I:%M:%S %p EST'),
                'utc': dt_utc.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'weekday': dt.strftime('%A')
            },
            'forex': {
                'is_open': forex_open,
                'status': 'OPEN' if forex_open else 'CLOSED (Weekend)',
                'active_sessions': active_forex_sessions,
                'session_overlap': session_overlap,
                'next_event': next_forex_event
            },
            'crypto': {
                'is_open': crypto_open,
                'status': 'OPEN 24/7',
                'note': 'Cryptocurrency markets never close'
            },
            'position_limits': {
                'max_hours': self.max_position_hours,
                'recommended_hours': self.recommended_position_hours,
                'note': 'Positions should be closed within 6-8 hours'
            }
        }


def get_current_market_status() -> Dict:
    """Convenience function to get current market status"""
    manager = MarketHoursManager()
    return manager.get_market_status()


if __name__ == "__main__":
    # Test the market hours manager
    print("=" * 80)
    print("RICK Trading System - Advanced Market Hours Manager")
    print("=" * 80)
    print()
    
    manager = MarketHoursManager()
    status = manager.get_market_status()
    
    # Display timestamp
    print("📅 Current Time:")
    print(f"   EST: {status['timestamp']['est']} ({status['timestamp']['weekday']})")
    print(f"   UTC: {status['timestamp']['utc']}")
    print()
    
    # Forex status
    print("💱 FOREX Market:")
    print(f"   Status: {status['forex']['status']}")
    
    if status['forex']['is_open']:
        print("   Active Sessions:")
        for session, is_active in status['forex']['active_sessions'].items():
            symbol = "🟢" if is_active else "⚫"
            session_info = manager.forex_sessions[session]
            print(f"      {symbol} {session:10} {session_info['description']:25} "
                  f"{session_info['open_hour']:02d}:{session_info['open_minute']:02d} - "
                  f"{session_info['close_hour']:02d}:{session_info['close_minute']:02d} EST")
        
        if status['forex']['session_overlap']:
            overlap = status['forex']['session_overlap']
            print(f"\n   🔄 Session Overlap: {overlap['sessions'][0]} ⟷ {overlap['sessions'][1]}")
            print(f"      Volatility: {overlap['volatility']}")
    
    print(f"\n   Next Event: {status['forex']['next_event']['description']}")
    print(f"              in {status['forex']['next_event']['minutes_until']} minutes")
    print(f"              at {status['forex']['next_event']['time_est']}")
    print()
    
    # Crypto status
    print("₿  CRYPTO Market (Coinbase Advanced):")
    print(f"   Status: {status['crypto']['status']}")
    print(f"   Note: {status['crypto']['note']}")
    print()
    
    # Position limits
    print("⏱️  Position Time Limits:")
    print(f"   Recommended: {status['position_limits']['recommended_hours']} hours")
    print(f"   Maximum: {status['position_limits']['max_hours']} hours")
    print(f"   Note: {status['position_limits']['note']}")
    print()
    
    print("=" * 80)
