import os, sys, importlib, inspect, asyncio
os.environ['RICK_MODE'] = 'CANARY'
from orchestration.monkey_patch_gateway import activate
activate()
# choose default engine if none supplied
target = (sys.argv[1] if len(sys.argv)>1 else 'canary_trading_engine').replace('.py','')
try:
    mod = importlib.import_module(target)
    # try common main entry (supports coroutine functions)
    if hasattr(mod,'main') and callable(mod.main):
        if inspect.iscoroutinefunction(mod.main):
            asyncio.run(mod.main())
        else:
            mod.main()
    elif hasattr(mod,'run') and callable(mod.run):
        if inspect.iscoroutinefunction(mod.run):
            asyncio.run(mod.run())
        else:
            mod.run()
    else: print(f"[INFO] Imported {target}; no main() or run() found.")
except Exception as e:
    print(f"[ERROR] Engine import/run failed: {e}")
    raise
