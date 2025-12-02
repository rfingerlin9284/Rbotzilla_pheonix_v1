#!/bin/bash
# Enforce charter and gated logic immutability
# PIN: 841921

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to display usage
function show_usage {
    echo -e "${BLUE}RICK Trading System - Charter Immutability Enforcement${NC}"
    echo ""
    echo -e "Usage: $0 [PIN] [OPTIONS]"
    echo ""
    echo -e "Arguments:"
    echo -e "  PIN        - Charter PIN for authentication (required for full enforcement)"
    echo ""
    echo -e "Options:"
    echo -e "  --verify-only     - Only verify files without making changes"
    echo -e "  --auto-restore    - Automatically restore modified critical files"
    echo -e "  --restore PATH    - Restore a specific file from backup"
    echo -e "  --list-backups    - List all available backups"
    echo -e "  --help, -h        - Show this help message"
    echo ""
    echo -e "This script enforces immutability of critical charter and gated logic files."
    echo -e "It creates checksums, backups, and makes the files read-only to prevent modifications."
    echo ""
    echo -e "Examples:"
    echo -e "  $0 841921                      - Full enforcement with PIN"
    echo -e "  $0 841921 --auto-restore       - Enforce and auto-restore modified files"
    echo -e "  $0 --verify-only               - Verify without making changes (no PIN needed)"
    echo -e "  $0 841921 --restore foundation/rick_charter.py - Restore specific file"
    echo ""
}

# Check if help was requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_usage
    exit 0
fi

# Create logs directory if it doesn't exist
mkdir -p logs
mkdir -p charter_backups

echo -e "${BLUE}=== RICK Charter Immutability Enforcement ===${NC}"
echo ""

# Handle --list-backups (doesn't require PIN)
if [[ "$1" == "--list-backups" ]]; then
    echo -e "${CYAN}Listing available backups...${NC}"
    echo ""
    python3 scripts/enforce_immutability.py --list-backups
    exit $?
fi

# Handle --verify-only (doesn't require PIN)
if [[ "$1" == "--verify-only" ]]; then
    echo -e "${YELLOW}Running in verification-only mode...${NC}"
    echo ""
    python3 scripts/enforce_immutability.py --verify-only
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Charter verification completed successfully${NC}"
        echo -e "${GREEN}✅ All critical files are verified${NC}"
    else
        echo ""
        echo -e "${RED}❌ Charter verification failed${NC}"
        echo -e "${RED}❌ Some critical files may have been modified or are missing${NC}"
        echo -e "${YELLOW}Check logs/immutability_enforcer.log for details${NC}"
    fi
    
    exit $exit_code
fi

# Check if PIN was provided for other operations
if [[ "$1" =~ ^[0-9]+$ ]]; then
    PIN="$1"
    shift
else
    echo -e "${YELLOW}Warning: No PIN provided. Running in verification-only mode.${NC}"
    echo -e "${YELLOW}For full enforcement, provide the Charter PIN.${NC}"
    echo ""
    python3 scripts/enforce_immutability.py --verify-only
    
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Charter verification completed successfully${NC}"
        echo -e "${GREEN}✅ All critical files are verified${NC}"
    else
        echo ""
        echo -e "${RED}❌ Charter verification failed${NC}"
        echo -e "${RED}❌ Some critical files may have been modified or are missing${NC}"
        echo -e "${YELLOW}Check logs/immutability_enforcer.log for details${NC}"
    fi
    
    exit $exit_code
fi

# Handle --restore
if [[ "$1" == "--restore" && -n "$2" ]]; then
    FILE_PATH="$2"
    echo -e "${CYAN}Attempting to restore ${FILE_PATH}...${NC}"
    echo ""
    python3 scripts/enforce_immutability.py "$PIN" --restore "$FILE_PATH"
    
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ File restored successfully${NC}"
    else
        echo -e "${RED}❌ Failed to restore file${NC}"
        echo -e "${YELLOW}Check logs/immutability_enforcer.log for details${NC}"
    fi
    
    exit $exit_code
fi

# Handle --auto-restore
if [[ "$1" == "--auto-restore" ]]; then
    echo -e "${BLUE}Enforcing charter immutability with auto-restore...${NC}"
    echo ""
    python3 scripts/enforce_immutability.py "$PIN" --auto-restore
    
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Charter immutability enforcement completed successfully${NC}"
        echo -e "${GREEN}✅ All critical files are protected and verified${NC}"
    else
        echo ""
        echo -e "${RED}❌ Charter immutability enforcement failed${NC}"
        echo -e "${RED}❌ Some critical files may have been modified or are missing${NC}"
        echo -e "${YELLOW}Check logs/immutability_enforcer.log for details${NC}"
    fi
    
    exit $exit_code
fi

# Default: full enforcement with PIN
echo -e "${BLUE}Enforcing charter immutability with PIN authentication...${NC}"
echo ""
python3 scripts/enforce_immutability.py "$PIN"

# Check exit code
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Charter immutability enforcement completed successfully${NC}"
    echo -e "${GREEN}✅ All critical files are protected and verified${NC}"
else
    echo ""
    echo -e "${RED}❌ Charter immutability enforcement failed${NC}"
    echo -e "${RED}❌ Some critical files may have been modified or are missing${NC}"
    echo -e "${YELLOW}Check logs/immutability_enforcer.log for details${NC}"
fi

exit $exit_code