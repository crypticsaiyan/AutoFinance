#!/usr/bin/env fish

# AutoFinance MCP Servers - HTTP/SSE Mode
# Run servers on different ports for remote URL access

set BASE_DIR ~/Documents/AutoFinance
set VENV_PYTHON $BASE_DIR/venv/bin/python

echo "🌐 Starting AutoFinance MCP Servers (HTTP/SSE Mode)..."
echo ""

# Port assignments
set MARKET_PORT 8001
set RISK_PORT 8002
set EXECUTION_PORT 8003
set COMPLIANCE_PORT 8004
set TECHNICAL_PORT 8005

echo "Starting servers on localhost..."
echo ""

# Market Server
echo "📊 Market Server: http://127.0.0.1:$MARKET_PORT"
$VENV_PYTHON $BASE_DIR/mcp-servers/market/server_http.py &
set MARKET_PID $last_pid

# Wait a bit between starts
sleep 1

# Add more servers here as needed
# $VENV_PYTHON $BASE_DIR/mcp-servers/risk/server_http.py &
# set RISK_PID $last_pid

echo ""
echo "✅ Servers started!"
echo ""
echo "URLs for Archestra 'Remote' configuration:"
echo "  Market:     http://127.0.0.1:$MARKET_PORT"
echo "  Risk:       http://127.0.0.1:$RISK_PORT (not started)"
echo "  Execution:  http://127.0.0.1:$EXECUTION_PORT (not started)"
echo "  Compliance: http://127.0.0.1:$COMPLIANCE_PORT (not started)"
echo "  Technical:  http://127.0.0.1:$TECHNICAL_PORT (not started)"
echo ""
echo "Active PIDs: $MARKET_PID"
echo ""
echo "To stop all servers:"
echo "  kill $MARKET_PID"
echo ""
echo "Test market server:"
echo "  curl http://127.0.0.1:$MARKET_PORT"
