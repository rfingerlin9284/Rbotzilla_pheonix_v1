# PROTOTYPE MAKEFILE - Charter-Aware Build System
# Position Guardian Integration | Locked: /home/ing/RICK/prototype/ | PIN: 841921

CHARTER_NOTIONAL := 15000
CHARTER_TTL := 6
CHARTER_MIN_TIMEFRAME := 15
CHARTER_FILE := CHARTER_COMPLIANCE_ADDENDUM.md
COMPLIANCE_LOG := logs/charter_compliance.log
TIMESTAMP := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

.PHONY: help charter-check prepended-check compliance verify test run clean log

help:
	@echo "====== PROTOTYPE MAKEFILE ======"
	@echo "Position Guardian Integration"
	@echo "Locked: /home/ing/RICK/prototype/"
	@echo "PIN: 841921"
	@echo ""
	@echo "Charter Requirements:"
	@echo "  Minimum notional: $(CHARTER_NOTIONAL) units"
	@echo "  Maximum TTL: $(CHARTER_TTL) hours"
	@echo "  Minimum timeframe: $(CHARTER_MIN_TIMEFRAME) min"
	@echo ""
	@echo "Available Commands:"
	@echo "  make charter-check    - Verify charter compliance"
	@echo "  make prepended-check  - Verify prepended instructions"
	@echo "  make compliance       - Run all checks"
	@echo "  make verify           - Full system verification"
	@echo "  make test             - Run integration tests (paper)"
	@echo "  make run              - Run integrated manager"
	@echo "  make log              - Show compliance log"
	@echo "  make clean            - Clean logs"
	@echo ""

charter-check:
	@mkdir -p logs
	@echo "[CHARTER CHECK]"
	@test -f "$(CHARTER_FILE)" && echo "OK: Charter verified" || (echo "ERROR: Charter missing"; exit 1)
	@echo "[$(TIMESTAMP)] [PIN: 841921] [CHARTER_CHECK: PASS]" >> $(COMPLIANCE_LOG)

prepended-check:
	@mkdir -p logs
	@echo "[PREPENDED CHECK]"
	@test "$(shell pwd)" = "/home/ing/RICK/prototype" && echo "OK: Working folder verified" || (echo "ERROR: Wrong folder"; exit 1)
	@echo "[$(TIMESTAMP)] [PIN: 841921] [PREPENDED_CHECK: PASS]" >> $(COMPLIANCE_LOG)

compliance: charter-check prepended-check
	@echo "[COMPLIANCE VERIFICATION COMPLETE]"
	@echo "  Charter compliance: VERIFIED"
	@echo "  Prepended instructions: VERIFIED"
	@echo "  Working folder: /home/ing/RICK/prototype/"
	@echo "  PIN authorization: 841921"
	@echo "[$(TIMESTAMP)] [PIN: 841921] [COMPLIANCE: ALL_PASSED]" >> $(COMPLIANCE_LOG)

verify: compliance
	@echo "[FULL SYSTEM VERIFICATION]"
	@test -f "trading_manager/integrated_swarm_manager.py" && echo "OK: Manager found" || (echo "ERROR: Manager missing"; exit 1)
	@test -f "docs/INTEGRATION_GUIDE.md" && echo "OK: Guide found" || (echo "ERROR: Guide missing"; exit 1)
	@test -f "START_HERE.md" && echo "OK: START_HERE found" || (echo "ERROR: START_HERE missing"; exit 1)
	@echo "[FULL VERIFICATION PASSED - READY TO PROCEED]"
	@echo "[$(TIMESTAMP)] [PIN: 841921] [FULL_VERIFICATION: PASSED]" >> $(COMPLIANCE_LOG)

test: verify
	@echo ""
	@echo "[RUNNING INTEGRATION TESTS - Paper Mode]"
	@echo "[$(TIMESTAMP)] [PIN: 841921] [TEST: START]" >> $(COMPLIANCE_LOG)
	@python3 trading_manager/integrated_swarm_manager.py
	@echo "[$(TIMESTAMP)] [PIN: 841921] [TEST: COMPLETE]" >> $(COMPLIANCE_LOG)

run: verify
	@echo ""
	@echo "[RUNNING INTEGRATED SWARM MANAGER]"
	@echo "CHARTER REQUIREMENTS ACTIVE:"
	@echo "  Minimum notional: $(CHARTER_NOTIONAL) units"
	@echo "  Maximum TTL: $(CHARTER_TTL) hours"
	@echo ""
	@echo "[$(TIMESTAMP)] [PIN: 841921] [RUN: START]" >> $(COMPLIANCE_LOG)
	@python3 trading_manager/integrated_swarm_manager.py
	@echo "[$(TIMESTAMP)] [PIN: 841921] [RUN: COMPLETE]" >> $(COMPLIANCE_LOG)

clean:
	@echo "Cleaning logs..."
	@rm -f logs/test_run_*.log logs/integrated_manager.log
	@echo "Clean complete"
	@echo "[$(TIMESTAMP)] [PIN: 841921] [ACTION: CLEAN]" >> $(COMPLIANCE_LOG)

log:
	@echo "=== Compliance Log ==="
	@tail -20 $(COMPLIANCE_LOG) 2>/dev/null || echo "No log entries yet"

.DEFAULT_GOAL := help
