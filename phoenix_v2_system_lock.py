#!/usr/bin/env python3
"""
Install or update files to 'lock' the Phoenix V2 project into a secure configuration.
This does not run the heavy operations (isolate/move) automatically; those are left to the operator.
"""
import os
import stat
import textwrap

FILES = {
    'scripts/isolate_phoenix.py': None,  # created by separate process
    'start_phoenix_v2.sh': None,
}

def ensure_scripts():
    # Ensure scripts and logs directories exist
    os.makedirs('scripts', exist_ok=True)
    os.makedirs('PhoenixV2/logs', exist_ok=True)

    # Make start script executable
    if os.path.exists('start_phoenix_v2.sh'):
        st = os.stat('start_phoenix_v2.sh')
        os.chmod('start_phoenix_v2.sh', st.st_mode | stat.S_IEXEC)
        print('Made start_phoenix_v2.sh executable')

    # Make isolate script executable if it exists
    if os.path.exists('scripts/isolate_phoenix.py'):
        st = os.stat('scripts/isolate_phoenix.py')
        os.chmod('scripts/isolate_phoenix.py', st.st_mode | stat.S_IEXEC)
        print('Made scripts/isolate_phoenix.py executable')

def print_next_steps():
    print(textwrap.dedent('''
    ✅ Phoenix V2 System Lock prepared.

    Next steps:
    1. Review the package and .env to ensure only PhoenixV2 is active in the repo.
    2. Optionally run: python3 scripts/isolate_phoenix.py --force
    3. Optionally run optimizer: python3 PhoenixV2/backtest/optimizer.py
    4. Start the supervisor: ./start_phoenix_v2.sh
    ''').strip())

def main():
    ensure_scripts()
    print_next_steps()

if __name__ == '__main__':
    main()
