#!/bin/bash
# ==============================================================================
# SAFE EXFILTRATION - RICK_PHOENIX CLEANUP
# AUTH CODE: 841921
# ==============================================================================
# This is the SAFE version that handles the LARGE folders properly
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

DESKTOP_PATH="/mnt/c/Users/RFing/OneDrive/Desktop"
RICK_ROOT="/home/ing/RICK"
PHOENIX_ROOT="/home/ing/RICK/RICK_PHOENIX"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}   RICK PHOENIX - SAFE EXFILTRATION OPERATION         ${NC}"
echo -e "${GREEN}======================================================${NC}"
echo ""
echo -e "${CYAN}Current folder sizes:${NC}"
cd "$RICK_ROOT"
du -sh */ 2>/dev/null | sort -hr | head -10
echo ""

echo -e "${YELLOW}⚠️  WARNING: Some folders are VERY LARGE!${NC}"
echo ""
echo "This script will compress and move the following to your Windows Desktop:"
echo "  1. Dev_unibot_v001 (39GB) → Dev_unibot_v001_$TIMESTAMP.tar.gz"
echo "  2. R_H_UNI (30GB) → R_H_UNI_$TIMESTAMP.tar.gz"  
echo "  3. R_H_UNI_BLOAT_ARCHIVE (74GB) → R_H_UNI_BLOAT_ARCHIVE_$TIMESTAMP.tar.gz"
echo ""
echo -e "${RED}NOTE: RICK_LIVE_PROTOTYPE (250GB) is NOT included - too large.${NC}"
echo ""
read -p "Do you want to proceed? Type 'YES' to continue: " CONFIRM

if [ "$CONFIRM" != "YES" ]; then
    echo "Aborted by user."
    exit 0
fi

# Function to safely compress and move
safe_compress_move() {
    local FOLDER="$1"
    local SOURCE="$RICK_ROOT/$FOLDER"
    local ARCHIVE="${FOLDER}_${TIMESTAMP}.tar.gz"
    
    if [ ! -d "$SOURCE" ]; then
        echo -e "${YELLOW}⚠️ $FOLDER not found, skipping${NC}"
        return
    fi
    
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Processing: $FOLDER${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    
    cd "$RICK_ROOT"
    
    # Remove any existing partial archive
    [ -f "$ARCHIVE" ] && rm -f "$ARCHIVE"
    
    echo "Compressing $FOLDER... (this will take a while)"
    echo "Started at: $(date)"
    
    # Use nice and ionice to reduce system impact
    nice -n 19 ionice -c2 -n7 tar -czf "$ARCHIVE" "$FOLDER"
    
    if [ $? -eq 0 ]; then
        SIZE=$(du -h "$ARCHIVE" | cut -f1)
        echo -e "${GREEN}✓ Compressed successfully${NC} - Archive size: $SIZE"
        echo "Finished at: $(date)"
        
        echo "Moving archive to Windows Desktop..."
        mv "$ARCHIVE" "$DESKTOP_PATH/"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Archive moved to Desktop${NC}"
            
            echo -e "${RED}Deleting original folder: $FOLDER${NC}"
            rm -rf "$SOURCE"
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ Original folder deleted${NC}"
            else
                echo -e "${RED}✗ Failed to delete original - manual cleanup needed${NC}"
            fi
        else
            echo -e "${RED}✗ Failed to move archive${NC}"
        fi
    else
        echo -e "${RED}✗ Compression failed${NC}"
    fi
}

# Process the three folders requested
safe_compress_move "Dev_unibot_v001"
safe_compress_move "R_H_UNI"
safe_compress_move "R_H_UNI_BLOAT_ARCHIVE"

echo ""
echo -e "${YELLOW}Phase 2: Clean legacy folders inside RICK_PHOENIX${NC}"
echo "------------------------------------------------------"

cd "$PHOENIX_ROOT"

for LEGACY in "rick_clean_live" "rick_clean_live-copilot-restore-repo-and-clean-errors"; do
    if [ -d "$LEGACY" ]; then
        echo "Compressing: $LEGACY"
        ARCHIVE="non_used_${LEGACY}_${TIMESTAMP}.tar.gz"
        tar -czf "$ARCHIVE" "$LEGACY"
        mv "$ARCHIVE" "$DESKTOP_PATH/"
        rm -rf "$LEGACY"
        echo -e "${GREEN}✓ $LEGACY cleaned${NC}"
    fi
done

# Clean up old archives and symlinks in RICK root
cd "$RICK_ROOT"
[ -f "Dev_unibot_v001.tar.gz" ] && rm -f "Dev_unibot_v001.tar.gz" && echo "Removed old partial archive"
[ -L "current" ] && rm -f "current" && echo "Removed dangling symlink"

echo ""
echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}   FINAL STATUS                                       ${NC}"
echo -e "${GREEN}======================================================${NC}"
echo ""
echo "Remaining in /home/ing/RICK:"
ls -la "$RICK_ROOT" | grep "^d" | grep -v "^\."
echo ""
echo "Archives on Desktop:"
ls -lh "$DESKTOP_PATH"/*.tar.gz 2>/dev/null | tail -10
echo ""
echo -e "${GREEN}✅ OPERATION COMPLETE${NC}"
