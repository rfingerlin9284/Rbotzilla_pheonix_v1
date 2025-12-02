Copilot said: **GOAL:** Implement auto-close on SL update failure
GOAL: Implement auto-close on SL update failure feature and add comprehensive test coverage for the hive confidence override.

Persona symphony plan:

ENGINEER (primary): Implement the auto-close logic, add tests for hive confidence
MENTOR_BK (secondary): Ensure reversible changes with proper testing
PROF_QUANT (minimal): Verify confidence thresholds maintain profitable edge
TRADER_PSYCH (minimal): Ensure fail-safes prevent panic closures
Summary of Changes Made
1. Auto-Close on SL Update Failure ✅
The feature is already implemented in oanda_trading_engine.py:

_apply_adaptive_trailing_sl() method has force_close_on_fail parameter
Controlled by FORCE_CLOSE_ON_SL_UPDATE_FAILURE env variable (default: 0)
When enabled (=1), if trailing stop update fails after retries, the engine attempts to close the position
Logs TRAILING_SL_FORCE_CLOSE_ATTEMPT with success/failure details
2. Hive Confidence Override Testing ✅
Added comprehensive test coverage in test_hive_confidence_override.py:

Test 1: Dev mode allows lower confidence (0.6)
Test 2: Production enforces charter minimum (0.8)
Test 3: Higher values always respected
Test 4: Invalid strings default to safe value
3. Environment Variables Documented ✅
Updated .env.example with:

HIVE_TRIGGER_CONFIDENCE=0.60 - Hive consensus threshold
FORCE_CLOSE_ON_SL_UPDATE_FAILURE=0 - Auto-close on SL failure (off by default)
How to Use Auto-Close Feature
Enable in .env:
bash
FORCE_CLOSE_ON_SL_UPDATE_FAILURE=1
Monitor logs for:
TRAILING_SL_SET_FAILED - Initial failure
TRAILING_SL_FORCE_CLOSE_ATTEMPT - Auto-close triggered
Check success field to see if close succeeded
Safety notes:
Only triggers after multiple retry failures
Logs all attempts for audit trail
Position may close at unfavorable price during volatility
Use with caution in production
Test Results
All tests passing:

✅ Trailing engine tests
✅ OANDA trailing retry/apply tests
✅ Hive confidence override tests
✅ Micro trade filter tests
RESULTS/ARTIFACTS:
test_hive_confidence_override.py - Comprehensive test coverage
Updated .env.example with new variables
Auto-close feature ready to use (already implemented)
All existing tests continue to pass
NEXT:
Set FORCE_CLOSE_ON_SL_UPDATE_FAILURE=1 in your .env to enable auto-close
Set RICK_DEV_MODE=1 and HIVE_TRIGGER_CONFIDENCE=0.60 for more trades
Monitor logs for TRAILING_SL_FORCE_CLOSE_ATTEMPT events
Adjust thresholds based on observed behavior
The auto-close feature provides a safety net when trailing stop updates fail, helping prevent the 41-pip losses you experienced. Combined with the lowered hive confidence (60%), you should see more trade opportunities while maintaining protection.

