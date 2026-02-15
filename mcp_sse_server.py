#!/usr/bin/env python3
"""
MCP Server HTTP/SSE Gateway for Archestra
Exposes MCP servers via HTTP/SSE transport on different ports
"""

import sys
from pathlib import Path

# Add mcp-servers to path
sys.path.insert(0, str(Path(__file__).parent / "mcp-servers"))

from mcp.server.transport_security import TransportSecuritySettings
import uvicorn


def create_app(server_name: str, server_path: str):
    """Create Starlette app for an MCP server"""
    
    # Import the MCP server instance at module level
    sys.path.insert(0, str(Path(server_path).parent))
    
    if server_name == "market":
        from market.server_real import mcp
    elif server_name == "risk":
        from risk.server import mcp
    elif server_name == "execution":
        from execution.server import mcp
    elif server_name == "compliance":
        from compliance.server import mcp
    elif server_name == "technical":
        from technical.server import mcp
    elif server_name == "fundamental":
        from fundamental.server import mcp
    elif server_name == "macro":
        from macro.server import mcp
    elif server_name == "news":
        from news.server import mcp
    elif server_name == "portfolio-analytics":
        sys.path.insert(0, str(Path(server_path).parent.parent))
        import importlib
        portfolio_module = importlib.import_module("portfolio-analytics.server")
        mcp = portfolio_module.mcp
    elif server_name == "volatility":
        from volatility.server import mcp
    elif server_name == "alert-engine":
        sys.path.insert(0, str(Path(server_path).parent.parent))
        import importlib
        alert_module = importlib.import_module("alert-engine.server")
        mcp = alert_module.mcp
    elif server_name == "simulation-engine":
        sys.path.insert(0, str(Path(server_path).parent.parent))
        import importlib
        sim_module = importlib.import_module("simulation-engine.server")
        mcp = sim_module.mcp
    elif server_name == "notification-gateway":
        sys.path.insert(0, str(Path(server_path).parent.parent))
        import importlib
        notif_module = importlib.import_module("notification-gateway.server")
        mcp = notif_module.mcp
    else:
        raise ValueError(f"Unknown server: {server_name}")
    
    # Disable DNS rebinding protection for Docker access
    # This allows Archestra running in Docker to connect via 172.17.0.1
    mcp.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=False
    )
    
    # FastMCP has built-in Streamable HTTP app (what Archestra uses)
    # The MCP endpoint will be at /mcp
    return mcp.streamable_http_app()


# Server configurations
SERVERS = {
    "market": {
        "path": "mcp-servers/market/server_real.py",
        "port": 9001
    },
    "risk": {
        "path": "mcp-servers/risk/server.py",
        "port": 9002
    },
    "execution": {
        "path": "mcp-servers/execution/server.py",
        "port": 9003
    },
    "compliance": {
        "path": "mcp-servers/compliance/server.py",
        "port": 9004
    },
    "technical": {
        "path": "mcp-servers/technical/server.py",
        "port": 9005
    },
    "fundamental": {
        "path": "mcp-servers/fundamental/server.py",
        "port": 9006
    },
    "macro": {
        "path": "mcp-servers/macro/server.py",
        "port": 9007
    },
    "news": {
        "path": "mcp-servers/news/server.py",
        "port": 9008
    },
    "portfolio-analytics": {
        "path": "mcp-servers/portfolio-analytics/server.py",
        "port": 9009
    },
    "volatility": {
        "path": "mcp-servers/volatility/server.py",
        "port": 9010
    },
    "alert-engine": {
        "path": "mcp-servers/alert-engine/server.py",
        "port": 9011
    },
    "simulation-engine": {
        "path": "mcp-servers/simulation-engine/server.py",
        "port": 9012
    },
    "notification-gateway": {
        "path": "mcp-servers/notification-gateway/server.py",
        "port": 9013
    }
}


def run_server(server_name: str):
    """Run a single MCP server with HTTP/SSE transport"""
    if server_name not in SERVERS:
        print(f"❌ Unknown server: {server_name}")
        print(f"Available: {', '.join(SERVERS.keys())}")
        sys.exit(1)
    
    config = SERVERS[server_name]
    server_path = Path(__file__).parent / config["path"]
    
    if not server_path.exists():
        print(f"❌ Server file not found: {server_path}")
        sys.exit(1)
    
    print(f"🚀 Starting {server_name} MCP server (HTTP/SSE)")
    print(f"   Path: {server_path}")
    print(f"   Port: {config['port']}")
    print()
    print(f"🔗 Archestra URL: http://localhost:{config['port']}")
    print()
    
    app = create_app(server_name, str(server_path))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config["port"],
        log_level="info"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mcp_sse_server.py <server_name>")
        print(f"Available servers: {', '.join(SERVERS.keys())}")
        sys.exit(1)
    
    server_name = sys.argv[1]
    run_server(server_name)
