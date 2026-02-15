#!/usr/bin/env sh

# AutoFinance CLI - Launcher Script

# Colors
cyan='\033[0;36m'
green='\033[0;32m'
yellow='\033[0;33m'
red='\033[0;31m'
reset='\033[0m'

printf "${cyan}"
echo "╔══════════════════════════════════════╗"
echo "║      AutoFinance CLI Launcher        ║"
echo "╚══════════════════════════════════════╝"
printf "${reset}"

# Check if virtual environment exists
if [ ! -d venv ]; then
    printf "${red}❌ Virtual environment not found!${reset}\n"
    echo ""
    echo "Run the installer first:"
    echo "  ./install.sh"
    exit 1
fi

# Activate virtual environment
. venv/bin/activate
printf "${green}✓ Virtual environment activated${reset}\n"

# Check if MCP servers are running
server_count=$(ps aux | grep "mcp_sse_server.py" | grep -v grep | wc -l)

if [ "$server_count" -lt 5 ]; then
    printf "${yellow}⚠️  Warning: MCP servers may not be running${reset}\n"
    echo "   Expected: 13 servers, Found: $server_count"
    echo ""
    echo "   Start servers with: cd .. && ./start_sse_servers.sh"
    echo ""
    printf "Continue anyway? [y/N] "
    read response
    if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
        exit 0
    fi
else
    printf "${green}✓ MCP servers: $server_count active${reset}\n"
fi

echo ""
echo "🚀 Launching AutoFinance Dashboard..."
echo ""

# Run the new Textual-based CLI (high performance)
python dashboard_new.py

echo ""
echo "Thanks for using AutoFinance! 👋"
