.PHONY: start stop status logs clean
# Add a convenience target for the live narration view
.PHONY: narration

start:
	@echo "RICK: Launching autonomous trading system (AMM + OANDA + IBKR)"
	@mkdir -p logs
	@./scripts/start_all.sh

stop:
	@./scripts/stop_all.sh
	@echo "RICK: All trading services stopped"

status:
	@ps aux | grep run_autonomous.py | grep -v grep || echo "No process running"
	@tail -n 10 narration.jsonl 2>/dev/null || echo "No narration yet"

logs:
	@tail -f narration.jsonl 2>/dev/null || echo "No narration yet"

narration:
	@./util/plain_english_narration.sh

clean:
	@make stop
	@rm -f logs/*.log
