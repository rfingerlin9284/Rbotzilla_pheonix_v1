#!/bin/bash
# PIN: 841921 - Lock ALL code files to read-only (prevent engine from modifying)

set -e

echo "🔒 LOCKING ALL CRITICAL CODE FILES..."

# Lock main engine files
echo "1. Main engine files..."
chmod 444 rick_charter.py 2>/dev/null || true
chmod 444 oanda_trading_engine.py 2>/dev/null || true
chmod 444 canary_trading_engine.py 2>/dev/null || true

# Lock all Python files in brokers/
echo "2. Broker connectors..."
find brokers/ -name "*.py" -exec chmod 444 {} \; 2>/dev/null || true

# Lock all Python files in foundation/
echo "3. Foundation logic..."
find foundation/ -name "*.py" -exec chmod 444 {} \; 2>/dev/null || true

# Lock all Python files in util/
echo "4. Utility modules..."
find util/ -name "*.py" -exec chmod 444 {} \; 2>/dev/null || true

# Lock all Python files in hive/
echo "5. Hive mind systems..."
find hive/ -name "*.py" -exec chmod 444 {} \; 2>/dev/null || true

# Lock all Python files in systems/
echo "6. System modules..."
find systems/ -name "*.py" -exec chmod 444 {} \; 2>/dev/null || true

# Lock dashboard files
echo "7. Dashboard..."
find dashboard/ -name "*.py" -exec chmod 444 {} \; 2>/dev/null || true

# Lock ml_learning files
echo "8. ML modules..."
find ml_learning/ -name "*.py" -exec chmod 444 {} \; 2>/dev/null || true

# Lock governance files
echo "9. Governance system..."
chmod 444 .agent_governance_lock 2>/dev/null || true
chmod 444 .vscode/AGENT_INSTRUCTIONS.md 2>/dev/null || true

# Lock all markdown documentation
echo "10. Documentation..."
find . -maxdepth 1 -name "*.md" -exec chmod 444 {} \; 2>/dev/null || true

# Lock all shell scripts (except this one)
echo "11. Shell scripts..."
find . -maxdepth 1 -name "*.sh" ! -name "lock_all_code.sh" -exec chmod 444 {} \; 2>/dev/null || true

# Ensure logs/ and data/ remain writable for engine
echo "12. Ensuring logs/data writable..."
chmod 755 logs/ 2>/dev/null || mkdir -p logs && chmod 755 logs/
chmod 755 data/ 2>/dev/null || mkdir -p data && chmod 755 data/

echo ""
echo "✅ CODE LOCK COMPLETE"
echo ""
echo "PROTECTED FILES:"
echo "  - All .py files in: brokers/, foundation/, util/, hive/, systems/, dashboard/, ml_learning/"
echo "  - Main engines: rick_charter.py, oanda_trading_engine.py, canary_trading_engine.py"
echo "  - Governance: .agent_governance_lock, AGENT_INSTRUCTIONS.md"
echo "  - Documentation: All .md files"
echo "  - Scripts: All .sh files"
echo ""
echo "WRITABLE DIRECTORIES (engine needs these):"
echo "  - logs/ (for narration and errors)"
echo "  - data/ (for trade records)"
echo ""
echo "⚠️  ENGINE CANNOT MODIFY ITS OWN CODE NOW"
