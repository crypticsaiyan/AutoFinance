#!/usr/bin/env fish

# Start all MCP servers with HTTP/SSE transport

set PYTHON ~/Documents/AutoFinance/venv/bin/python
set SCRIPT ~/Documents/AutoFinance/mcp_sse_server.py

echo "🚀 Starting AutoFinance MCP Servers (HTTP/SSE)"
echo "=============================================="
echo ""

# Start each server in background
for server in market risk execution compliance technical fundamental macro news portfolio-analytics volatility simulation-engine notification-gateway
    echo "  Starting $server..."
    $PYTHON $SCRIPT $server &
    sleep 1
end

echo ""
echo "✅ All servers started!"
echo ""
echo "📋 Archestra URLs:"
echo "   market:                http://localhost:9001/mcp"
echo "   risk:                  http://localhost:9002/mcp"
echo "   execution:             http://localhost:9003/mcp"
echo "   compliance:            http://localhost:9004/mcp"
echo "   technical:             http://localhost:9005/mcp"
echo "   fundamental:           http://localhost:9006/mcp"
echo "   macro:                 http://localhost:9007/mcp"
echo "   news:                  http://localhost:9008/mcp"
echo "   portfolio-analytics:   http://localhost:9009/mcp"
echo "   volatility:            http://localhost:9010/mcp"
echo "   simulation-engine:     http://localhost:9012/mcp"
echo "   notification-gateway:  http://localhost:9013/mcp  (includes alerts)"
echo ""
echo "🔗 Docker URLs (for Archestra):"
echo "   Use: http://172.17.0.1:900X/mcp"
echo ""
echo "🛑 To stop all servers: pkill -f mcp_sse_server.py"
