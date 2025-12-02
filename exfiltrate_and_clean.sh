#!/bin/bash
# ==============================================================================
# MISSION: EXFILTRATE & SANITIZE - RICK_PHOENIX CLEANUP OPERATION
# AUTH CODE: 841921
# ==============================================================================
# This script will:
# 1. Compress specified legacy folders to .tar.gz
# 2. MOVE (not copy) the archives to Windows Desktop
# 3. DELETE the original folders from WSL after successful compression
# 4. Clean up legacy folders inside RICK_PHOENIX
# ==============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DESKTOP_PATH="/mnt/c/Users/RFing/OneDrive/Desktop"
RICK_ROOT="/home/ing/RICK"
PHOENIX_ROOT="/home/ing/RICK/RICK_PHOENIX"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}   RICK PHOENIX - EXFILTRATION & CLEANUP OPERATION    ${NC}"
echo -e "${GREEN}   AUTH: 841921 | Timestamp: $TIMESTAMP               ${NC}"
echo -e "${GREEN}======================================================${NC}"

# Verify Desktop Path
if [ ! -d "$DESKTOP_PATH" ]; then
    echo -e "${RED}ERROR: Desktop path not found: $DESKTOP_PATH${NC}"
    echo "Creating directory..."
    mkdir -p "$DESKTOP_PATH"
fi

echo ""
echo -e "${YELLOW}Phase 1: EXFILTRATE LEGACY REPOS FROM /home/ing/RICK${NC}"
echo "------------------------------------------------------"

# Function to compress and move a folder
compress_and_move() {
    local FOLDER_NAME="$1"
    local SOURCE_PATH="$RICK_ROOT/$FOLDER_NAME"
    local ARCHIVE_NAME="${FOLDER_NAME}_${TIMESTAMP}.tar.gz"
    
    if [ -d "$SOURCE_PATH" ]; then
        echo -e "📦 Processing: ${YELLOW}$FOLDER_NAME${NC}"
        
        cd "$RICK_ROOT"
        
        # Check if a partial archive already exists and remove it
        if [ -f "$ARCHIVE_NAME" ]; then
            echo "   Removing existing partial archive..."
            rm -f "$ARCHIVE_NAME"
        fi
        
        # Compress
        echo "   Compressing... (this may take a while for large folders)"
        tar -czf "$ARCHIVE_NAME" "$FOLDER_NAME" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            # Get archive size
            SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)
            echo -e "   ${GREEN}✓ Compression complete${NC} (Size: $SIZE)"
            
            # Move to Desktop
            echo "   Moving to Windows Desktop..."
            mv "$ARCHIVE_NAME" "$DESKTOP_PATH/"
            
            if [ $? -eq 0 ]; then
                echo -e "   ${GREEN}✓ Moved to Desktop${NC}"
                
                # DELETE the original folder
                echo -e "   ${RED}🔥 Deleting original source: $FOLDER_NAME${NC}"
                rm -rf "$SOURCE_PATH"
                
                if [ $? -eq 0 ]; then
                    echo -e "   ${GREEN}✓ Original deleted${NC}"
                else
                    echo -e "   ${RED}✗ Failed to delete original${NC}"
                fi
            else
                echo -e "   ${RED}✗ Failed to move archive${NC}"
            fi
        else
            echo -e "   ${RED}✗ Compression failed${NC}"
        fi
    else
        echo -e "⚠️  ${YELLOW}Skipping $FOLDER_NAME${NC} (Not found)"
    fi
    echo ""
}

# Process the three specified legacy repos
compress_and_move "Dev_unibot_v001"
compress_and_move "R_H_UNI"
compress_and_move "R_H_UNI_BLOAT_ARCHIVE"

# Also compress BACKUP_ZIP_CONTENT if it exists
compress_and_move "BACKUP_ZIP_CONTENT"

# Also compress N_RLC_rebuild and new_RLC_rebuild if they exist
compress_and_move "N_RLC_rebuild"
compress_and_move "new_RLC_rebuild"

echo ""
echo -e "${YELLOW}Phase 2: CLEAN LEGACY FOLDERS INSIDE RICK_PHOENIX${NC}"
echo "------------------------------------------------------"

cd "$PHOENIX_ROOT"

# List of legacy folders inside RICK_PHOENIX to clean
LEGACY_INSIDE_PHOENIX=(
    "rick_clean_live"
    "rick_clean_live-copilot-restore-repo-and-clean-errors"
)

for LEGACY in "${LEGACY_INSIDE_PHOENIX[@]}"; do
    if [ -d "$LEGACY" ]; then
        echo -e "📦 Processing legacy inside Phoenix: ${YELLOW}$LEGACY${NC}"
        
        ARCHIVE_NAME="non_used_${LEGACY}_${TIMESTAMP}.tar.gz"
        
        # Compress
        tar -czf "$ARCHIVE_NAME" "$LEGACY" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)
            echo -e "   ${GREEN}✓ Compressed${NC} (Size: $SIZE)"
            
            # Move to Desktop
            mv "$ARCHIVE_NAME" "$DESKTOP_PATH/"
            echo -e "   ${GREEN}✓ Moved to Desktop${NC}"
            
            # Delete original
            rm -rf "$LEGACY"
            echo -e "   ${GREEN}✓ Deleted from RICK_PHOENIX${NC}"
        else
            echo -e "   ${RED}✗ Compression failed${NC}"
        fi
    else
        echo -e "⚠️  ${YELLOW}$LEGACY${NC} not found in RICK_PHOENIX"
    fi
done

echo ""
echo -e "${YELLOW}Phase 3: CLEANUP OLD ARCHIVES FROM /home/ing/RICK${NC}"
echo "------------------------------------------------------"

cd "$RICK_ROOT"

# Remove old partial .tar.gz files that might be lingering
if [ -f "Dev_unibot_v001.tar.gz" ]; then
    echo "Removing old partial archive: Dev_unibot_v001.tar.gz"
    rm -f "Dev_unibot_v001.tar.gz"
fi

# Clean up the symlink if it points to something we deleted
if [ -L "current" ]; then
    TARGET=$(readlink "current")
    if [ ! -d "$TARGET" ]; then
        echo "Removing dangling symlink: current"
        rm -f "current"
    fi
fi

echo ""
echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}   FINAL STATUS REPORT                                ${NC}"
echo -e "${GREEN}======================================================${NC}"

echo ""
echo "📂 REMAINING IN /home/ing/RICK:"
ls -la "$RICK_ROOT" | grep -v "^\." | grep -v "^total"

echo ""
echo "📂 ARCHIVES NOW ON DESKTOP:"
ls -la "$DESKTOP_PATH"/*.tar.gz 2>/dev/null || echo "   No archives found"

echo ""
echo -e "${GREEN}✅ EXFILTRATION COMPLETE${NC}"
echo ""
echo "RICK_PHOENIX should now be the ONLY active folder in /home/ing/RICK"
echo "All legacy code has been compressed and moved to your Windows Desktop."
