#!/bin/bash
set -e

echo "�� COMPREHENSIVE WORKSPACE CLEANUP - Removing unused files..."

# Create archive directory if it doesn't exist
mkdir -p archives/pre_cleanup_$(date +%Y%m%d_%H%M%S)
ARCHIVE="archives/pre_cleanup_$(date +%Y%m%d_%H%M%S)"

# Move documentation markdown files (keeping only essential ones)
echo "📝 Archiving excessive documentation..."
for doc in \
    AGENT_*.md \
    AUDIT_*.md ANALYSIS_*.md ANSWER_*.md \
    CANARY_*.md CAPITAL_*.md CHARTER_*.md \
    CODE_*.md COINBASE_*.md COMPLETE_*.md COMPLETION_*.md COMPONENTS_*.md COMPREHENSIVE_*.md \
    CONFIGURATION_*.md CONTINUOUS_*.md COPY_PASTE_*.md CRITICAL_*.md CRYPTO_*.md CURRENCY_*.md \
    DELIVERABLES.md DIRECT_*.md DISABLE_*.md DOCKER_*.md DO_THIS_NOW.md \
    ENDPOINT_*.md ENV_README.md ENVIRONMENT_*.md EXECUTIVE_*.md EXECUTION_*.md \
    FASTEST_*.md FILE_*.md FINAL_*.md FOUND_*.md FRONTEND_*.md \
    GAP_*.md GHOST_*.md GOVERNANCE_*.md GUARDIAN_*.md \
    HANDOFF_*.md \
    IB_*.md IBKR_*.md IMMUTABLE_*.md IMPLEMENTATION_*.md INCOME_*.md INSTITUTIONAL_*.md INTEGRATION_*.md \
    LIVE_*.md \
    MAKEFILE_*.md MANIFEST.txt MAXIMUM_*.md MISSION_*.md MODE_*.md MOMENTUM_*.md MONITORING_*.md MULTI_*.md \
    OCTOBER_*.md OANDA_*.md OPENALGO_*.md \
    PAPER_*.md PATTERN_*.md POLICIES.md PORT_*.md PROGRESS_*.md PROMPTS_*.md \
    QUICK_*.md \
    READY_*.md RECOMMENDED_*.md REFACTORING_*.md RICK_*.md ROLLBACK_*.md RBOTZILLA_*.md \
    SENTINEL_*.md SESSION_*.md SOPHISTICATION_*.md START_*.md STRATEGY_*.md STREAMLIT_*.md SUMMARY_*.md SWARM_*.md SYSTEM_*.md \
    TASK_*.md THREE_*.md TWO_*.md \
    UNIFIED_*.md USD_*.md \
    WOLFPACK_*.md
do
    [ -f "$doc" ] && mv "$doc" "$ARCHIVE/" 2>/dev/null || true
done

# Remove deprecated/backup engines
echo "🗑️ Removing old/deprecated engines..."
rm -f canary_trading_engine_OLD_DEPRECATED.py
rm -f oanda_trading_engine_proto.py
rm -f oanda_swing_paper_trading.py
rm -f enhanced_rick_engine.py
rm -f rick_trading_engine.py
rm -f ghost_trading_*.py
rm -f live_ghost_engine.py
rm -f stochastic_engine.py
rm -f trading_engine.py
rm -f *.py.bak*

# Remove test files (not needed in production)
echo "🧪 Removing test files..."
rm -f test_*.py
rm -f compare_golden_age_tests.py
rm -f discover_available_data.py
rm -f unified_system_test.py

# Remove launch scripts (we have tasks.json now)
echo "🚀 Removing redundant launch scripts..."
rm -f launch_*.sh
rm -f start_*.sh
rm -f activate_*.sh
rm -f control_*.sh
rm -f check_*.sh diagnose_*.sh disable_*.sh enforce_*.sh install_*.sh
rm -f monitor_*.sh canary_summary.sh gen_reveal.sh rbotzilla_docs_sync.sh
rm -f setup_*.sh verify_*.sh view_tmux_session.sh
rm -f stop_dashboard.sh

# Remove one-off utility scripts
echo "🔧 Removing one-off utilities..."
rm -f backend.py dashboard.py
rm -f canary_to_live.py capital_manager.py deploy_*.py
rm -f institutional_charter_agent.py live_monitor.py
rm -f load_env.py market_data_diagnostic.py progress_manager.py
rm -f rbotzilla_*.py rick_deep_dive_analyzer.py
rm -f sentinel_mode.py show_*.py status_report.py
rm -f temp_*.py
rm -f check_*.py setup_personal_accounts.py
rm -f verify_*.py

# Remove old env files
echo "🔐 Cleaning up old env files..."
rm -f env_decrypt.env env_new.env env_new2.env* master_paper_env.env no_place_holders.env
rm -f crypto_first.env

# Remove log files (they'll regenerate)
echo "📋 Removing old logs..."
rm -f *.log *.pid
rm -f canary_trading_report.json capital_summary.json ghost_charter_progress.json
rm -f ml_intelligence_test_report.json PROGRESS_LOG.json

# Remove miscellaneous config files
echo "⚙️ Removing misc config files..."
rm -f Makefile* rick-trading.service system_architecture.*
rm -f .last_immutability_check .narration_policy .upgrade_toggle .dashboard_supervisor.pid
rm -f *.txt *.bat *.dot

# Keep only essential directories, archive others
echo "📁 Archiving unused directories..."
for dir in \
    accumulated_data archives backups blueprints charter_backups \
    dev_candidates final_v001 ml_learning patches pre_upgrade \
    RICK_LIVE_PROTOTYPE rick_intelligence_extracted rbot_arena \
    ROLLBACK_SNAPSHOTS swarm temp_extracted_data tmp wolf_packs \
    🔴_DOCUMENTATION_HUB_🔴
do
    [ -d "$dir" ] && mv "$dir" "$ARCHIVE/" 2>/dev/null || true
done

echo "✅ Cleanup complete! Archived to: $ARCHIVE"
echo "📦 Essential files remaining:"
ls -1 *.py *.sh 2>/dev/null | head -20
