#!/usr/bin/env fish

# AutoFinance MCP Server Launcher
# Starts all essential MCP servers in background

set BASE_DIR ~/Documents/AutoFinance
set VENV_PYTHON $BASE_DIR/venv/bin/python

echo "🚀 Starting AutoFinance MCP Servers..."

# Start essential servers
echo "Starting market server..."
$VENV_PYTHON $BASE_DIR/mcp-servers/market/server_real.py &
set MARKET_PID $last_pid
echo "  ✓ Market server (PID: $MARKET_PID)"

echo "Starting risk server..."
$VENV_PYTHON $BASE_DIR/mcp-servers/risk/server.py &
set RISK_PID $last_pid
echo "  ✓ Risk server (PID: $RISK_PID)"

echo "Starting execution server..."
$VENV_PYTHON $BASE_DIR/mcp-servers/execution/server.py &
set EXEC_PID $last_pid
echo "  ✓ Execution server (PID: $EXEC_PID)"

echo "Starting compliance server..."
$VENV_PYTHON $BASE_DIR/mcp-servers/compliance/server.py &
set COMP_PID $last_pid
echo "  ✓ Compliance server (PID: $COMP_PID)"

echo "Starting technical server..."
$VENV_PYTHON $BASE_DIR/mcp-servers/technical/server.py &
set TECH_PID $last_pid
echo "  ✓ Technical server (PID: $TECH_PID)"

echo ""
echo "✅ All servers started!"
echo ""
echo "PIDs: $MARKET_PID $RISK_PID $EXEC_PID $COMP_PID $TECH_PID"
echo ""
echo "To stop all servers:"
echo "  kill $MARKET_PID $RISK_PID $EXEC_PID $COMP_PID $TECH_PID"
echo ""
echo "Servers are running. Configure them in Archestra using 'Remote' tab."
