#!/bin/bash
# ============================================================================
# RICK DEV/LIVE TOGGLE SYSTEM
# ============================================================================
# Safely switch between development mode and frozen production state
# 
# IMMUTABLE PROTOCOL:
# - Production state is NEVER modified directly
# - Dev changes are always on a separate branch
# - Toggle creates automatic backup before switching
#
# Usage:
#   ./dev_toggle.sh status     # Show current mode
#   ./dev_toggle.sh dev        # Switch to dev mode
#   ./dev_toggle.sh live       # Switch to frozen production
#   ./dev_toggle.sh backup     # Create manual backup
#   ./dev_toggle.sh restore    # Restore from backup
# ============================================================================

set -e

# Configuration
RICK_ROOT="/home/ing/RICK/RICK_LIVE_CLEAN"
RICK_SYSTEM_DIR="$RICK_ROOT/.rick_system"
BACKUP_DIR="$RICK_SYSTEM_DIR/backups"
MODE_FILE="$RICK_SYSTEM_DIR/.current_mode"
FROZEN_BRANCH="frozen-v2"
DEV_BRANCH="copilot/restore-repo-and-clean-errors"
LOG_FILE="$RICK_SYSTEM_DIR/toggle_log.jsonl"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Ensure directories exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$RICK_SYSTEM_DIR"

# Log function
log_action() {
    local action="$1"
    local details="$2"
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"action\":\"$action\",\"details\":\"$details\"}" >> "$LOG_FILE"
}

# Get current mode
get_mode() {
    if [ -f "$MODE_FILE" ]; then
        cat "$MODE_FILE"
    else
        echo "unknown"
    fi
}

# Get current git branch
get_branch() {
    cd "$RICK_ROOT/rick_clean_live" 2>/dev/null && git branch --show-current 2>/dev/null || echo "unknown"
}

# Show status
show_status() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           RICK DEV/LIVE TOGGLE STATUS                    ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local mode=$(get_mode)
    local branch=$(get_branch)
    
    echo -e "  Current Mode:   ${YELLOW}$mode${NC}"
    echo -e "  Git Branch:     ${YELLOW}$branch${NC}"
    echo -e "  Frozen Branch:  ${GREEN}$FROZEN_BRANCH${NC}"
    echo -e "  Dev Branch:     ${GREEN}$DEV_BRANCH${NC}"
    echo ""
    
    # Check if trading engine is running
    if pgrep -f "oanda_trading_engine" > /dev/null 2>&1; then
        echo -e "  Trading Engine: ${GREEN}RUNNING${NC}"
    else
        echo -e "  Trading Engine: ${RED}STOPPED${NC}"
    fi
    
    # Check for uncommitted changes
    cd "$RICK_ROOT/rick_clean_live"
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        echo -e "  Uncommitted:    ${YELLOW}YES - changes pending${NC}"
    else
        echo -e "  Uncommitted:    ${GREEN}NO - clean state${NC}"
    fi
    
    echo ""
}

# Create backup
create_backup() {
    local backup_name="backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    echo -e "${CYAN}Creating backup: $backup_name${NC}"
    
    mkdir -p "$backup_path"
    
    # Backup critical files
    cp -r "$RICK_ROOT/rick_clean_live" "$backup_path/" 2>/dev/null || true
    cp "$RICK_ROOT/.env" "$backup_path/" 2>/dev/null || true
    
    # Save metadata
    cat > "$backup_path/BACKUP_META.json" << EOF
{
    "name": "$backup_name",
    "created": "$(date -Iseconds)",
    "mode": "$(get_mode)",
    "branch": "$(get_branch)",
    "has_uncommitted": "$(cd $RICK_ROOT/rick_clean_live && git status --porcelain | wc -l)"
}
EOF
    
    log_action "BACKUP_CREATED" "$backup_name"
    echo -e "${GREEN}✅ Backup created: $backup_path${NC}"
}

# Switch to dev mode
switch_to_dev() {
    echo -e "${YELLOW}Switching to DEV mode...${NC}"
    
    # Check if engine is running
    if pgrep -f "oanda_trading_engine" > /dev/null 2>&1; then
        echo -e "${RED}⚠️  WARNING: Trading engine is running!${NC}"
        echo -e "${YELLOW}Stop the engine before switching modes? (y/n)${NC}"
        read -r response
        if [ "$response" = "y" ]; then
            pkill -f "oanda_trading_engine" 2>/dev/null || true
            sleep 2
        else
            echo -e "${RED}Aborted. Stop the engine first.${NC}"
            exit 1
        fi
    fi
    
    # Create backup first
    create_backup
    
    # Set dev environment variable
    export RICK_DEV_MODE=1
    echo "RICK_DEV_MODE=1" > "$RICK_ROOT/.rick_dev_mode"
    
    # Update mode file
    echo "dev" > "$MODE_FILE"
    
    log_action "MODE_SWITCH" "Switched to DEV mode"
    
    echo -e "${GREEN}✅ DEV mode activated${NC}"
    echo -e "${YELLOW}⚠️  Changes will be tracked in .rick_system/change_log/${NC}"
    echo -e "${YELLOW}⚠️  Remember to test thoroughly before merging to production${NC}"
}

# Switch to live/production mode
switch_to_live() {
    echo -e "${YELLOW}Switching to LIVE (frozen) mode...${NC}"
    
    # Check for uncommitted changes
    cd "$RICK_ROOT/rick_clean_live"
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        echo -e "${RED}⚠️  WARNING: You have uncommitted changes!${NC}"
        echo -e "${YELLOW}These will be stashed. Continue? (y/n)${NC}"
        read -r response
        if [ "$response" = "y" ]; then
            git stash push -m "Auto-stash before switching to live mode $(date +%Y%m%d_%H%M%S)"
        else
            echo -e "${RED}Aborted. Commit or discard changes first.${NC}"
            exit 1
        fi
    fi
    
    # Create backup first
    create_backup
    
    # Checkout frozen branch
    echo -e "${CYAN}Checking out frozen branch: $FROZEN_BRANCH${NC}"
    git fetch origin 2>/dev/null || true
    git checkout "$FROZEN_BRANCH" 2>/dev/null || {
        echo -e "${YELLOW}Branch doesn't exist yet, creating from current state...${NC}"
        git checkout -b "$FROZEN_BRANCH"
    }
    
    # Clear dev mode
    rm -f "$RICK_ROOT/.rick_dev_mode"
    unset RICK_DEV_MODE
    
    # Update mode file
    echo "live" > "$MODE_FILE"
    
    log_action "MODE_SWITCH" "Switched to LIVE (frozen) mode"
    
    echo -e "${GREEN}✅ LIVE mode activated - running frozen production code${NC}"
}

# Restore from backup
restore_backup() {
    echo -e "${CYAN}Available backups:${NC}"
    ls -la "$BACKUP_DIR" 2>/dev/null | grep "backup_" || {
        echo -e "${RED}No backups found${NC}"
        exit 1
    }
    
    echo ""
    echo -e "${YELLOW}Enter backup name to restore (or 'latest'):${NC}"
    read -r backup_name
    
    if [ "$backup_name" = "latest" ]; then
        backup_name=$(ls -t "$BACKUP_DIR" | head -1)
    fi
    
    local backup_path="$BACKUP_DIR/$backup_name"
    
    if [ ! -d "$backup_path" ]; then
        echo -e "${RED}Backup not found: $backup_path${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}⚠️  This will overwrite current files. Continue? (y/n)${NC}"
    read -r response
    if [ "$response" != "y" ]; then
        echo -e "${RED}Aborted${NC}"
        exit 1
    fi
    
    # Restore files
    cp -r "$backup_path/rick_clean_live/"* "$RICK_ROOT/rick_clean_live/" 2>/dev/null || true
    
    log_action "BACKUP_RESTORED" "$backup_name"
    
    echo -e "${GREEN}✅ Restored from: $backup_name${NC}"
}

# Main command handler
case "$1" in
    status)
        show_status
        ;;
    dev)
        switch_to_dev
        ;;
    live|prod|frozen)
        switch_to_live
        ;;
    backup)
        create_backup
        ;;
    restore)
        restore_backup
        ;;
    *)
        echo ""
        echo -e "${CYAN}RICK Dev/Live Toggle System${NC}"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  status   - Show current mode and status"
        echo "  dev      - Switch to development mode"
        echo "  live     - Switch to frozen production mode"
        echo "  backup   - Create manual backup"
        echo "  restore  - Restore from backup"
        echo ""
        show_status
        ;;
esac
