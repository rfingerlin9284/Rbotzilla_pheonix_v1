#!/usr/bin/env python3
from foundation.system_goals import get_goals, is_battle_ready
import json

goals = get_goals()
print('SYSTEM GOALS:')
print(json.dumps(goals, indent=2))
print(f"\nBattle ready: {is_battle_ready()}")
