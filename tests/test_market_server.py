"""Test script for Market Server (Yahoo Finance) - Port: 9001"""
import requests, json

BASE_URL = "http://172.17.0.1:9001/mcp"

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

print("="*80 + "\nTesting Market Server - Yahoo Finance (Port 9001)\n" + "="*80)
mcp = MCPSession(BASE_URL)

print("\n📊 Test 1: Initialize...")
result = mcp.initialize()
if result:
    print(f"✅ Initialized: {result.get('result',{}).get('serverInfo',{}).get('name')}")
else:
    print("❌ FAILED"); exit(1)

print("\n📊 Test 2: Get live price for AAPL...")
result = mcp.call("tools/call", {"name":"get_live_price","arguments":{"symbol":"AAPL"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Symbol: {content['symbol']}, Price: ${content.get('price')}")
    print(f"Change: {content.get('change_24h')}, Source: {content.get('source')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📊 Test 3: Get market overview...")
result = mcp.call("tools/call", {"name":"get_market_overview","arguments":{}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    indices = content.get("indices", {})
    print(f"Indices tracked: {len(indices)}")
    for name, data in list(indices.items())[:3]:
        if "price" in data:
            print(f"  {name}: ${data['price']} ({data.get('change_pct', 'N/A')}%)")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📊 Test 4: Get candle data for BTCUSDT...")
result = mcp.call("tools/call", {"name":"get_candles","arguments":{"symbol":"BTCUSDT","timeframe":"1d","periods":5}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    candles = content.get("candles", [])
    print(f"Candles returned: {len(candles)}")
    if candles:
        latest = candles[-1]
        print(f"Latest: Open ${latest['open']}, Close ${latest['close']}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n" + "="*80 + "\nMarket Server Testing Complete!\n" + "="*80)
