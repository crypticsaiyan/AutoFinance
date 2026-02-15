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

print("\n📰 Test 2: Analyze sentiment for AAPL (LLM-powered)...")
result = mcp.call("tools/call", {"name":"analyze_sentiment","arguments":{"symbol":"AAPL"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Symbol: {content.get('symbol')}, Sentiment: {content.get('sentiment')}, Score: {content.get('score')}")
    print(f"Method: {content.get('analysis_method')}, Source: {content.get('source')}")
    if content.get("news_items"):
        item = content["news_items"][0]
        print(f"Sample reasoning: {item.get('reasoning', 'N/A')[:80]}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📰 Test 3: Get news for BTCUSDT (with LLM sentiment)...")
result = mcp.call("tools/call", {"name":"get_news","arguments":{"symbol":"BTCUSDT","count":5}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"News items: {content.get('count')}")
    if content.get('news_items'):
        item = content['news_items'][0]
        print(f"Latest: {item.get('headline','')[:60]}...")
        print(f"Sentiment: {item.get('sentiment')}, Method: {item.get('method')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📰 Test 4: Get market sentiment (multi-symbol)...")
result = mcp.call("tools/call", {"name":"get_market_sentiment","arguments":{"symbols":["AAPL","TSLA","MSFT"]}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Market: {content.get('market_sentiment')}, Score: {content.get('market_score')}")
    for sym in content.get("symbols", []):
        print(f"  {sym['symbol']}: {sym['sentiment']} ({sym.get('method','unknown')})")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📰 Test 5: Analyze custom headline (LLM)...")
result = mcp.call("tools/call", {"name":"analyze_custom_headline","arguments":{"headline":"Tesla stock surges 15% on record earnings report"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Headline: {content.get('headline')[:50]}...")
    print(f"Sentiment: {content.get('sentiment')}, Score: {content.get('score')}")
    print(f"Method: {content.get('method')}, Reasoning: {content.get('reasoning','')[:80]}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n" + "="*80 + "\nNews Server Testing Complete!\n" + "="*80)
