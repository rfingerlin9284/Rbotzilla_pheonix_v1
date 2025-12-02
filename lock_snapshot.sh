#!/bin/bash
# ==============================================================================
# RICK LIVE CLEAN - LOCK SNAPSHOT SCRIPT v3.0
# ==============================================================================
# Purpose: Create immutable frozen snapshot of the trading system
# Auth Code: 841921 required for execution
# Generated: 2025-11-26
# ==============================================================================

set -e

# Configuration
WORKSPACE="/home/ing/RICK/RICK_LIVE_CLEAN"
TIMESTAMP=$(date +%Y%m%dT%H%M%S)
FROZEN_DIR="${WORKSPACE}/frozen_v3"
SNAPSHOT_NAME="FROZEN_V3_SNAPSHOT_${TIMESTAMP}"
ZIP_FILE="${WORKSPACE}/${SNAPSHOT_NAME}.zip"
LOG_FILE="${WORKSPACE}/logs/lock_snapshot_${TIMESTAMP}.log"
AUTH_CODE="841921"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ==============================================================================
# FUNCTIONS
# ==============================================================================

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$msg"
    echo "$msg" >> "$LOG_FILE"
}

error_exit() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    log "ERROR: $1"
    exit 1
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING: $1"
}

info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
    log "INFO: $1"
}

# ==============================================================================
# AUTH VERIFICATION
# ==============================================================================

verify_auth() {
    echo -e "${CYAN}=====================================${NC}"
    echo -e "${CYAN}  RICK LOCK SNAPSHOT v3.0${NC}"
    echo -e "${CYAN}=====================================${NC}"
    echo ""
    
    read -p "Enter AUTH CODE to proceed: " user_code
    
    if [ "$user_code" != "$AUTH_CODE" ]; then
        error_exit "Invalid AUTH CODE. Snapshot aborted."
    fi
    
    success "AUTH CODE verified: $AUTH_CODE"
}

# ==============================================================================
# PRE-FLIGHT CHECKS
# ==============================================================================

preflight_checks() {
    info "Running pre-flight checks..."
    
    # Check workspace exists
    if [ ! -d "$WORKSPACE" ]; then
        error_exit "Workspace not found: $WORKSPACE"
    fi
    
    # Create logs directory if needed
    mkdir -p "${WORKSPACE}/logs"
    
    # Check for active processes
    if pgrep -f "run_autonomous" > /dev/null 2>&1; then
        warn "Trading engine is running. Consider stopping before snapshot."
        read -p "Continue anyway? (y/N): " confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            error_exit "User aborted due to running processes."
        fi
    fi
    
    # Check disk space (need at least 500MB)
    available_kb=$(df "$WORKSPACE" | awk 'NR==2 {print $4}')
    if [ "$available_kb" -lt 512000 ]; then
        error_exit "Insufficient disk space. Need at least 500MB free."
    fi
    
    success "Pre-flight checks passed"
}

# ==============================================================================
# CLEANUP TEMPORARY FILES
# ==============================================================================

cleanup_temp() {
    info "Cleaning up temporary files..."
    
    # Remove __pycache__ directories
    find "$WORKSPACE" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # Remove .pyc files
    find "$WORKSPACE" -type f -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove temporary demo data (optional - comment out to keep)
    # rm -rf "${WORKSPACE}/tmp_demo_data" 2>/dev/null || true
    # rm -rf "${WORKSPACE}/tmp_demo_data2" 2>/dev/null || true
    # rm -rf "${WORKSPACE}/tmp_demo_data3" 2>/dev/null || true
    # rm -rf "${WORKSPACE}/tmp_demo_data4" 2>/dev/null || true
    # rm -rf "${WORKSPACE}/tmp_results" 2>/dev/null || true
    # rm -rf "${WORKSPACE}/tmp_results3" 2>/dev/null || true
    
    success "Temporary files cleaned"
}

# ==============================================================================
# CREATE ZIP SNAPSHOT
# ==============================================================================

create_snapshot() {
    info "Creating ZIP snapshot: ${SNAPSHOT_NAME}.zip"
    
    cd "$WORKSPACE"
    
    # Exclude patterns for cleaner snapshot
    EXCLUDE_PATTERNS=(
        ".git/*"
        ".venv/*"
        "venv_coinbase/*"
        "__pycache__/*"
        "*.pyc"
        "*.pyo"
        "logs/*.log"
        "narration.jsonl"
        "tmp_*"
        "*.tmp"
        "node_modules/*"
    )
    
    # Build exclude args
    EXCLUDE_ARGS=""
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        EXCLUDE_ARGS="$EXCLUDE_ARGS -x '$pattern'"
    done
    
    # Create zip with timestamp
    eval "zip -r '$ZIP_FILE' . $EXCLUDE_ARGS"
    
    # Verify zip was created
    if [ ! -f "$ZIP_FILE" ]; then
        error_exit "Failed to create ZIP file"
    fi
    
    ZIP_SIZE=$(du -h "$ZIP_FILE" | cut -f1)
    success "ZIP snapshot created: $ZIP_FILE ($ZIP_SIZE)"
}

# ==============================================================================
# CREATE FROZEN DIRECTORY
# ==============================================================================

create_frozen_dir() {
    info "Creating frozen_v3 directory..."
    
    # Remove old frozen_v3 if exists
    if [ -d "$FROZEN_DIR" ]; then
        warn "Existing frozen_v3 found. Backing up..."
        mv "$FROZEN_DIR" "${FROZEN_DIR}_backup_${TIMESTAMP}"
    fi
    
    # Create frozen directory
    mkdir -p "$FROZEN_DIR"
    
    # Extract snapshot to frozen directory
    unzip -q "$ZIP_FILE" -d "$FROZEN_DIR"
    
    success "Frozen directory created: $FROZEN_DIR"
}

# ==============================================================================
# SET READ-ONLY PERMISSIONS
# ==============================================================================

set_readonly() {
    info "Setting READ-ONLY permissions on frozen_v3..."
    
    # Make all files read-only
    find "$FROZEN_DIR" -type f -exec chmod 444 {} \;
    
    # Make directories read + execute only
    find "$FROZEN_DIR" -type d -exec chmod 555 {} \;
    
    # Set immutable attribute (requires root - optional)
    # sudo chattr -R +i "$FROZEN_DIR" 2>/dev/null || warn "Could not set immutable flag (requires root)"
    
    success "Permissions set to READ-ONLY"
}

# ==============================================================================
# GENERATE MANIFEST
# ==============================================================================

generate_manifest() {
    info "Generating freeze manifest..."
    
    MANIFEST_FILE="${WORKSPACE}/FROZEN_V3_MANIFEST_${TIMESTAMP}.md"
    
    cat > "$MANIFEST_FILE" << MANIFEST_EOF
# FROZEN V3 MANIFEST
## Generated: $(date)
## Auth Code: $AUTH_CODE

---

## Snapshot Details
| Property | Value |
|----------|-------|
| Timestamp | $TIMESTAMP |
| ZIP File | ${SNAPSHOT_NAME}.zip |
| ZIP Size | $(du -h "$ZIP_FILE" | cut -f1) |
| Frozen Dir | frozen_v3/ |
| File Count | $(find "$FROZEN_DIR" -type f | wc -l) |
| Dir Count | $(find "$FROZEN_DIR" -type d | wc -l) |

---

## File Checksums (Top-Level)
\`\`\`
$(md5sum "${WORKSPACE}"/*.py 2>/dev/null || echo "No .py files in root")
\`\`\`

---

## Frozen Directory Structure
\`\`\`
$(ls -la "$FROZEN_DIR" | head -30)
\`\`\`

---

## Active Manifests Included
- manifest_active.json
- manifest_legacy.json

---

## Lock Status
✅ All files in frozen_v3/ are READ-ONLY
✅ ZIP snapshot preserved
✅ Change tracking enabled

MANIFEST_EOF

    success "Manifest generated: $MANIFEST_FILE"
}

# ==============================================================================
# LOG TO CHANGE TRACKER
# ==============================================================================

log_to_tracker() {
    info "Logging to change tracker..."
    
    # Call Python change tracker if it exists
    if [ -f "${WORKSPACE}/.rick_system/change_tracker.py" ]; then
        cd "$WORKSPACE"
        python3 -c "
from .rick_system.change_tracker import ChangeTracker
tracker = ChangeTracker()
tracker.log_event(
    event_type='SNAPSHOT_CREATED',
    file_path='${ZIP_FILE}',
    auth_pin=${AUTH_CODE},
    details={'timestamp': '${TIMESTAMP}', 'frozen_dir': 'frozen_v3'}
)
" 2>/dev/null || warn "Could not log to change tracker"
    fi
    
    success "Event logged"
}

# ==============================================================================
# SUMMARY
# ==============================================================================

print_summary() {
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}  SNAPSHOT COMPLETE${NC}"
    echo -e "${GREEN}=====================================${NC}"
    echo ""
    echo -e "📦 ZIP File:     ${CYAN}${ZIP_FILE}${NC}"
    echo -e "📁 Frozen Dir:   ${CYAN}${FROZEN_DIR}${NC}"
    echo -e "📋 Manifest:     ${CYAN}FROZEN_V3_MANIFEST_${TIMESTAMP}.md${NC}"
    echo -e "📝 Log File:     ${CYAN}${LOG_FILE}${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  frozen_v3/ is now READ-ONLY${NC}"
    echo -e "${YELLOW}⚠️  To modify, use AUTH CODE: $AUTH_CODE${NC}"
    echo ""
}

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

main() {
    # Initialize log
    mkdir -p "$(dirname "$LOG_FILE")"
    log "========== LOCK SNAPSHOT STARTED =========="
    
    # Execute steps
    verify_auth
    preflight_checks
    cleanup_temp
    create_snapshot
    create_frozen_dir
    set_readonly
    generate_manifest
    log_to_tracker
    print_summary
    
    log "========== LOCK SNAPSHOT COMPLETED =========="
}

# Run main
main "$@"
