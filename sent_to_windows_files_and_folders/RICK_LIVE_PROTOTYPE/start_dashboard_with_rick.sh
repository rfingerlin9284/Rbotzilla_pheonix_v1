#!/bin/bash
#
# RICK Dashboard Startup Script
# PIN 841921 Approved | Charter Compliant
#
# Unified launcher for:
# - Ollama LLM service
# - Streamlit web dashboard
# - Headless CLI dashboard
#
# Usage: ./start_dashboard_with_rick.sh [--web|--cli|--both]
#

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv_dashboard"
LOG_DIR="$SCRIPT_DIR/logs"
OLLAMA_MODEL="llama3.1:8b"
STREAMLIT_PORT=8501
HEADLESS_PID_FILE="/tmp/rick_headless_dashboard.pid"

# Ensure logs directory exists
mkdir -p "$LOG_DIR"

# Function to print messages
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Ollama status
check_ollama() {
    info "Checking Ollama service..."
    
    if ! command_exists ollama; then
        error "Ollama not found. Install from https://ollama.ai"
        return 1
    fi
    
    # Check if Ollama is running
    if pgrep -x "ollama" > /dev/null; then
        success "Ollama is already running"
        return 0
    else
        return 1
    fi
}

# Function to start Ollama
start_ollama() {
    if check_ollama; then
        return 0
    fi
    
    info "Starting Ollama service..."
    
    # Start Ollama in background
    ollama serve > "$LOG_DIR/ollama.log" 2>&1 &
    OLLAMA_PID=$!
    
    info "Ollama starting (PID: $OLLAMA_PID)..."
    
    # Wait for Ollama to be ready
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            success "Ollama service is ready"
            
            # Verify model is available
            if curl -s http://localhost:11434/api/tags | grep -q "$OLLAMA_MODEL"; then
                success "Model $OLLAMA_MODEL is available"
            else
                warning "Model $OLLAMA_MODEL not found, pulling..."
                ollama pull "$OLLAMA_MODEL" || warning "Could not pull model"
            fi
            
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 1
    done
    
    error "Ollama failed to start"
    return 1
}

# Function to check Python virtual environment
check_venv() {
    info "Checking Python virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        warning "Virtual environment not found, creating..."
        python3 -m venv "$VENV_DIR"
        success "Virtual environment created"
    fi
    
    # Activate venv and check dependencies
    source "$VENV_DIR/bin/activate"
    
    # Check required packages
    local required_packages=("streamlit" "plotly" "pandas" "requests")
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if ! python -c "import $package" 2>/dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        info "Installing missing packages: ${missing_packages[*]}"
        pip install -q "${missing_packages[@]}"
        success "Dependencies installed"
    else
        success "All dependencies are installed"
    fi
}

# Function to start Streamlit dashboard
start_streamlit() {
    info "Starting Streamlit dashboard..."
    
    source "$VENV_DIR/bin/activate"
    
    # Check which dashboard script to use
    local dashboard_script="$SCRIPT_DIR/dashboard_unified_v2_llm.py"
    
    if [ ! -f "$dashboard_script" ]; then
        dashboard_script="$SCRIPT_DIR/dashboard_unified.py"
    fi
    
    if [ ! -f "$dashboard_script" ]; then
        error "Dashboard script not found"
        return 1
    fi
    
    info "Launching: $dashboard_script"
    info "Access dashboard at: http://localhost:$STREAMLIT_PORT"
    
    streamlit run "$dashboard_script" \
        --logger.level=error \
        --client.showErrorDetails=false \
        --server.port=$STREAMLIT_PORT \
        --server.runOnSave=true
}

# Function to start headless dashboard
start_headless() {
    info "Starting headless CLI dashboard..."
    
    source "$VENV_DIR/bin/activate"
    
    local dashboard_script="$SCRIPT_DIR/dashboard_headless.py"
    
    if [ ! -f "$dashboard_script" ]; then
        error "Headless dashboard script not found"
        return 1
    fi
    
    # Start in background
    python "$dashboard_script" --refresh 2 > "$LOG_DIR/headless.log" 2>&1 &
    local pid=$!
    echo $pid > "$HEADLESS_PID_FILE"
    
    success "Headless dashboard started (PID: $pid)"
    success "View with: tail -f $LOG_DIR/headless.log"
}

# Function to show status
show_status() {
    info "RICK Dashboard Status"
    echo "─────────────────────────────────────────"
    
    # Ollama status
    if pgrep -x "ollama" > /dev/null; then
        echo -e "${GREEN}✓${NC} Ollama service running"
    else
        echo -e "${RED}✗${NC} Ollama service not running"
    fi
    
    # Check for dashboard processes
    if pgrep -f "streamlit run" > /dev/null; then
        local port=$(lsof -t -i:$STREAMLIT_PORT 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✓${NC} Streamlit dashboard running (port $STREAMLIT_PORT)"
    else
        echo -e "${RED}✗${NC} Streamlit dashboard not running"
    fi
    
    if [ -f "$HEADLESS_PID_FILE" ] && pgrep -p "$(cat $HEADLESS_PID_FILE)" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Headless dashboard running (PID: $(cat $HEADLESS_PID_FILE))"
    else
        echo -e "${RED}✗${NC} Headless dashboard not running"
    fi
    
    echo "─────────────────────────────────────────"
}

# Function to stop services
stop_services() {
    info "Stopping RICK services..."
    
    # Stop headless dashboard
    if [ -f "$HEADLESS_PID_FILE" ]; then
        local pid=$(cat "$HEADLESS_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid 2>/dev/null || true
            success "Headless dashboard stopped"
        fi
        rm -f "$HEADLESS_PID_FILE"
    fi
    
    # Streamlit will be stopped via Ctrl+C
    warning "Press Ctrl+C to stop Streamlit dashboard"
}

# Function to show usage
show_usage() {
    cat << EOF
${CYAN}RICK Dashboard Startup Script${NC}
${CYAN}PIN 841921 Approved | Charter Compliant${NC}

${BLUE}Usage:${NC}
    $0 [OPTION]

${BLUE}Options:${NC}
    --web       Start only Streamlit web dashboard
    --cli       Start only headless CLI dashboard  
    --both      Start both dashboards (recommended)
    --status    Show service status
    --stop      Stop all services
    --help      Show this help message

${BLUE}Examples:${NC}
    $0 --web        # Start web dashboard only
    $0 --cli        # Start CLI dashboard only
    $0 --both       # Start web + CLI dashboards (recommended)
    $0 --status     # Check running services

${BLUE}Configuration:${NC}
    Ollama Model: $OLLAMA_MODEL
    Streamlit Port: $STREAMLIT_PORT
    Logs Directory: $LOG_DIR

${BLUE}First Time Setup:${NC}
    1. Ensure Ollama is installed: ollama.ai
    2. Run: $0 --web
    3. Access dashboard at: http://localhost:$STREAMLIT_PORT

EOF
}

# Main script
main() {
    local mode="web"  # default
    
    # Parse arguments
    case "${1:-}" in
        --web)
            mode="web"
            ;;
        --cli)
            mode="cli"
            ;;
        --both)
            mode="both"
            ;;
        --status)
            show_status
            exit 0
            ;;
        --stop)
            stop_services
            exit 0
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            if [ -z "$1" ]; then
                # Default to web if no argument
                mode="web"
            else
                error "Unknown option: $1"
                show_usage
                exit 1
            fi
            ;;
    esac
    
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║      🤖 RICK DASHBOARD STARTUP SYSTEM 🤖             ║${NC}"
    echo -e "${CYAN}║      PIN 841921 Approved | Charter Compliant         ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    info "Starting RICK Dashboard (mode: $mode)"
    echo ""
    
    # Phase 1: Check dependencies
    info "Phase 1: Checking dependencies..."
    if ! command_exists python3; then
        error "Python 3 not found"
        exit 1
    fi
    success "Python 3 found"
    
    # Phase 2: Setup virtual environment
    info "Phase 2: Setting up Python environment..."
    check_venv
    
    # Phase 3: Start Ollama
    info "Phase 3: Starting Ollama LLM service..."
    if start_ollama; then
        success "Ollama LLM service ready"
    else
        warning "Ollama failed to start (LLM features will be limited)"
    fi
    
    echo ""
    
    # Phase 4: Start dashboards based on mode
    case "$mode" in
        web)
            info "Phase 4: Starting Streamlit web dashboard..."
            start_streamlit
            ;;
        cli)
            info "Phase 4: Starting headless CLI dashboard..."
            start_headless
            ;;
        both)
            info "Phase 4a: Starting headless CLI dashboard..."
            start_headless
            echo ""
            info "Phase 4b: Starting Streamlit web dashboard..."
            info "Web dashboard will launch in foreground. Headless runs in background."
            start_streamlit
            ;;
    esac
}

# Run main function
main "$@"
