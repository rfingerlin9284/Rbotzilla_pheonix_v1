import importlib
from orchestration._miniyaml import load

CFG_GATES = load('config/gates.yaml') if __import__('os').path.exists('config/gates.yaml') else {'rick_hive':{'enabled':False}}

def _maybe(mod,name):
    try:
        m = importlib.import_module(mod)
        return getattr(m,name) if hasattr(m,name) else None
    except Exception:
        return None

def advisors():
    a = CFG_GATES.get('rick_hive',{}).get('advisors',[])
    res=[]
    for name in a:
        # try hive.<name>, logic.<name>, risk.<name>
        for mod in (f'hive.{name}', f'logic.{name}', f'risk.{name}'):
            fn = _maybe(mod, 'advise') or _maybe(mod, name) or _maybe(mod, 'run')
            if fn: res.append((name, fn)); break
    return res

def decide(ctx):
    cfg = CFG_GATES.get('rick_hive',{})
    if not cfg.get('enabled',False): return True, {'enabled':False,'reason':'disabled'}
    votes, detail = 0, {}
    for nm,fn in advisors():
        try:
            out = fn(ctx)  # expected True/False or dict with 'pass'
            ok = bool(out if isinstance(out,bool) else out.get('pass',False))
            votes += 1 if ok else 0
            detail[nm] = ok
        except Exception as e:
            detail[nm] = f'error:{e}'
    quorum = int(cfg.get('quorum',1))
    passed = votes >= quorum
    return passed, {'enabled':True,'votes':votes,'quorum':quorum,'detail':detail}
