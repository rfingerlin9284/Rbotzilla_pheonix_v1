# AGENT CHARTER v2 (RICK_PHOENIX)
**USER ROLE**: Creator (Absolute Authority) | **AUTH**: 841921

## ARCHITECTURE: HIVE MIND vs RBOTZILLA
1. **THE BRAIN**: RICK Hive Mind (Inference Only).
2. **THE BODY**: RBotZilla (Execution & Safety).

## IMMUTABLE RULES
1. **NO PARTIAL PATCHES**: Output ENTIRE FILE content.
2. **SEMANTICS**: "Canary"/"Ghost" -> **"Paper"**.
3. **MICRO-TRADING**: 
   - **DISABLED** by default (< 1000 units rejected).
   - **M15 FLOOR**: No M1/M5 logic allowed without explicit override.
4. **STATE**: All changes must be logged via `change_tracker.py`.
