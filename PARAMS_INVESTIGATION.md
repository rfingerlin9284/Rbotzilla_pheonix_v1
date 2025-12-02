# 🔍 INVESTIGATION REPORT: The "params" Mystery Solved

## What You Asked
**"WHY DID MY AGENT ADD PARAMS? SEEMS THATS WHEN ISSUES STARTED"**

## The Truth: The Bug Was ALREADY in the "Verified" Branch

### Timeline Discovery

1. **October 27, 2025** - "live-verified-98pc-2025-10-27" branch created
   - Commit: `940db38d3a6b05fcd669b754249fce8abe845ec6`
   - **BUG ALREADY PRESENT**:
     - `get_historical_data()` calls: `_make_request("GET", endpoint, params=params)` 
     - `_make_request()` signature: `def _make_request(self, method, endpoint, data=None)` ❌ NO params!

2. **November 7, 2025** - I restored files from that branch
   - I did NOT add params - it was already there!
   - I just restored the exact code that was already broken

### How Did It Ever Work?

The system had a **workaround** in place:

**File**: `runtime_guard/sitecustomize.py` (lines 107-158)

This file patches the `_make_request` method at runtime to accept `params`:

```python
def _patch_oanda_connector(module):
    # Wrap _make_request to accept params kw and fold into endpoint for GET
    orig_mr = getattr(OC, "_make_request", None)
    def _mr_wrapped(self, method, endpoint, data=None, **kwargs):
        params = kwargs.pop("params", None)
        if params and str(method).upper() == "GET":
            endpoint = _ensure_qs(endpoint, params)  # Merge params into URL
        return orig_mr(self, method, endpoint, data)
    
    setattr(OC, "_make_request", _mr_wrapped)
```

### Why It's Failing Now

**Python only loads `sitecustomize.py` if**:
1. It's in a directory on PYTHONPATH, OR
2. It's in the Python site-packages directory

**Current situation**:
- File exists at: `./runtime_guard/sitecustomize.py`
- But `./runtime_guard/` is NOT in PYTHONPATH
- So Python never loads it
- So the patch never happens
- So `params` keyword fails

---

## The Two Solutions

### Solution 1: Fix the Code Properly (RECOMMENDED)
**What I did**: Add `params` parameter to `_make_request` signature

```python
# Before (broken):
def _make_request(self, method: str, endpoint: str, data: Dict = None):
    if method.upper() == "GET":
        response = requests.get(url, headers=self.headers, timeout=...)

# After (fixed):
def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None):
    if method.upper() == "GET":
        response = requests.get(url, headers=self.headers, params=params, timeout=...)
```

**Pros**:
- ✅ Clean, permanent fix
- ✅ No runtime patching needed
- ✅ Standard Python/requests pattern
- ✅ Easy to understand and maintain

**Cons**:
- Changes the "verified" code
- But the verified code was already broken!

### Solution 2: Use the Runtime Patch (WORKAROUND)
**Method A**: Copy sitecustomize.py to root:
```bash
cp runtime_guard/sitecustomize.py ./sitecustomize.py
```

**Method B**: Add to PYTHONPATH before running:
```bash
export PYTHONPATH=/home/runner/work/rick_clean_live/rick_clean_live/runtime_guard:$PYTHONPATH
python3 oanda_trading_engine.py
```

**Pros**:
- ✅ Doesn't change any "core" files
- ✅ Follows the original workaround pattern

**Cons**:
- ❌ Fragile - easy to forget to set PYTHONPATH
- ❌ Hard to debug - patches happen invisibly at runtime
- ❌ Not portable - breaks if you run from different directory

---

## My Recommendation

**Keep Solution 1 (my fix)** because:

1. **The "verified" branch was already broken** - it had the params mismatch
2. **The workaround is fragile** - depends on PYTHONPATH being set correctly
3. **My fix is the standard pattern** - `requests.get()` DOES accept params
4. **It's cleaner** - no runtime monkey-patching needed

The fact that someone needed to create `sitecustomize.py` to patch this proves the original code was broken!

---

## Bottom Line

**You didn't break it. It was already broken.**

The "verified" branch had a mismatch between:
- What `get_historical_data()` expected (`_make_request` to accept params)
- What `_make_request()` actually provided (no params support)

Someone created a runtime patch as a workaround, but that patch isn't loading because PYTHONPATH isn't set up.

**My fix makes the code work correctly without needing runtime patches.**

---

## What Should We Do?

**Option 1**: Keep my fix (recommended)
- System works without runtime patches
- Code is cleaner and more maintainable

**Option 2**: Revert my fix and use the runtime patch
- Copy sitecustomize.py to root OR set PYTHONPATH
- Preserves the "original" (broken) code with workaround

**Which do you prefer?**
