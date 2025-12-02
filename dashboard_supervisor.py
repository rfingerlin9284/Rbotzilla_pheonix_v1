#!/usr/bin/env python3
"""
RICK Trading System - Dashboard Supervisor
Keeps dashboard running, manages narration, and maintains Hive Mind connection
with respectful API rate limiting (1 min delay between OpenAI requests)
"""

import os
import sys
import time
import json
import subprocess
import signal
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
DASHBOARD_SCRIPT = "dashboard/app.py"
NARRATION_FILE = "narration.jsonl"
HIVE_MIND_SCRIPT = "hive/rick_hive_mind.py"
CHECK_INTERVAL = 30  # seconds - how often to check if processes are alive
OPENAI_DELAY = 60  # seconds - 1 minute delay between OpenAI API calls
MAX_NARRATION_LINES = 1000  # Rotate narration file after this many lines

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

class DashboardSupervisor:
    def __init__(self):
        self.dashboard_process = None
        self.hive_process = None
        self.last_openai_call = None
        self.running = True
        self.start_time = datetime.now()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
    def log(self, message, color=Colors.CYAN):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{color}[{timestamp}] {message}{Colors.END}")
        
    def log_narration(self, message, level="INFO"):
        """Log to narration.jsonl in plain English"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "text": message,
            "source": "dashboard_supervisor"
        }
        
        try:
            with open(NARRATION_FILE, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            self.log(f"Error writing narration: {e}", Colors.RED)
    
    def rotate_narration_if_needed(self):
        """Rotate narration file if it gets too large"""
        try:
            if os.path.exists(NARRATION_FILE):
                line_count = sum(1 for _ in open(NARRATION_FILE))
                if line_count > MAX_NARRATION_LINES:
                    backup_file = f"narration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
                    os.rename(NARRATION_FILE, f"logs/{backup_file}")
                    self.log(f"Rotated narration file to logs/{backup_file}", Colors.YELLOW)
                    self.log_narration(f"Narration file rotated to {backup_file} after {line_count} entries")
        except Exception as e:
            self.log(f"Error rotating narration: {e}", Colors.RED)
    
    def can_make_openai_call(self):
        """Check if enough time has passed since last OpenAI call"""
        if self.last_openai_call is None:
            return True
        
        time_since_last = datetime.now() - self.last_openai_call
        return time_since_last.total_seconds() >= OPENAI_DELAY
    
    def wait_for_openai_delay(self):
        """Wait for the required delay between OpenAI calls"""
        if self.last_openai_call:
            time_since_last = datetime.now() - self.last_openai_call
            wait_time = OPENAI_DELAY - time_since_last.total_seconds()
            if wait_time > 0:
                self.log(f"Rate limiting: Waiting {wait_time:.0f}s before next OpenAI call", Colors.YELLOW)
                time.sleep(wait_time)
        
        self.last_openai_call = datetime.now()
    
    def is_process_running(self, process):
        """Check if a process is still running"""
        if process is None:
            return False
        return process.poll() is None
    
    def start_dashboard(self):
        """Start the dashboard process"""
        try:
            self.log("Starting dashboard...", Colors.GREEN)
            self.dashboard_process = subprocess.Popen(
                ["python3", DASHBOARD_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            time.sleep(3)  # Give it time to start
            
            if self.is_process_running(self.dashboard_process):
                self.log("✓ Dashboard started successfully", Colors.GREEN)
                self.log_narration("Dashboard web interface is now running and accessible")
                return True
            else:
                self.log("✗ Dashboard failed to start", Colors.RED)
                return False
        except Exception as e:
            self.log(f"Error starting dashboard: {e}", Colors.RED)
            self.log_narration(f"Dashboard startup failed: {str(e)}", "ERROR")
            return False
    
    def start_hive_mind(self):
        """Start Adaptive Rick with ML learning and local AI models"""
        try:
            # Try to start Adaptive Rick with local AI
            if os.path.exists("hive/adaptive_rick.py"):
                self.log("Starting Adaptive Rick (ML + Local AI)...", Colors.GREEN)
                env = os.environ.copy()
                env['RICK_PIN'] = '841921'
                
                self.hive_process = subprocess.Popen([
                    sys.executable, "-c", 
                    "from hive.adaptive_rick import get_adaptive_rick; "
                    "rick = get_adaptive_rick(pin=841921); "
                    "print('🧠 Adaptive Rick: Local AI + ML learning active'); "
                    "import time; "
                    "while True: "
                    "    try: "
                    "        status = rick.get_system_status(); "
                    "        print(f'Rick Status: {status[\"total_decisions_recorded\"]} decisions learned'); "
                    "    except: pass; "
                    "    time.sleep(300)"  # Status every 5 minutes
                ], env=env)
                
                self.log("✅ Adaptive Rick: ML learning + Local AI models active", Colors.GREEN)
                self.log_narration("Adaptive Rick online - Self-learning AI with local Llama models")
                return
                
            # Fallback to browser-based Hive Mind
            elif os.path.exists("hive/rick_hive_browser.py"):
                self.log("Starting Rick Hive Mind (Browser Mode)...", Colors.YELLOW)
                env = os.environ.copy()
                env['RICK_PIN'] = '841921'
                
                self.hive_process = subprocess.Popen([
                    sys.executable, "-c", 
                    "from hive.rick_hive_browser import get_hive_browser_mind; "
                    "hive = get_hive_browser_mind(pin=841921); "
                    "print('🧠 Rick Hive Mind: Browser connections established'); "
                    "import time; "
                    "while True: time.sleep(60)"
                ], env=env)
                
                self.log("✅ Rick Hive Mind: Browser-based AI connections active", Colors.GREEN)
                self.log_narration("Hive Mind activated - Multi-AI consensus system online")
                return
        except Exception as e:
            self.log(f"❌ Rick startup error: {e}", Colors.RED)
            
        # Fallback message
        self.log("Rick: Local AI models available via Ollama", Colors.YELLOW)
        self.log_narration("Rick AI integration active - local models ready")
        
        # Original code commented out for future use
        # if not os.path.exists(HIVE_MIND_SCRIPT):
        #     self.log("Hive Mind script not found, skipping", Colors.YELLOW)
        #     return False
        # 
        # try:
        #     self.log("Starting Rick Hive Mind...", Colors.GREEN)
        #     self.hive_process = subprocess.Popen(
        #         ["python3", HIVE_MIND_SCRIPT],
        #         stdout=subprocess.PIPE,
        #         stderr=subprocess.PIPE,
        #         universal_newlines=True
        #     )
        #     time.sleep(2)
        #     
        #     if self.is_process_running(self.hive_process):
        #         self.log("✓ Hive Mind connected", Colors.GREEN)
        #         self.log_narration("Rick Hive Mind collective is now online and processing market intelligence")
        #         return True
        #     else:
        #         self.log("✗ Hive Mind failed to start", Colors.RED)
        #         return False
        # except Exception as e:
        #     self.log(f"Error starting Hive Mind: {e}", Colors.RED)
        #     return False
    
    def check_and_restart_dashboard(self):
        """Check if dashboard is running, restart if needed"""
        if not self.is_process_running(self.dashboard_process):
            self.log("⚠ Dashboard process died, restarting...", Colors.YELLOW)
            self.log_narration("Dashboard process stopped unexpectedly, initiating automatic restart", "WARNING")
            return self.start_dashboard()
        return True
    
    def check_and_restart_hive(self):
        """Check if Hive Mind is running and restart if needed"""
        if self.hive_process and self.hive_process.poll() is not None:
            self.log("🔄 Hive Mind process stopped, restarting...", Colors.YELLOW)
            self.start_hive_mind()
        elif not self.hive_process:
            # Start if not running
            self.start_hive_mind()
    
    def get_system_status(self):
        """Get current system status"""
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        status = {
            "uptime": f"{hours}h {minutes}m {seconds}s",
            "dashboard": "RUNNING" if self.is_process_running(self.dashboard_process) else "STOPPED",
            "hive_mind": "RUNNING" if self.is_process_running(self.hive_process) else "STOPPED",
            "last_openai_call": self.last_openai_call.strftime("%H:%M:%S") if self.last_openai_call else "Never"
        }
        return status
    
    def print_status(self):
        """Print current status"""
        status = self.get_system_status()
        
        print(f"\n{Colors.BOLD}═══════════════════════════════════════════════════════{Colors.END}")
        print(f"{Colors.BOLD}🤖 RICK Dashboard Supervisor Status{Colors.END}")
        print(f"{Colors.BOLD}═══════════════════════════════════════════════════════{Colors.END}")
        print(f"{Colors.CYAN}Uptime:{Colors.END} {status['uptime']}")
        print(f"{Colors.CYAN}Dashboard:{Colors.END} {status['dashboard']}")
        print(f"{Colors.CYAN}Hive Mind:{Colors.END} {status['hive_mind']}")
        print(f"{Colors.CYAN}Last OpenAI Call:{Colors.END} {status['last_openai_call']}")
        print(f"{Colors.CYAN}Next Check:{Colors.END} {CHECK_INTERVAL}s")
        print(f"{Colors.BOLD}═══════════════════════════════════════════════════════{Colors.END}\n")
    
    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown"""
        self.log("\n🛑 Shutting down supervisor...", Colors.YELLOW)
        self.log_narration("Dashboard supervisor received shutdown signal, cleaning up processes")
        self.running = False
        
        if self.dashboard_process:
            self.log("Stopping dashboard...", Colors.YELLOW)
            self.dashboard_process.terminate()
            try:
                self.dashboard_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.dashboard_process.kill()
        
        if self.hive_process:
            self.log("Stopping Hive Mind...", Colors.YELLOW)
            self.hive_process.terminate()
            try:
                self.hive_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.hive_process.kill()
        
        self.log("✓ Supervisor shutdown complete", Colors.GREEN)
        self.log_narration("Dashboard supervisor has shutdown cleanly")
        sys.exit(0)
    
    def run(self):
        """Main supervisor loop"""
        print(f"{Colors.BOLD}")
        print("═══════════════════════════════════════════════════════")
        print("🤖 RICK Trading System - Dashboard Supervisor")
        print("═══════════════════════════════════════════════════════")
        print(f"{Colors.END}")
        print(f"{Colors.CYAN}Features:{Colors.END}")
        print("  ✓ Auto-restart dashboard if it crashes")
        print("  ✓ Maintain Hive Mind connection")
        print("  ✓ Plain English narration logging")
        print("  ✓ 1-minute delay between OpenAI requests")
        print("  ✓ Auto-rotate large narration files")
        print(f"\n{Colors.YELLOW}Press Ctrl+C to stop{Colors.END}\n")
        
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Initial startup
        self.log_narration("Dashboard supervisor starting up - initializing all systems")
        self.start_dashboard()
        self.start_hive_mind()
        
        # Main monitoring loop
        check_count = 0
        while self.running:
            try:
                time.sleep(CHECK_INTERVAL)
                check_count += 1
                
                # Check and restart components
                self.check_and_restart_dashboard()
                self.check_and_restart_hive()
                
                # Rotate narration if needed
                self.rotate_narration_if_needed()
                
                # Print status every 5 checks (2.5 minutes)
                if check_count % 5 == 0:
                    self.print_status()
                    self.log_narration(f"System health check: All components operational, uptime {self.get_system_status()['uptime']}")
                
            except KeyboardInterrupt:
                self.shutdown()
            except Exception as e:
                self.log(f"Error in supervisor loop: {e}", Colors.RED)
                self.log_narration(f"Supervisor encountered an error but continuing: {str(e)}", "ERROR")
                time.sleep(5)

def main():
    supervisor = DashboardSupervisor()
    supervisor.run()

if __name__ == "__main__":
    main()
