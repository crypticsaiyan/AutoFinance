"""
Test script for News Sentiment Server
Port: 9009
"""

import requests
import json

BASE_URL = "http://172.17.0.1:9009/mcp"

def make_mcp_call(method, params=None):
    """Make an MCP protocol call"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.post(BASE_URL, json=payload, headers=headers)
    return response.json()

print("=" * 80)
print("Testing News Sentiment Server (Port 9009)")
print("=" * 80)

# Test 1: Initialize
print("\n📰 Test 1: Initialize MCP session...")
result = make_mcp_call("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "test", "version": "1.0"}
})
print(f"✅ Initialized: {result.get('result', {}).get('serverInfo', {}).get('name')}")

# Test 2: Analyze sentiment for AAPL
print("\n📰 Test 2: Analyze sentiment for AAPL...")
result = make_mcp_call("tools/call", {
    "name": "analyze_sentiment",
    "arguments": {"symbol": "AAPL"}
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Overall sentiment: {content.get('overall_sentiment', 'N/A')}")
    print(f"Sentiment score: {content.get('sentiment_score', 'N/A')}")
    print(f"Articles analyzed: {content.get('article_count', 'N/A')}")
    print("✅ AAPL sentiment analysis PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 3: Get news for BTCUSDT
print("\n📰 Test 3: Get news headlines for BTCUSDT...")
result = make_mcp_call("tools/call", {
    "name": "get_news",
    "arguments": {
        "symbol": "BTCUSDT",
        "count": 5
    }
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    news_items = content.get("news", [])
    print(f"News items returned: {len(news_items)}")
    for i, item in enumerate(news_items[:3], 1):
        print(f"\n  {i}. {item.get('headline', 'N/A')}")
        print(f"     Sentiment: {item.get('sentiment', 'N/A')} (score: {item.get('score', 'N/A')})")
    print("✅ News headlines test PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 4: Analyze sentiment for Tesla
print("\n📰 Test 4: Analyze sentiment for TSLA...")
result = make_mcp_call("tools/call", {
    "name": "analyze_sentiment",
    "arguments": {"symbol": "TSLA"}
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Overall sentiment: {content.get('overall_sentiment', 'N/A')}")
    print(f"Sentiment score: {content.get('sentiment_score', 'N/A')}")
    print(f"Source: {content.get('source', 'N/A')}")
    print("✅ TSLA sentiment analysis PASSED")
else:
    print("❌ Test FAILED:", result)

print("\n" + "=" * 80)
print("News Sentiment Server Testing Complete!")
print("=" * 80)
