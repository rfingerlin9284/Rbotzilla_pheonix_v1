def load(path):
    """Very small YAML subset loader supporting maps and inline flow maps.
    Converts simple inline flow maps like `{ a: 1, b: true }` into dict recursively.
    This is intentionally minimal to avoid external deps.
    """
    def parse_scalar(tok: str):
        t = tok.strip()
        if t.lower() in ('true','false'): return t.lower()=='true'
        if t.startswith(("'","\"")) and t.endswith(("'","\"")) and len(t)>=2:
            return t[1:-1]
        try:
            if '.' in t: return float(t)
            return int(t)
        except: return t

    def parse_flow_map(s: str):
        # Remove outer braces
        inner = s.strip()[1:-1].strip()
        if not inner: return {}
        out = {}
        depth = 0; start = 0; parts = []
        for i,ch in enumerate(inner):
            if ch in '{[': depth += 1
            elif ch in '}]': depth -= 1
            elif ch == ',' and depth==0:
                parts.append(inner[start:i].strip()); start = i+1
        parts.append(inner[start:].strip())
        for p in parts:
            if not p: continue
            if ':' not in p: continue
            k,v = [x.strip() for x in p.split(':',1)]
            if v.startswith('{') and v.endswith('}'):
                out[k] = parse_flow_map(v)
            elif v.startswith('[') and v.endswith(']'):
                # simple list split
                lst_inner = v[1:-1].strip()
                if lst_inner:
                    out[k] = [parse_scalar(x) for x in lst_inner.split(',')]
                else:
                    out[k] = []
            else:
                out[k] = parse_scalar(v)
        return out

    root = {}
    stack = [(0, root)]
    with open(path,'r',encoding='utf-8') as fh:
        for raw in fh:
            if not raw.strip() or raw.lstrip().startswith('#'): continue
            indent = len(raw) - len(raw.lstrip(' '))
            line = raw.strip()

            def up_to(i):
                while len(stack)>1 and stack[-1][0] >= i:
                    stack.pop()

            if line.startswith('- '):
                key = list(stack[-1][1].keys())[-1]
                stack[-1][1].setdefault(key, []).append(parse_scalar(line[2:].strip()))
                continue

            if ':' in line:
                k,v = [s.strip() for s in line.split(':',1)]
                if v == '':
                    up_to(indent); d={}
                    stack[-1][1][k]=d; stack.append((indent+1,d))
                else:
                    if v.startswith('{') and v.endswith('}'):
                        val = parse_flow_map(v)
                    elif v.startswith('[') and v.endswith(']'):
                        inner = v[1:-1].strip()
                        val = [parse_scalar(x) for x in inner.split(',')] if inner else []
                    else:
                        val = parse_scalar(v)
                    up_to(indent); stack[-1][1][k]=val
    return root
