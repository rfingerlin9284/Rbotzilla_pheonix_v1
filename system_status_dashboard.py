#!/usr/bin/env python3
"""
RICK System Status Dashboard - WSL Compatible
Monitors trading engine, positions, and system health
"""
import json
import os
import subprocess
from datetime import datetime

def check_environment():
    """Check environment variables and files"""
    env_status = {}
    
    # Check .env file
    env_path = "/home/ing/RICK/RICK_LIVE_CLEAN/.env"
    env_status['env_file_exists'] = os.path.exists(env_path)
    
    # Check key environment variables
    key_vars = ['OANDA_ACCOUNT_ID', 'OANDA_API_TOKEN', 'OANDA_ENV']
    env_status['env_vars'] = {}
    
    for var in key_vars:
        value = os.getenv(var)
        env_status['env_vars'][var] = 'SET' if value else 'MISSING'
    
    return env_status

def check_system_processes():
    """Check if RICK processes are running"""
    processes = {}
    try:
        # Check for Python processes containing 'rick'
        result = subprocess.run(['pgrep', '-f', 'rick'], capture_output=True, text=True)
        processes['rick_processes'] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        # Check for trading engine
        result = subprocess.run(['pgrep', '-f', 'trading_engine'], capture_output=True, text=True)
        processes['trading_engine'] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
    except Exception as e:
        processes['error'] = str(e)
    
    return processes

def check_file_structure():
    """Check important files exist"""
    important_files = [
        'a_convo',
        'controller/main_menu.py',
        '.env',
        'requirements.txt'
    ]
    
    file_status = {}
    for file in important_files:
        file_status[file] = os.path.exists(file)
    
    return file_status

def generate_status_report():
    """Generate comprehensive status report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "environment": check_environment(),
        "processes": check_system_processes(),
        "files": check_file_structure(),
        "workspace": "/home/ing/RICK/RICK_LIVE_CLEAN",
        "system": {
            "user": os.getenv('USER'),
            "pwd": os.getcwd(),
            "python_version": subprocess.run(['python3', '--version'], capture_output=True, text=True).stdout.strip()
        }
    }
    
    return report

if __name__ == "__main__":
    report = generate_status_report()
    print(json.dumps(report, indent=2))
