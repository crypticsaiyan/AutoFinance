#!/usr/bin/env fish

# AutoFinance CLI - Launcher Script

# Colors
set -l cyan (set_color cyan)
set -l green (set_color green)
set -l yellow (set_color yellow)
set -l red (set_color red)
set -l reset (set_color normal)

echo "$cyan"
echo "╔══════════════════════════════════════╗"
echo "║      AutoFinance CLI Launcher        ║"
echo "╚══════════════════════════════════════╝"
echo "$reset"

# Check if virtual environment exists
if not test -d venv
    echo "$red❌ Virtual environment not found!$reset"
    echo ""
    echo "Run the installer first:"
    echo "  ./install.fish"
    exit 1
end

# Activate virtual environment
source venv/bin/activate.fish
echo "$green✓ Virtual environment activated$reset"

# Check if MCP servers are running
set server_count (ps aux | grep "mcp_sse_server.py" | grep -v grep | wc -l)

if test $server_count -lt 5
    echo "$yellow⚠️  Warning: MCP servers may not be running$reset"
    echo "   Expected: 13 servers, Found: $server_count"
    echo ""
    echo "   Start servers with: cd .. && ./start_sse_servers.fish"
    echo ""
    read -P "Continue anyway? [y/N] " -l response
    if test "$response" != "y" -a "$response" != "Y"
        exit 0
    end
else
    echo "$green✓ MCP servers: $server_count active$reset"
end

echo ""
echo "🚀 Launching AutoFinance Dashboard..."
echo ""

# Run the new Textual-based CLI (high performance)
python dashboard_new.py

echo ""
echo "Thanks for using AutoFinance! 👋"
