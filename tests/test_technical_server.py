"""Test script for Technical Analysis Server - Port: 9005"""
import requests, json

BASE_URL = "http://172.17.0.1:9005/mcp"

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

print("="*80 + "\nTesting Technical Analysis Server (Port  9005)\n" + "="*80)
mcp = MCPSession(BASE_URL)

print("\n📊 Test 1: Initialize...")
result = mcp.initialize()
if result:
    print(f"✅ Initialized: {result.get('result',{}).get('serverInfo',{}).get('name')}")
else:
    print("❌ FAILED"); exit(1)

print("\n📊 Test 2: Generate signal for AAPL...")
result = mcp.call("tools/call", {"name":"generate_signal","arguments":{"symbol":"AAPL","timeframe":"1mo"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Signal: {content.get('signal')}, Confidence: {content.get('confidence')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📊 Test 3: Calculate RSI for TSLA...")
result = mcp.call("tools/call", {"name":"calculate_rsi_tool","arguments":{"symbol":"TSLA","period":14}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"RSI: {content.get('rsi')}, Interpretation: {content.get('interpretation')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📊 Test 4: Calculate MACD for BTCUSDT...")
result = mcp.call("tools/call", {"name":"calculate_macd_tool","arguments":{"symbol":"BTCUSDT"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"MACD: {content.get('macd_line')}, Signal: {content.get('signal_line')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📊 Test 5: Calculate Bollinger Bands for AAPL...")
result = mcp.call("tools/call", {"name":"calculate_bollinger_bands_tool","arguments":{"symbol":"AAPL","period":20}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Upper: {content.get('upper_band')}, Lower: {content.get('lower_band')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📊 Test 6: Calculate support/resistance for MSFT...")
result = mcp.call("tools/call", {"name":"calculate_support_resistance","arguments":{"symbol":"MSFT","period":"1mo"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Support levels: {len(content.get('support',[]))}, Resistance levels: {len(content.get('resistance',[]))}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n" + "="*80 + "\nTechnical Server Testing Complete!\n" + "="*80)
