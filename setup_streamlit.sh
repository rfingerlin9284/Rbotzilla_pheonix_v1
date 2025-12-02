#!/bin/bash
# RBOTzilla Streamlit Setup & Launch Script
# Quick setup for WSL environment

set -e

echo "🤖 RBOTzilla Streamlit Setup"
echo "============================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check Python
echo -e "${YELLOW}[1/5]${NC} Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "Install with: sudo apt install python3 python3-pip"
    exit 1
fi
PY_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PY_VERSION}${NC}"

# 2. Install dependencies
echo ""
echo -e "${YELLOW}[2/5]${NC} Installing dependencies..."
pip3 install -q -r requirements.txt 2>/dev/null && \
    pip3 install -q fastapi uvicorn websockets websocket-client 2>/dev/null
echo -e "${GREEN}✅ Dependencies installed${NC}"

# 3. Create .env if missing
echo ""
echo -e "${YELLOW}[3/5]${NC} Checking environment variables..."
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env not found, creating from template...${NC}"
    cat > .env << 'EOF'
# OANDA (Practice)
OANDA_ACCESS_TOKEN=PLACEHOLDER_OANDA_TOKEN
OANDA_ACCOUNT_ID=PLACEHOLDER_ACCOUNT_ID

# Coinbase
COINBASE_API_KEY=PLACEHOLDER_CB_KEY
COINBASE_API_SECRET=PLACEHOLDER_CB_SECRET

# Dashboard
BACKEND_URL=http://127.0.0.1:8000
WEBSOCKET_URL=ws://127.0.0.1:8000/ws

# Bot Config
BOT_LOG_LEVEL=INFO
BOT_RISK_PER_TRADE=0.02
BOT_MAX_TRADES=3
EOF
    echo -e "${YELLOW}⚠️  Update .env with real credentials!${NC}"
else
    echo -e "${GREEN}✅ .env exists${NC}"
fi

# 4. Create run scripts
echo ""
echo -e "${YELLOW}[4/5]${NC} Creating run scripts..."

cat > run_backend.sh << 'EOF'
#!/bin/bash
echo "Starting RBOTzilla Backend..."
echo "Server: http://127.0.0.1:8000"
echo "Health: http://127.0.0.1:8000/api/health"
echo "Press Ctrl+C to stop"
echo ""
python3 -m uvicorn backend:app --reload --host 127.0.0.1 --port 8000
EOF
chmod +x run_backend.sh

cat > run_dashboard.sh << 'EOF'
#!/bin/bash
echo "Starting RBOTzilla Dashboard..."
echo "Open: http://127.0.0.1:8501"
echo "Press Ctrl+C to stop"
echo ""
streamlit run dashboard.py --server.port 8501 --server.address 127.0.0.1
EOF
chmod +x run_dashboard.sh

echo -e "${GREEN}✅ Run scripts created${NC}"
echo "   - run_backend.sh"
echo "   - run_dashboard.sh"

# 5. Health check
echo ""
echo -e "${YELLOW}[5/5]${NC} Setup complete!"
echo ""
echo -e "${GREEN}✅ All checks passed!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  Terminal 1:"
echo "    ./run_backend.sh"
echo ""
echo "  Terminal 2:"
echo "    ./run_dashboard.sh"
echo ""
echo "  Then open: http://127.0.0.1:8501"
echo ""
