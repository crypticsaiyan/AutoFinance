"""
Test script for Market Server (Real Yahoo Finance data)
Port: 9001
"""

import requests
import json

BASE_URL = "http://172.17.0.1:9001/mcp"

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

def format_dict(d, indent=2):
    """Format dictionary for readable output"""
    for key, value in d.items():
        if isinstance(value, dict):
            print(f"{' ' * indent}{key}:")
            format_dict(value, indent + 2)
        else:
            print(f"{' ' * indent}{key}: {value}")

print("=" * 80)
print("Testing Market Server (Port 9001)")
print("=" * 80)

# Test 1: Initialize
print("\n📊 Test 1: Initialize MCP session...")
result = make_mcp_call("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "test", "version": "1.0"}
})
print(f"✅ Initialized: {result.get('result', {}).get('serverInfo', {}).get('name')}")

# Test 2: Get live price
print("\n📊 Test 2: Get live price for AAPL...")
result = make_mcp_call("tools/call", {
    "name": "get_live_price",
    "arguments": {"symbol": "AAPL"}
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print("symbol:", content["symbol"])
    print("price: $" + str(content["price"]))
    print("change_24h:", content.get("change_24h", "N/A"))
    print("✅ AAPL live price test PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 3: Get market overview
print("\n📊 Test 3: Get market overview...")
result = make_mcp_call("tools/call", {
    "name": "get_market_overview",
    "arguments": {}
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Markets tracked: {len(content.get('markets', []))}")
    for market in content.get("markets", [])[:3]:
        print(f"  - {market['symbol']}: ${market['price']}")
    print("✅ Market overview test PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 4: Get candles
print("\n📊 Test 4: Get candle data for BTCUSDT...")
result = make_mcp_call("tools/call", {
    "name": "get_candles",
    "arguments": {
        "symbol": "BTCUSDT",
        "interval": "1d",
        "count": 5
    }
})
if "result" in result:
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
result = make_mcp_call("tools/call", {
    "name": "calculate_volatility",
    "arguments": {"symbol": "TSLA"}
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"30-day volatility: {content.get('volatility_30d', 'N/A')}%")
    print(f"Risk level: {content.get('risk_level', 'N/A')}")
    print("✅ Volatility calculation test PASSED")
else:
    print("❌ Test FAILED:", result)

print("\n" + "=" * 80)
print("Market Server Testing Complete!")
print("=" * 80)
