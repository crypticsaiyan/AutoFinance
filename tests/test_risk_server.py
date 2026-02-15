"""Test script for Risk Management Server - Port: 9002"""
import requests, json

BASE_URL = "http://172.17.0.1:9002/mcp"

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

print("="*80 + "\nTesting Risk Management Server (Port 9002)\n" + "="*80)
mcp = MCPSession(BASE_URL)

print("\n🛡️ Test 1: Initialize...")
result = mcp.initialize()
if result:
    print(f"✅ Initialized: {result.get('result',{}).get('serverInfo',{}).get('name')}")
else:
    print("❌ FAILED"); exit(1)

print("\n🛡️ Test 2: Get risk policy...")
result = mcp.call("tools/call", {"name":"get_risk_policy","arguments":{}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Max position size: {content.get('max_position_size_pct')}%, Max portfolio risk: {content.get('max_portfolio_risk_pct')}%")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n🛡️ Test 3: Validate small trade (should PASS)...")
result = mcp.call("tools/call", {"name":"validate_trade","arguments":{
    "symbol":"AAPL",
    "action":"BUY",
    "quantity":10,
    "price":250.0,
    "confidence":0.8,
    "volatility":0.25,
    "position_size_pct":0.025,
    "trade_value":2500.0
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Approved: {content.get('approved')}, Risk Level: {content.get('risk_level')}")
    if content.get('approved'):
        print("✅ Trade approved as expected")
    else:
        print(f"❌ Trade rejected unexpectedly: {content.get('violations')}")
else:
    print(f"❌ FAILED: {result}")

print("\n🛡️ Test 4: Validate oversized trade (should FAIL)...")
result = mcp.call("tools/call", {"name":"validate_trade","arguments":{
    "symbol":"AAPL",
    "action":"BUY",
    "quantity":500,
    "price":250.0,
    "confidence":0.8,
    "volatility":0.25,
    "position_size_pct":0.5,
    "trade_value":125000.0
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Approved: {content.get('approved')}, Risk Level: {content.get('risk_level')}")
    if not content.get('approved'):
        print(f"✅ Trade correctly rejected: {content.get('violations',[])[:1]}")
    else:
        print("❌ Oversized trade approved unexpectedly")
else:
    print(f"❌ FAILED: {result}")

print("\n🛡️ Test 5: Validate low confidence trade (should FAIL)...")
result = mcp.call("tools/call", {"name":"validate_trade","arguments":{
    "symbol":"AAPL",
    "action":"BUY",
    "quantity":10,
    "price":250.0,
    "confidence":0.5,
    "volatility":0.25,
    "position_size_pct":0.025,
    "trade_value":2500.0
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Approved: {content.get('approved')}, Risk Level: {content.get('risk_level')}")
    if not content.get('approved'):
        print(f"✅ Low confidence trade correctly rejected")
    else:
        print("❌ Low confidence trade approved unexpectedly")
else:
    print(f"❌ FAILED: {result}")

print("\n" + "="*80 + "\nRisk Server Testing Complete!\n" + "="*80)
