#!/bin/bash
# Quick launcher for Advanced Multi-Window Dashboard
# Charter-Compliant Independent Refresh System

DASHBOARD_FILE="/home/ing/RICK/RICK_LIVE_CLEAN/dashboard/advanced_multi_window_dashboard.html"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🤖 RBOTzilla Advanced Multi-Window Dashboard"
echo "  Charter UI Separation Enforced | PIN: 841921"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Opening dashboard with independent refresh controls..."
echo ""
echo "FEATURES:"
echo "  • Page Background: 1 minute refresh (fixed)"
echo "  • Micro Window: 300ms-60s (user-adjustable)"
echo "  • Intraday Window: 5s-5min (user-adjustable)"
echo "  • Independent FOREX/CRYPTO selection per window"
echo ""
echo "⚖️  CHARTER COMPLIANCE:"
echo "  Refresh rates are DISPLAY ONLY"
echo "  Trading logic timing is independent of UI"
echo "  ML/AI nodes control execution, not user preferences"
echo ""
echo "Opening in default browser..."

# Try different browsers
if command -v firefox &> /dev/null; then
    firefox "$DASHBOARD_FILE" &
elif command -v google-chrome &> /dev/null; then
    google-chrome "$DASHBOARD_FILE" &
elif command -v chromium &> /dev/null; then
    chromium "$DASHBOARD_FILE" &
elif command -v xdg-open &> /dev/null; then
    xdg-open "$DASHBOARD_FILE" &
else
    echo "❌ No browser found. Please open manually:"
    echo "   $DASHBOARD_FILE"
    exit 1
fi

echo "✅ Dashboard launched!"
echo ""
echo "To view backend integration, run:"
echo "  python3 dashboard/app.py"
echo "  Then navigate to http://localhost:8080/advanced"
