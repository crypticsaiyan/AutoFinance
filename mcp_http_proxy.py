#!/usr/bin/env python3
"""
Simple HTTP proxy for MCP stdio servers
Exposes MCP servers as HTTP endpoints for remote access
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os
import sys

app = Flask(__name__)
CORS(app)

# Server configurations
SERVERS = {
    "market": {
        "command": "/home/cryptosaiyan/Documents/AutoFinance/venv/bin/python",
        "args": ["/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/market/server_real.py"],
        "port": 8001
    },
    "risk": {
        "command": "/home/cryptosaiyan/Documents/AutoFinance/venv/bin/python",
        "args": ["/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/risk/server.py"],
        "port": 8002
    },
    "execution": {
        "command": "/home/cryptosaiyan/Documents/AutoFinance/venv/bin/python",
        "args": ["/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/execution/server.py"],
        "port": 8003
    },
    "compliance": {
        "command": "/home/cryptosaiyan/Documents/AutoFinance/venv/bin/python",
        "args": ["/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/compliance/server.py"],
        "port": 8004
    },
    "technical": {
        "command": "/home/cryptosaiyan/Documents/AutoFinance/venv/bin/python",
        "args": ["/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/technical/server.py"],
        "port": 8005
    }
}

def call_mcp_server(server_name, json_rpc_request):
    """Call an MCP server via stdio and return the response"""
    if server_name not in SERVERS:
        return {"error": f"Unknown server: {server_name}"}
    
    server_config = SERVERS[server_name]
    
    try:
        # Start the MCP server process
        process = subprocess.Popen(
            [server_config["command"]] + server_config["args"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send JSON-RPC request
        stdout, stderr = process.communicate(
            input=json.dumps(json_rpc_request) + "\n",
            timeout=10
        )
        
        # Parse response
        if stdout:
            return json.loads(stdout.strip())
        else:
            return {"error": "No response from server", "stderr": stderr}
            
    except subprocess.TimeoutExpired:
        process.kill()
        return {"error": "Request timeout"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/servers', methods=['GET'])
def list_servers():
    """List available MCP servers"""
    return jsonify({
        "servers": list(SERVERS.keys()),
        "endpoints": {
            name: f"http://localhost:{config['port']}" 
            for name, config in SERVERS.items()
        }
    })

@app.route('/<server_name>', methods=['POST'])
def proxy_request(server_name):
    """Proxy JSON-RPC request to MCP server"""
    json_rpc_request = request.get_json()
    
    if not json_rpc_request:
        return jsonify({"error": "Invalid JSON-RPC request"}), 400
    
    response = call_mcp_server(server_name, json_rpc_request)
    return jsonify(response)

@app.route('/<server_name>/sse', methods=['GET'])
def sse_endpoint(server_name):
    """SSE endpoint for MCP server (for Archestra)"""
    return jsonify({
        "message": "SSE endpoint",
        "server": server_name,
        "url": f"http://localhost:8000/{server_name}"
    })

if __name__ == "__main__":
    PORT = 9100
    print("🌐 AutoFinance MCP HTTP Proxy")
    print("=" * 50)
    print(f"Main Proxy: http://localhost:{PORT}")
    print()
    print("Available servers:")
    for name, config in SERVERS.items():
        url = f"http://localhost:{PORT}/{name}"
        print(f"  • {name:15} → {url}")
    print()
    print("Archestra Configuration:")
    print(f"  URL format: http://localhost:{PORT}/<server-name>")
    print()
    
    app.run(host="0.0.0.0", port=PORT, debug=False)
