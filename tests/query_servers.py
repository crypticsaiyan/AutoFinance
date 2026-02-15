"""Query all servers to discover their actual tools"""
import requests
import json

SERVERS = {
    9002: "Risk",
    9003: "Execution", 
    9005: "Technical",
    9006: "Fundamental",
    9009: "News",
    9010: "Macro"
}

def query_server(port):
    base_url = f"http://172.17.0.1:{port}/mcp"
    
    # Initialize session
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    try:
        response = requests.post(base_url, json=init_payload, headers=headers, timeout=3)
        
        # Parse SSE response
        session_id = response.headers.get('mcp-session-id')
        for line in response.text.split('\n'):
            if line.startswith('data: '):
                data = json.loads(line[6:])
                server_name = data.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')
                
                # Now list tools
                tools_payload = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
                
                headers_with_session = headers.copy()
                if session_id:
                    headers_with_session['mcp-session-id'] = session_id
                
                tools_response = requests.post(base_url, json=tools_payload, headers=headers_with_session, timeout=3)
                
                for tline in tools_response.text.split('\n'):
                    if tline.startswith('data: '):
                        tools_data = json.loads(tline[6:])
                        tools = tools_data.get('result', {}).get('tools', [])
                        
                        print(f"\n{'='*80}")
                        print(f"Port {port}: {server_name}")
                        print(f"{'='*80}")
                        for tool in tools:
                            print(f"\n  Tool: {tool['name']}")
                            print(f"  Description: {tool.get('description', 'N/A')}")
                            if 'inputSchema' in tool:
                                props = tool['inputSchema'].get('properties', {})
                                required = tool['inputSchema'].get('required', [])
                                if props:
                                    print(f"  Parameters:")
                                    for param, schema in props.items():
                                        req = " (required)" if param in required else ""
                                        print(f"    - {param}{req}: {schema.get('type', 'any')} - {schema.get('description', '')}")
                        return True
                        
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"Port {port}: ERROR - {e}")
        print(f"{'='*80}")
        return False

for port, name in SERVERS.items():
    query_server(port)
