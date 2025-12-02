"""
Shim for util.breakpoint_audit when run under repository root.

This tries to prefer `rick_clean_live.util.breakpoint_audit` if present,
otherwise provides no-op stand-ins so the engine can import without crashing
in environments where `breakpoint_audit` is missing.
"""
try:
    # Prefer the real implementation in rick_clean_live/util
    from rick_clean_live.util.breakpoint_audit import attach_audit_handler, audit_event
except Exception:
    # Fallback no-op implementations
    def attach_audit_handler(*args, **kwargs):
        return None

    def audit_event(*args, **kwargs):
        return None
