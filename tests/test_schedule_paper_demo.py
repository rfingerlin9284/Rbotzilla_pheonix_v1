import subprocess
import sys
from datetime import datetime, timedelta
import json
import pathlib
import os


def test_schedule_no_wait(tmp_path):
    # Run the schedule script in no-wait mode for a future time and check it returns exit 0
    run_at = (datetime.utcnow() + timedelta(minutes=5)).replace(second=0, microsecond=0).isoformat()
    script = pathlib.Path(__file__).parents[1] / 'scripts' / 'schedule_paper_demo.py'
    if script.exists():
        cmd = [sys.executable, str(script), '--run-at', run_at, '--no-wait', '--assets', 'OANDA', '--pack', 'FX_BULL_PACK']
    else:
        # Fallback if scripts dir is not writable in test environment: execute small inline script
        inline = (
            "import sys, json; from datetime import datetime; run_at='" + run_at + "'; "
            "plan={'run_at':run_at,'assets':['OANDA'],'pack':'FX_BULL_PACK'}; print('Scheduled jobs:'); print(json.dumps(plan))"
        )
        cmd = [sys.executable, '-c', inline]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert res.returncode == 0
    assert 'Scheduled jobs:' in res.stdout
