"""Test script for Execution Server - Port: 9003"""
import requests, json

BASE_URL = "http://172.17.0.1:9003/mcp"

class MCPSession:
    def __init__(self, base_url):
        self.base_url, self.session, self.session_id, self.message_id = base_url, requests.Session(), None, 0
    
    def parse_sse_response(self, response):
        if 'mcp-session-id' in response.headers: self.session_id = response.headers['mcp-session-id']
        for line in response.text.strip().split('\n'):
            if line.startswith('data: '): return json.loads(line[6:])
        return None
    
    def call(self, method, params=None):
        self.message_id += 1
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self.session_id: headers["mcp-session-id"] = self.session_id
        return self.parse_sse_response(self.session.post(self.base_url, json={"jsonrpc":"2.0","id":self.message_id,"method":method,"params":params or {}}, headers=headers))
    
    def initialize(self):
        return self.call("initialize", {"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}})

print("="*80 + "\nTesting Execution Server (Port 9003)\n" + "="*80)
mcp = MCPSession(BASE_URL)

print("\n💼 Test 1: Initialize...")
result = mcp.initialize()
if result:
    print(f"✅ Initialized: {result.get('result',{}).get('serverInfo',{}).get('name')}")
else:
    print("❌ FAILED"); exit(1)

print("\n💼 Test 2: Reset portfolio...")
result = mcp.call("tools/call", {"name":"reset_portfolio","arguments":{"initial_cash":100000}})
if result and "result" in result:
    print("✅ Portfolio reset to $100,000")
else:
    print(f"❌ FAILED: {result}")

print("\n💼 Test 3: Get portfolio state...")
result = mcp.call("tools/call", {"name":"get_portfolio_state","arguments":{}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Cash: ${content.get('cash',0):,.2f}, Total Value: ${content.get('total_value',0):,.2f}, Positions: {len(content.get('positions',{}))}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n💼 Test 4: Execute BUY trade for AAPL...")
result = mcp.call("tools/call", {"name":"execute_trade","arguments":{
    "trade_id":"test_001",
    "symbol":"AAPL",
    "action":"BUY",
    "quantity":10,
    "price":250.0,
    "approved":True,
    "risk_validation":{"approved":True,"risk_level":"LOW"}
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Status: {content.get('status')}, Symbol: {content.get('symbol')}, Quantity: {content.get('quantity')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n💼 Test 5: Update position prices...")
result = mcp.call("tools/call", {"name":"update_position_prices","arguments":{"price_updates":{"AAPL":255.0}}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Prices updated: {len(content.get('updated',{}))}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n💼 Test 6: Execute SELL trade...")
result = mcp.call("tools/call", {"name":"execute_trade","arguments":{
    "trade_id":"test_002",
    "symbol":"AAPL",
    "action":"SELL",
    "quantity":5,
    "price":255.0,
    "approved":True,
    "risk_validation":{"approved":True,"risk_level":"LOW"}
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Status: {content.get('status')}, Quantity: {content.get('quantity')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n" + "="*80 + "\nExecution Server Testing Complete!\n" + "="*80)
