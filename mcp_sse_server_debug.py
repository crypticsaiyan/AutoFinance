#!/usr/bin/env python3
"""
MCP Server HTTP/SSE Gateway for Archestra - DEBUG VERSION
Logs all incoming requests to help troubleshoot Archestra connectivity
"""

import sys
from pathlib import Path
import logging
from datetime import datetime

# Add mcp-servers to path
sys.path.insert(0, str(Path(__file__).parent / "mcp-servers"))

from mcp.server.transport_security import TransportSecuritySettings
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class DebugLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests with full details"""
    
    async def dispatch(self, request, call_next):
        logger.info("=" * 80)
        logger.info(f"📥 INCOMING REQUEST")
        logger.info(f"   Method: {request.method}")
        logger.info(f"   URL: {request.url}")
        logger.info(f"   Path: {request.url.path}")
        logger.info(f"   Query: {request.url.query}")
        logger.info(f"   Headers:")
        for key, value in request.headers.items():
            logger.info(f"      {key}: {value}")
        
        # Try to read body if present
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            if body:
                try:
                    logger.info(f"   Body: {body.decode('utf-8')[:500]}")
                except:
                    logger.info(f"   Body (bytes): {body[:100]}")
                # Need to recreate request with body for downstream handlers
                from starlette.requests import Request
                
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request = Request(request.scope, receive)
        
        logger.info("=" * 80)
        
        response = await call_next(request)
        
        logger.info(f"📤 RESPONSE: {response.status_code}")
        logger.info("=" * 80)
        
        return response


def create_app(server_name: str, server_path: str):
    """Create Starlette app for an MCP server with debugging"""
    
    # Import the MCP server instance
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
    else:
        raise ValueError(f"Unknown server: {server_name}")
    
    logger.info(f"🚀 Loaded MCP server: {server_name}")
    logger.info(f"   Server name: {mcp.name}")
    logger.info(f"   Tools: {len(mcp._tool_manager._tools)}")
    
    # Disable DNS rebinding protection for Docker access
    mcp.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=False
    )
    
    # Get the streamable HTTP app (Archestra uses this, not SSE!)
    # The MCP endpoint will be at /mcp
    streamable_http_app = mcp.streamable_http_app()
    
    # Add debug routes
    async def root_get(request):
        logger.info("📍 Root endpoint accessed (GET)")
        return JSONResponse({
            "server": server_name,
            "status": "running",
            "protocol": "mcp-sse",
            "endpoints": {
                "sse": "/sse",
                "messages": "/messages",
                "debug": "/debug"
            }
        })
    
    async def debug_info(request):
        logger.info("🔍 Debug endpoint accessed")
        return JSONResponse({
            "server": server_name,
            "mcp_name": mcp.name,
            "tools_count": len(mcp._tool_manager._tools),
            "tools": [tool.name for tool in mcp._tool_manager._tools.values()],
            "endpoints": {
                "sse": f"http://172.17.0.1:{SERVERS[server_name]['port']}/sse",
                "messages": f"http://172.17.0.1:{SERVERS[server_name]['port']}/messages",
                "root": f"http://172.17.0.1:{SERVERS[server_name]['port']}/"
            },
            "docker_accessible": True,
            "dns_rebinding_protection": False
        })
    
    # Get the streamable HTTP app (Archestra uses this, not SSE!)
    streamable_http_app = mcp.streamable_http_app()
    
    # Create Starlette app with debug routes
    routes = [
        Route("/", endpoint=root_get, methods=["GET"]),
        Route("/debug", endpoint=debug_info),
    ]
    
    # Add the streamable HTTP app routes (handles POST at /)
    for route in streamable_http_app.routes:
        routes.append(route)
    
    middleware = [
        Middleware(DebugLoggingMiddleware)
    ]
    
    app = Starlette(routes=routes, middleware=middleware)
    
    return app


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
    
    logger.info("🚀 Starting DEBUG MCP server")
    logger.info(f"   Server: {server_name}")
    logger.info(f"   Path: {server_path}")
    logger.info(f"   Port: {config['port']}")
    logger.info("")
    logger.info(f"🔗 Archestra URL: http://172.17.0.1:{config['port']}")
    logger.info(f"📊 Debug info: http://172.17.0.1:{config['port']}/debug")
    logger.info("")
    logger.info("🔍 ALL REQUESTS WILL BE LOGGED")
    logger.info("=" * 80)
    
    app = create_app(server_name, str(server_path))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config["port"],
        log_level="debug",
        access_log=True
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mcp_sse_server_debug.py <server_name>")
        print(f"Available servers: {', '.join(SERVERS.keys())}")
        sys.exit(1)
    
    server_name = sys.argv[1]
    run_server(server_name)
