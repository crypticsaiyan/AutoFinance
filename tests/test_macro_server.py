"""
Test script for Macro Economics Server
Port: 9010
"""

import requests
import json

BASE_URL = "http://172.17.0.1:9010/mcp"

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
print("Testing Macro Economics Server (Port 9010)")
print("=" * 80)

# Test 1: Initialize
print("\n🌍 Test 1: Initialize MCP session...")
result = make_mcp_call("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "test", "version": "1.0"}
})
print(f"✅ Initialized: {result.get('result', {}).get('serverInfo', {}).get('name')}")

# Test 2: Analyze macro environment
print("\n🌍 Test 2: Analyze macro environment...")
result = make_mcp_call("tools/call", {
    "name": "analyze_macro",
    "arguments": {}
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Market regime: {content.get('market_regime', 'N/A')}")
    print(f"Investment stance: {content.get('investment_stance', 'N/A')}")
    print(f"Risk appetite: {content.get('risk_appetite', 'N/A')}")
    indicators = content.get("indicators", {})
    print(f"GDP growth: {indicators.get('gdp_growth', 'N/A')}%")
    print(f"Inflation: {indicators.get('inflation', 'N/A')}%")
    print("✅ Macro analysis PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 3: Get macro indicators
print("\n🌍 Test 3: Get macro indicators...")
result = make_mcp_call("tools/call", {
    "name": "get_macro_indicators",
    "arguments": {}
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"GDP growth: {content.get('gdp_growth', 'N/A')}%")
    print(f"Inflation: {content.get('inflation', 'N/A')}%")
    print(f"Unemployment: {content.get('unemployment', 'N/A')}%")
    print(f"Interest rate: {content.get('interest_rate', 'N/A')}%")
    print(f"Source: {content.get('source', 'N/A')}")
    print("✅ Macro indicators test PASSED")
else:
    print("❌ Test FAILED:", result)

print("\n" + "=" * 80)
print("Macro Economics Server Testing Complete!")
print("=" * 80)
