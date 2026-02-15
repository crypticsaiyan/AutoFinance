"""Test script for Volatility Analysis Server - Port: 9010"""
import requests, json

BASE_URL = "http://172.17.0.1:9010/mcp"

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

print("="*80 + "\nTesting Volatility Analysis Server (Port 9010)\n" + "="*80)
mcp = MCPSession(BASE_URL)

print("\n📈 Test 1: Initialize...")
result = mcp.initialize()
if result:
    print(f"✅ Initialized: {result.get('result',{}).get('serverInfo',{}).get('name')}")
else:
    print("❌ FAILED"); exit(1)

print("\n📈 Test 2: Calculate historical volatility for AAPL...")
result = mcp.call("tools/call", {"name":"calculate_historical_volatility","arguments":{"symbol":"AAPL","period":"3mo"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Volatility: {content.get('volatility')}%, Period: {content.get('period')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📈 Test 3: Detect volatility regime for BTCUSDT...")
result = mcp.call("tools/call", {"name":"detect_volatility_regime","arguments":{"symbol":"BTCUSDT"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Regime: {content.get('regime')}, Symbol: {content.get('symbol')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📈 Test 4: Get volatility score for TSLA...")
result = mcp.call("tools/call", {"name":"get_volatility_score","arguments":{"symbol":"TSLA"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Volatility: {content.get('volatility')}%, Risk Level: {content.get('risk_level')}, Score: {content.get('score')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📈 Test 5: Compare volatility across symbols...")
result = mcp.call("tools/call", {"name":"compare_volatility","arguments":{"symbols":["AAPL","MSFT","TSLA"]}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Symbols compared: {len(content.get('symbols',{}))} ")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n" + "="*80 + "\nVolatility Server Testing Complete!\n" + "="*80)
