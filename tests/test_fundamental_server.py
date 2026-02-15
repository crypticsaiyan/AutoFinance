"""Test script for Fundamental Analysis Server - Port: 9006"""
import requests, json

BASE_URL = "http://172.17.0.1:9006/mcp"

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

print("="*80 + "\nTesting Fundamental Analysis Server (Port 9006)\n" + "="*80)
mcp = MCPSession(BASE_URL)

print("\n💼 Test 1: Initialize...")
result = mcp.initialize()
if result:
    print(f"✅ Initialized: {result.get('result',{}).get('serverInfo',{}).get('name')}")
else:
    print("❌ FAILED"); exit(1)

print("\n💼 Test 2: Analyze fundamentals for AAPL...")
result = mcp.call("tools/call", {"name":"analyze_fundamentals","arguments":{"symbol":"AAPL"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Valuation: {content.get('valuation_score')}, Quality: {content.get('quality_score')}, Recommendation: {content.get('recommendation')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n💼 Test 3: Get company overview for MSFT...")
result = mcp.call("tools/call", {"name":"get_company_overview","arguments":{"symbol":"MSFT"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Name: {content.get('name')}, Sector: {content.get('sector')}, Industry: {content.get('industry')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n💼 Test 4: Compare fundamentals...")
result = mcp.call("tools/call", {"name":"compare_fundamentals","arguments":{"symbols":["AAPL","MSFT","GOOGL"]}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Symbols compared: {len(content.get('symbols',{}))}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n💼 Test 4: Get investment thesis for TSLA...")
result = mcp.call("tools/call", {"name":"get_investment_thesis","arguments":{"symbol":"TSLA"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Symbol: {content.get('symbol')}, Thesis: {len(content.get('thesis',''))} chars")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n" + "="*80 + "\nFundamental Server Testing Complete!\n" + "="*80)
