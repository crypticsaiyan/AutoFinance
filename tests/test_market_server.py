"""
Test script for Market Server (Real Yahoo Finance data)
Port: 9001
"""

import requests
import json

BASE_URL = "http://172.17.0.1:9001/mcp"

class MCPSession:
    """MCP session manager with SSE support"""
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = None
        self.message_id = 0
        
    def parse_sse_response(self, response):
        """Parse Server-Sent Events (SSE) response"""
        # Extract session ID from headers if present
        if 'mcp-session-id' in response.headers:
            self.session_id = response.headers['mcp-session-id']
            
        lines = response.text.strip().split('\n')
        for line in lines:
            if line.startswith('data: '):
                return json.loads(line[6:])
        return None
    
    def call(self, method, params=None):
        """Make an MCP protocol call"""
        self.message_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": method,
            "params": params or {}
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        
        response = self.session.post(self.base_url, json=payload, headers=headers)
        return self.parse_sse_response(response)
    
    def initialize(self):
        """Initialize MCP session"""
        return self.call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        })

print("=" * 80)
print("Testing Market Server (Port 9001)")
print("=" * 80)

# Create session
mcp = MCPSession(BASE_URL)

# Test 1: Initialize
print("\n📊 Test 1: Initialize MCP session...")
result = mcp.initialize()
if result:
    print(f"✅ Initialized: {result.get('result', {}).get('serverInfo', {}).get('name')}")
else:
    print("❌ Initialization FAILED")
    exit(1)

# Test 2: Get live price
print("\n📊 Test 2: Get live price for AAPL...")
result = mcp.call("tools/call", {
    "name": "get_live_price",
    "arguments": {"symbol": "AAPL"}
})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print("symbol:", content["symbol"])
    print("price: $" + str(content["price"]))
    print("change_24h:", content.get("change_24h", "N/A"))
    print("✅ AAPL live price test PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 3: Get market overview
print("\n📊 Test 3: Get market overview...")
result = mcp.call("tools/call", {
    "name": "get_market_overview",
    "arguments": {}
})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Markets tracked: {len(content.get('markets', []))}")
    for market in content.get("markets", [])[:3]:
        print(f"  - {market['symbol']}: ${market['price']}")
    print("✅ Market overview test PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 4: Get candles
print("\n📊 Test 4: Get candle data for BTCUSDT...")
result = mcp.call("tools/call", {
    "name": "get_candles",
    "arguments": {
        "symbol": "BTCUSDT",
        "interval": "1d",
        "count": 5
    }
})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Candles returned: {len(content.get('candles', []))}")
    if content.get("candles"):
        latest = content["candles"][-1]
        print(f"Latest candle: Open ${latest['open']}, Close ${latest['close']}")
    print("✅ Candle data test PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 5: Calculate volatility
print("\n📊 Test 5: Calculate volatility for TSLA...")
result = mcp.call("tools/call", {
    "name": "calculate_volatility",
    "arguments": {"symbol": "TSLA"}
})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"30-day volatility: {content.get('volatility_30d', 'N/A')}%")
    print(f"Risk level: {content.get('risk_level', 'N/A')}")
    print("✅ Volatility calculation test PASSED")
else:
    print("❌ Test FAILED:", result)

print("\n" + "=" * 80)
print("Market Server Testing Complete!")
print("=" * 80)
