#!/usr/bin/env fish

# Simple solution: Use the stdio servers but provide URL config for Archestra
# This creates a JSON config file that Archestra can import

set BASE_DIR ~/Documents/AutoFinance

echo "📝 Creating Archestra MCP Server Configuration..."

cat > $BASE_DIR/archestra-servers.json << 'EOF'
{
  "mcpServers": {
    "autofinance-market": {
      "command": "/home/cryptosaiyan/Documents/AutoFinance/venv/bin/python",
      "args": ["/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/market/server_real.py"],
      "env": {}
    },
    "autofinance-risk": {
      "command": "/home/cryptosaiyan/Documents/AutoFinance/venv/bin/python",
      "args": ["/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/risk/server.py"],
      "env": {}
    },
    "autofinance-execution": {
      "command": "/home/cryptosaiyan/Documents/AutoFinance/venv/bin/python",
      "args": ["/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/execution/server.py"],
      "env": {}
    },
    "autofinance-compliance": {
      "command": "/home/cryptosaiyan/Documents/AutoFinance/venv/bin/python",
      "args": ["/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/compliance/server.py"],
      "env": {}
    },
    "autofinance-technical": {
      "command": "/home/cryptosaiyan/Documents/AutoFinance/venv/bin/python",
      "args": ["/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/technical/server.py"],
      "env": {}
    }
  }
}
EOF

echo "✅ Configuration created: $BASE_DIR/archestra-servers.json"
echo ""
echo "📋 To use in Archestra:"
echo "1. In Archestra UI, look for 'Import Configuration' or 'Batch Add Servers'"
echo "2. Upload archestra-servers.json"
echo ""
echo "📝 Or add manually in 'Remote' tab with these details:"
echo ""
echo "=== Market Server ==="
echo "Command: /home/cryptosaiyan/Documents/AutoFinance/venv/bin/python"
echo "Arguments: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/market/server_real.py"
echo ""
echo "=== Risk Server ==="
echo "Command: /home/cryptosaiyan/Documents/AutoFinance/venv/bin/python"
echo "Arguments: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/risk/server.py"
echo ""
echo "(Repeat pattern for other servers)"
