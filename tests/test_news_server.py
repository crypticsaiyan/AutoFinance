"""Test script for News Sentiment Server - Port: 9008"""
import requests, json

BASE_URL = "http://172.17.0.1:9008/mcp"

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

print("="*80 + "\nTesting News Sentiment Server (Port 9008)\n" + "="*80)
mcp = MCPSession(BASE_URL)

print("\n📰 Test 1: Initialize...")
result = mcp.initialize()
if result:
    print(f"✅ Initialized: {result.get('result',{}).get('serverInfo',{}).get('name')}")
else:
    print("❌ FAILED"); exit(1)

print("\n📰 Test 2: Analyze sentiment for AAPL...")
result = mcp.call("tools/call", {"name":"analyze_sentiment","arguments":{"symbol":"AAPL"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Symbol: {content.get('symbol')}, Sentiment: {content.get('sentiment')}, Score: {content.get('score')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📰 Test 3: Get news for BTCUSDT...")
result = mcp.call("tools/call", {"name":"get_news","arguments":{"symbol":"BTCUSDT","count":5}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"News items: {len(content.get('news',[]))}")
    if content.get('news'): print(f"Latest: {content['news'][0].get('title','')[:60]}...")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📰 Test 4: Get market sentiment...")
result = mcp.call("tools/call", {"name":"get_market_sentiment","arguments":{"symbols":["AAPL","TSLA","MSFT"]}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Market: {content.get('market_sentiment')}, Avg: {content.get('average_score')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n" + "="*80 + "\nNews Server Testing Complete!\n" + "="*80)
