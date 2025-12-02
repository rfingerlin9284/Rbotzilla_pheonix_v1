#!/usr/bin/env python3
"""
Supervisor script for PHOENIX V2.
Monitors `main.py` and keeps it running, enforcing target mode and connectivity.
"""
import time
import subprocess
import os
import json
import signal
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [SUPERVISOR] %(message)s')
logger = logging.getLogger('Supervisor')

ROOT = Path(__file__).resolve().parents[0]
MAIN = ROOT / 'main.py'
LOGS = ROOT / 'logs'
STATUS = LOGS / 'system_status.json'


def is_process_running(cmd_fragment: str):
    """Return True if a process containing cmd_fragment is running."""
    try:
        out = subprocess.check_output(['pgrep', '-f', cmd_fragment])
        return bool(out.strip())
    except subprocess.CalledProcessError:
        return False


def start_main(force_live=False):
    os.makedirs(LOGS, exist_ok=True)
    if force_live:
        proc = subprocess.Popen(['python3', str(MAIN), '--force-live'], cwd=str(ROOT), stdout=open(LOGS / 'main.out', 'a'), stderr=open(LOGS / 'main.err', 'a'))
    else:
        proc = subprocess.Popen(['python3', str(MAIN)], cwd=str(ROOT), stdout=open(LOGS / 'main.out', 'a'), stderr=open(LOGS / 'main.err', 'a'))
    return proc


def kill_main():
    try:
        out = subprocess.check_output(['pgrep', '-f', str(MAIN)])
        pids = [int(x) for x in out.split() if x.strip()]
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
            except Exception:
                pass
    except subprocess.CalledProcessError:
        pass


def ping_ok(host='8.8.8.8'):
    try:
        r = subprocess.run(['ping', '-c', '1', host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return r.returncode == 0
    except Exception:
        return False


def read_status():
    try:
        with open(STATUS, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def main_loop():
    os.makedirs(LOGS, exist_ok=True)
    pidfile = LOGS / 'supervisor.pid'
    if pidfile.exists():
        try:
            prev = int(pidfile.read_text())
            os.kill(prev, 0)
            logger.info('Supervisor already running. Exiting...')
            return
        except Exception:
            pass
    pidfile.write_text(str(os.getpid()))

    proc = None
    logger.info('Supervisor starting...')
    while True:
        try:
            connected = ping_ok()
            if not is_process_running(str(MAIN)) and connected:
                logger.warning('Main not running, starting...')
                proc = start_main(force_live=False)
            status = read_status()
            current_mode = status.get('current_mode', 'PAPER').upper()
            target_mode = status.get('target_mode', os.getenv('TARGET_MODE', os.getenv('MODE', 'PAPER'))).upper()
            if current_mode != target_mode and target_mode == 'LIVE' and connected:
                logger.warning('Mode mismatch; forcing LIVE restart...')
                kill_main()
                proc = start_main(force_live=True)
            if not connected:
                logger.warning('Connectivity lost; killing main process')
                kill_main()
            time.sleep(10)
        except KeyboardInterrupt:
            logger.info('Supervisor stopping...')
            kill_main()
            break
        except Exception as e:
            logger.exception('Supervisor encountered error: %s', e)
            time.sleep(10)


if __name__ == '__main__':
    main_loop()
