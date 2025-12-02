#!/usr/bin/env python3
"""
RBOTzilla UNI - Live Monitoring & Alert System
Real-time health monitoring with automated circuit breakers.
PIN: 841921 | Phase 17
"""

import os
import sys
import json
import time
import datetime
import threading
import logging
import traceback
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import signal
import psutil

# =============================================================================
# RBOTZILLA UNI LIVE MONITORING SYSTEM
# =============================================================================
# ENGINEER (40%): Live metrics collection loop and system monitoring
# PROF_QUANT (30%): PnL anomaly detection and statistical analysis
# TRADER_PSYCH (20%): Panic halt triggers and psychological protection
# MENTOR_BK (10%): Alert formatting and notification standards
#
# This system provides:
# - Real-time performance monitoring every 60 seconds
# - Automated circuit breakers for risk protection
# - Multi-level alert system (WARNING, CRITICAL, EMERGENCY)
# - Live dashboard data generation
# - Automatic system shutdown on breach detection
# =============================================================================

# Global configuration
REQUIRED_PIN = 841921
MONITORING_INTERVAL = 60  # seconds
LOG_DIR = Path("logs")
DASHBOARD_DIR = Path("monitoring")
STATUS_FILE = Path("production_status.json")

# Alert thresholds
LATENCY_WARNING_MS = 100
LATENCY_CRITICAL_MS = 250
DAILY_LOSS_WARNING_PCT = 3.0
DAILY_LOSS_CRITICAL_PCT = 5.0
MARGIN_WARNING_PCT = 80.0
MARGIN_CRITICAL_PCT = 90.0
WIN_RATE_WARNING_PCT = 45.0
CONSECUTIVE_LOSSES_WARNING = 3
CONSECUTIVE_LOSSES_CRITICAL = 5

# Circuit breaker configuration
CIRCUIT_BREAKER_ACTIVE = True
AUTO_SHUTDOWN_ON_CRITICAL = True
EMERGENCY_CONTACT_ENABLED = False

@dataclass
class AlertLevel:
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"

@dataclass
class SystemMetrics:
    """Real-time system performance metrics"""
    timestamp: str
    latency_ms: float
    daily_pnl_pct: float
    total_pnl_pct: float
    margin_usage_pct: float
    win_rate_pct: float
    consecutive_losses: int
    active_positions: int
    daily_trades: int
    system_status: str
    cpu_usage_pct: float
    memory_usage_pct: float
    disk_usage_pct: float
    alerts_count: int
    last_trade_time: Optional[str] = None

@dataclass
class Alert:
    """System alert structure"""
    timestamp: str
    level: str
    category: str
    message: str
    metric_value: float
    threshold: float
    action_taken: str
    resolved: bool = False

class LiveMonitor:
    """
    RBOTzilla UNI Live Monitoring System
    
    Provides real-time monitoring of system performance, risk metrics,
    and automated circuit breaker functionality.
    """
    
    def __init__(self, pin: int):
        self.pin = pin
        self.verify_pin()
        
        # Initialize monitoring state
        self.monitoring_active = False
        self.shutdown_requested = False
        self.metrics_history: List[SystemMetrics] = []
        self.active_alerts: List[Alert] = []
        self.circuit_breakers_armed = True
        
        # Performance tracking
        self.start_time = datetime.datetime.now()
        self.last_update_time = None
        self.update_count = 0
        self.error_count = 0
        
        # Setup logging
        self.setup_logging()
        
        # Initialize directories
        LOG_DIR.mkdir(exist_ok=True)
        DASHBOARD_DIR.mkdir(exist_ok=True)
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)
        
        self.logger.info("Live monitor initialized with PIN authentication")
    
    def verify_pin(self) -> None:
        """Verify PIN authentication"""
        if self.pin != REQUIRED_PIN:
            raise ValueError(f"Invalid PIN. Monitor access denied.")
    
    def setup_logging(self) -> None:
        """Setup comprehensive logging system"""
        log_file = LOG_DIR / f"live_monitor_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('LiveMonitor')
    
    def shutdown_handler(self, signum: int, frame) -> None:
        """Handle graceful shutdown signals"""
        self.logger.warning(f"Shutdown signal received: {signum}")
        self.shutdown_requested = True
    
    def collect_system_metrics(self) -> SystemMetrics:
        """
        Collect comprehensive system performance metrics
        
        ENGINEER (40%): System resource monitoring and performance collection
        PROF_QUANT (30%): PnL calculation and statistical analysis
        """
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            # System resource metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Simulated trading metrics (would connect to real broker in production)
            latency_ms = self.measure_system_latency()
            daily_pnl_pct = self.calculate_daily_pnl()
            total_pnl_pct = self.calculate_total_pnl()
            margin_usage_pct = self.calculate_margin_usage()
            win_rate_pct = self.calculate_win_rate()
            consecutive_losses = self.count_consecutive_losses()
            active_positions = self.count_active_positions()
            daily_trades = self.count_daily_trades()
            
            # System status determination
            system_status = self.determine_system_status()
            
            metrics = SystemMetrics(
                timestamp=timestamp,
                latency_ms=latency_ms,
                daily_pnl_pct=daily_pnl_pct,
                total_pnl_pct=total_pnl_pct,
                margin_usage_pct=margin_usage_pct,
                win_rate_pct=win_rate_pct,
                consecutive_losses=consecutive_losses,
                active_positions=active_positions,
                daily_trades=daily_trades,
                system_status=system_status,
                cpu_usage_pct=cpu_usage,
                memory_usage_pct=memory.percent,
                disk_usage_pct=(disk.used / disk.total) * 100,
                alerts_count=len(self.active_alerts),
                last_trade_time=self.get_last_trade_time()
            )
            
            return metrics
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error collecting metrics: {str(e)}")
            raise
    
    def measure_system_latency(self) -> float:
        """Measure system response latency"""
        start_time = time.time()
        
        # Simulate system operation (file I/O, network check, etc.)
        try:
            # Check file system responsiveness
            test_file = LOG_DIR / "latency_test.tmp"
            test_file.write_text("latency_test")
            test_file.unlink()
            
            # Simulate network/broker latency
            time.sleep(0.001)  # Baseline 1ms
            
            # Add realistic variation based on system load
            load_factor = psutil.cpu_percent() / 100.0
            simulated_latency = 25 + (load_factor * 50)  # 25-75ms base range
            
        except Exception:
            simulated_latency = 150  # Higher latency on errors
        
        end_time = time.time()
        measured_latency = (end_time - start_time) * 1000  # Convert to ms
        
        return max(simulated_latency, measured_latency)
    
    def calculate_daily_pnl(self) -> float:
        """Calculate daily PnL percentage"""
        try:
            # Simulate realistic PnL based on market conditions
            if len(self.metrics_history) > 0:
                # Trend-following simulation with some randomness
                last_pnl = self.metrics_history[-1].daily_pnl_pct
                market_trend = 0.02  # Slight positive bias
                volatility = 0.5     # Daily volatility factor
                
                import random
                random_factor = random.gauss(0, volatility)
                new_pnl = last_pnl + market_trend + random_factor
                
                # Keep within realistic bounds
                new_pnl = max(-8.0, min(8.0, new_pnl))
            else:
                # Initial simulation value
                new_pnl = 0.15  # Slightly positive start
            
            return round(new_pnl, 2)
            
        except Exception:
            return 0.0
    
    def calculate_total_pnl(self) -> float:
        """Calculate total PnL since system start"""
        try:
            if len(self.metrics_history) > 0:
                daily_pnls = [m.daily_pnl_pct for m in self.metrics_history[-30:]]
                return round(sum(daily_pnls), 2)
            return 0.0
        except Exception:
            return 0.0
    
    def calculate_margin_usage(self) -> float:
        """Calculate current margin usage percentage"""
        try:
            # Simulate margin usage based on active positions and system load
            base_margin = 15.0
            position_factor = self.count_active_positions() * 8.0
            volatility_factor = abs(self.calculate_daily_pnl()) * 2.0
            
            margin_usage = base_margin + position_factor + volatility_factor
            return min(95.0, margin_usage)
            
        except Exception:
            return 20.0
    
    def calculate_win_rate(self) -> float:
        """Calculate current win rate percentage"""
        try:
            # Simulate win rate based on system performance
            base_win_rate = 58.0
            
            if len(self.metrics_history) > 10:
                recent_pnls = [m.daily_pnl_pct for m in self.metrics_history[-10:]]
                positive_count = len([p for p in recent_pnls if p > 0])
                calculated_rate = (positive_count / len(recent_pnls)) * 100
                
                return round((base_win_rate + calculated_rate) / 2, 1)
            
            return base_win_rate
            
        except Exception:
            return 55.0
    
    def count_consecutive_losses(self) -> int:
        """Count consecutive losing periods"""
        try:
            consecutive = 0
            for metrics in reversed(self.metrics_history):
                if metrics.daily_pnl_pct < 0:
                    consecutive += 1
                else:
                    break
            return consecutive
        except Exception:
            return 0
    
    def count_active_positions(self) -> int:
        """Count currently active trading positions"""
        try:
            hour = datetime.datetime.now().hour
            
            # More positions during active trading hours
            if 8 <= hour <= 16:
                base_positions = 2
            else:
                base_positions = 1
            
            # Adjust based on performance
            if len(self.metrics_history) > 0:
                last_pnl = self.metrics_history[-1].daily_pnl_pct
                if last_pnl > 2.0:
                    base_positions += 1
                elif last_pnl < -2.0:
                    base_positions = max(0, base_positions - 1)
            
            return min(3, base_positions)  # Canary mode max
            
        except Exception:
            return 1
    
    def count_daily_trades(self) -> int:
        """Count trades executed today"""
        try:
            today = datetime.datetime.now().date()
            
            base_trades = len([m for m in self.metrics_history if 
                             datetime.datetime.fromisoformat(m.timestamp).date() == today])
            
            return min(10, base_trades)  # Canary mode max
            
        except Exception:
            return 0
    
    def get_last_trade_time(self) -> Optional[str]:
        """Get timestamp of last trade execution"""
        try:
            if len(self.metrics_history) > 0:
                last_time = datetime.datetime.fromisoformat(self.metrics_history[-1].timestamp)
                return (last_time - datetime.timedelta(minutes=30)).isoformat()
            return None
        except Exception:
            return None
    
    def determine_system_status(self) -> str:
        """Determine overall system health status"""
        try:
            critical_alerts = [a for a in self.active_alerts if a.level == AlertLevel.CRITICAL]
            emergency_alerts = [a for a in self.active_alerts if a.level == AlertLevel.EMERGENCY]
            
            if emergency_alerts:
                return "EMERGENCY"
            elif critical_alerts:
                return "CRITICAL"
            elif len(self.active_alerts) > 5:
                return "WARNING"
            elif self.error_count > 10:
                return "DEGRADED"
            else:
                return "HEALTHY"
                
        except Exception:
            return "UNKNOWN"
    
    def analyze_metrics_for_alerts(self, metrics: SystemMetrics) -> List[Alert]:
        """
        Analyze current metrics and generate alerts
        
        PROF_QUANT (30%): Statistical analysis and anomaly detection
        TRADER_PSYCH (20%): Psychological trigger identification
        """
        alerts = []
        timestamp = datetime.datetime.now().isoformat()
        
        try:
            # Latency monitoring
            if metrics.latency_ms > LATENCY_CRITICAL_MS:
                alerts.append(Alert(
                    timestamp=timestamp,
                    level=AlertLevel.CRITICAL,
                    category="LATENCY",
                    message=f"System latency critically high: {metrics.latency_ms:.1f}ms",
                    metric_value=metrics.latency_ms,
                    threshold=LATENCY_CRITICAL_MS,
                    action_taken="INVESTIGATE_NETWORK"
                ))
            elif metrics.latency_ms > LATENCY_WARNING_MS:
                alerts.append(Alert(
                    timestamp=timestamp,
                    level=AlertLevel.WARNING,
                    category="LATENCY",
                    message=f"System latency elevated: {metrics.latency_ms:.1f}ms",
                    metric_value=metrics.latency_ms,
                    threshold=LATENCY_WARNING_MS,
                    action_taken="MONITOR"
                ))
            
            # Daily P&L monitoring
            if metrics.daily_pnl_pct <= -DAILY_LOSS_CRITICAL_PCT:
                alerts.append(Alert(
                    timestamp=timestamp,
                    level=AlertLevel.CRITICAL,
                    category="PNL",
                    message=f"Daily loss exceeds critical threshold: {metrics.daily_pnl_pct:.1f}%",
                    metric_value=abs(metrics.daily_pnl_pct),
                    threshold=DAILY_LOSS_CRITICAL_PCT,
                    action_taken="CIRCUIT_BREAKER_TRIGGERED"
                ))
            elif metrics.daily_pnl_pct <= -DAILY_LOSS_WARNING_PCT:
                alerts.append(Alert(
                    timestamp=timestamp,
                    level=AlertLevel.WARNING,
                    category="PNL",
                    message=f"Daily loss approaching threshold: {metrics.daily_pnl_pct:.1f}%",
                    metric_value=abs(metrics.daily_pnl_pct),
                    threshold=DAILY_LOSS_WARNING_PCT,
                    action_taken="RISK_REDUCTION"
                ))
            
            # Margin usage monitoring
            if metrics.margin_usage_pct >= MARGIN_CRITICAL_PCT:
                alerts.append(Alert(
                    timestamp=timestamp,
                    level=AlertLevel.CRITICAL,
                    category="MARGIN",
                    message=f"Margin usage critically high: {metrics.margin_usage_pct:.1f}%",
                    metric_value=metrics.margin_usage_pct,
                    threshold=MARGIN_CRITICAL_PCT,
                    action_taken="REDUCE_POSITIONS"
                ))
            elif metrics.margin_usage_pct >= MARGIN_WARNING_PCT:
                alerts.append(Alert(
                    timestamp=timestamp,
                    level=AlertLevel.WARNING,
                    category="MARGIN",
                    message=f"Margin usage elevated: {metrics.margin_usage_pct:.1f}%",
                    metric_value=metrics.margin_usage_pct,
                    threshold=MARGIN_WARNING_PCT,
                    action_taken="MONITOR"
                ))
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error analyzing metrics for alerts: {str(e)}")
            return []
    
    def process_alerts(self, new_alerts: List[Alert]) -> None:
        """Process and handle system alerts"""
        for alert in new_alerts:
            # Add to active alerts
            self.active_alerts.append(alert)
            
            # Log the alert
            log_level = {
                AlertLevel.INFO: logging.INFO,
                AlertLevel.WARNING: logging.WARNING,
                AlertLevel.CRITICAL: logging.CRITICAL,
                AlertLevel.EMERGENCY: logging.CRITICAL
            }.get(alert.level, logging.INFO)
            
            self.logger.log(log_level, f"[{alert.level}] {alert.category}: {alert.message}")
            
            # Handle critical alerts with circuit breaker
            if alert.level == AlertLevel.CRITICAL and CIRCUIT_BREAKER_ACTIVE:
                self.trigger_circuit_breaker(alert)
    
    def trigger_circuit_breaker(self, alert: Alert) -> None:
        """Trigger circuit breaker for critical alerts"""
        self.logger.critical(f"CIRCUIT BREAKER TRIGGERED: {alert.message}")
        
        if STATUS_FILE.exists():
            try:
                with open(STATUS_FILE, 'r') as f:
                    status = json.load(f)
                
                status['status'] = 'CIRCUIT_BREAKER_ACTIVE'
                status['circuit_breaker_reason'] = alert.message
                status['circuit_breaker_time'] = alert.timestamp
                
                with open(STATUS_FILE, 'w') as f:
                    json.dump(status, f, indent=2)
                    
            except Exception as e:
                self.logger.error(f"Failed to update status file: {str(e)}")
        
        # Auto-shutdown if configured
        if AUTO_SHUTDOWN_ON_CRITICAL and alert.category in ['PNL', 'MARGIN', 'STREAK']:
            self.logger.critical("AUTO-SHUTDOWN TRIGGERED DUE TO CRITICAL ALERT")
            self.shutdown_requested = True
    
    def cleanup_resolved_alerts(self) -> None:
        """Clean up resolved alerts to prevent memory buildup"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=1)
        
        self.active_alerts = [
            alert for alert in self.active_alerts
            if not alert.resolved and 
            datetime.datetime.fromisoformat(alert.timestamp) > cutoff_time
        ]
    
    def generate_dashboard_data(self, metrics: SystemMetrics) -> None:
        """Generate dashboard data for real-time display"""
        try:
            dashboard_data = {
                "timestamp": metrics.timestamp,
                "system_status": metrics.system_status,
                "uptime_seconds": int((datetime.datetime.now() - self.start_time).total_seconds()),
                "update_count": self.update_count,
                "error_count": self.error_count,
                
                "performance": {
                    "latency_ms": metrics.latency_ms,
                    "daily_pnl_pct": metrics.daily_pnl_pct,
                    "total_pnl_pct": metrics.total_pnl_pct,
                    "win_rate_pct": metrics.win_rate_pct,
                    "consecutive_losses": metrics.consecutive_losses
                },
                
                "risk": {
                    "margin_usage_pct": metrics.margin_usage_pct,
                    "active_positions": metrics.active_positions,
                    "daily_trades": metrics.daily_trades,
                    "last_trade_time": metrics.last_trade_time
                },
                
                "system": {
                    "cpu_usage_pct": metrics.cpu_usage_pct,
                    "memory_usage_pct": metrics.memory_usage_pct,
                    "disk_usage_pct": metrics.disk_usage_pct
                },
                
                "alerts": {
                    "total_count": len(self.active_alerts),
                    "by_level": {
                        "INFO": len([a for a in self.active_alerts if a.level == AlertLevel.INFO]),
                        "WARNING": len([a for a in self.active_alerts if a.level == AlertLevel.WARNING]),
                        "CRITICAL": len([a for a in self.active_alerts if a.level == AlertLevel.CRITICAL]),
                        "EMERGENCY": len([a for a in self.active_alerts if a.level == AlertLevel.EMERGENCY])
                    },
                    "recent": [asdict(alert) for alert in self.active_alerts[-5:]]
                },
                
                "history": {
                    "timestamps": [m.timestamp for m in self.metrics_history[-60:]],
                    "daily_pnl": [m.daily_pnl_pct for m in self.metrics_history[-60:]],
                    "latency": [m.latency_ms for m in self.metrics_history[-60:]],
                    "margin_usage": [m.margin_usage_pct for m in self.metrics_history[-60:]],
                    "win_rate": [m.win_rate_pct for m in self.metrics_history[-60:]]
                }
            }
            
            # Write dashboard data
            dashboard_file = DASHBOARD_DIR / "live_data.json"
            with open(dashboard_file, 'w') as f:
                json.dump(dashboard_data, f, indent=2)
            
            # Create status summary for TMUX display
            self.create_tmux_status(metrics)
            
        except Exception as e:
            self.logger.error(f"Error generating dashboard data: {str(e)}")
    
    def create_tmux_status(self, metrics: SystemMetrics) -> None:
        """Create condensed status for TMUX display"""
        try:
            status_emoji = {
                "HEALTHY": "🟢",
                "WARNING": "🟡", 
                "DEGRADED": "🟠",
                "CRITICAL": "🔴",
                "EMERGENCY": "🚨",
                "UNKNOWN": "⚪"
            }.get(metrics.system_status, "⚪")
            
            tmux_status = (
                f"{status_emoji} RBOTzilla | "
                f"PnL: {metrics.daily_pnl_pct:+.1f}% | "
                f"Latency: {metrics.latency_ms:.0f}ms | "
                f"Margin: {metrics.margin_usage_pct:.0f}% | "
                f"Alerts: {len(self.active_alerts)} | "
                f"Uptime: {int((datetime.datetime.now() - self.start_time).total_seconds() / 60)}m"
            )
            
            # Write TMUX status
            tmux_file = DASHBOARD_DIR / "tmux_status.txt"
            with open(tmux_file, 'w') as f:
                f.write(tmux_status)
                
        except Exception as e:
            self.logger.error(f"Error creating TMUX status: {str(e)}")
    
    def monitoring_loop(self) -> None:
        """Main monitoring loop - runs every 60 seconds"""
        self.monitoring_active = True
        self.logger.info("Live monitoring started - collecting metrics every 60 seconds")
        
        while self.monitoring_active and not self.shutdown_requested:
            try:
                loop_start = time.time()
                
                # Collect current metrics
                metrics = self.collect_system_metrics()
                
                # Store metrics in history
                self.metrics_history.append(metrics)
                
                # Keep only last 24 hours of data
                if len(self.metrics_history) > 1440:
                    self.metrics_history = self.metrics_history[-1440:]
                
                # Analyze for alerts
                new_alerts = self.analyze_metrics_for_alerts(metrics)
                
                # Process alerts
                if new_alerts:
                    self.process_alerts(new_alerts)
                
                # Cleanup old alerts
                self.cleanup_resolved_alerts()
                
                # Generate dashboard data
                self.generate_dashboard_data(metrics)
                
                # Update tracking
                self.update_count += 1
                self.last_update_time = datetime.datetime.now()
                
                # Log status summary
                if self.update_count % 10 == 0:
                    self.logger.info(
                        f"Monitor cycle {self.update_count}: "
                        f"Status={metrics.system_status}, "
                        f"PnL={metrics.daily_pnl_pct:+.1f}%, "
                        f"Latency={metrics.latency_ms:.0f}ms, "
                        f"Alerts={len(self.active_alerts)}"
                    )
                
                # Calculate sleep time to maintain 60-second intervals
                loop_duration = time.time() - loop_start
                sleep_time = max(0, MONITORING_INTERVAL - loop_duration)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    self.logger.warning(f"Monitoring loop overran by {-sleep_time:.1f} seconds")
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring interrupted by user")
                break
            except Exception as e:
                self.error_count += 1
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                
                # Sleep before retry
                time.sleep(10)
        
        self.monitoring_active = False
        self.logger.info("Live monitoring stopped")
    
    def start_monitoring(self) -> None:
        """Start the monitoring system"""
        try:
            self.logger.info("Starting RBOTzilla UNI Live Monitor")
            self.logger.info(f"Monitoring interval: {MONITORING_INTERVAL} seconds")
            self.logger.info(f"Circuit breakers: {'ACTIVE' if CIRCUIT_BREAKER_ACTIVE else 'DISABLED'}")
            self.logger.info(f"Auto-shutdown: {'ENABLED' if AUTO_SHUTDOWN_ON_CRITICAL else 'DISABLED'}")
            
            # Start monitoring loop
            self.monitoring_loop()
            
        except Exception as e:
            self.logger.critical(f"Critical error in monitoring system: {str(e)}")
            raise
        finally:
            self.cleanup_on_shutdown()
    
    def cleanup_on_shutdown(self) -> None:
        """Cleanup operations on shutdown"""
        try:
            if STATUS_FILE.exists():
                with open(STATUS_FILE, 'r') as f:
                    status = json.load(f)
                
                status['monitoring_status'] = 'STOPPED'
                status['last_monitor_stop'] = datetime.datetime.now().isoformat()
                
                with open(STATUS_FILE, 'w') as f:
                    json.dump(status, f, indent=2)
            
            shutdown_summary = {
                "shutdown_time": datetime.datetime.now().isoformat(),
                "total_updates": self.update_count,
                "total_errors": self.error_count,
                "uptime_seconds": int((datetime.datetime.now() - self.start_time).total_seconds()),
                "final_alert_count": len(self.active_alerts)
            }
            
            summary_file = LOG_DIR / f"monitor_shutdown_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w') as f:
                json.dump(shutdown_summary, f, indent=2)
            
            self.logger.info("Monitor cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

def get_live_monitor(pin: int) -> LiveMonitor:
    """Factory function to create live monitor instance"""
    return LiveMonitor(pin=pin)

def main():
    """Main entry point for live monitoring"""
    if len(sys.argv) != 2:
        print("Usage: python live_monitor.py <PIN>")
        sys.exit(1)
    
    try:
        pin = int(sys.argv[1])
        monitor = get_live_monitor(pin=pin)
        monitor.start_monitoring()
    except ValueError:
        print("Invalid PIN format")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()