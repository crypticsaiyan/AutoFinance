"""
Test script for Risk Server
Port: 9002
"""

import requests
import json

BASE_URL = "http://172.17.0.1:9002/mcp"

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
print("Testing Risk Server (Port 9002)")
print("=" * 80)

# Test 1: Initialize
print("\n🛡️ Test 1: Initialize MCP session...")
result = make_mcp_call("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "test", "version": "1.0"}
})
print(f"✅ Initialized: {result.get('result', {}).get('serverInfo', {}).get('name')}")

# Test 2: Get risk policy
print("\n🛡️ Test 2: Get risk policy...")
result = make_mcp_call("tools/call", {
    "name": "get_risk_policy",
    "arguments": {}
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Max position size: {content.get('max_position_size_pct', 'N/A')}%")
    print(f"Max portfolio risk: {content.get('max_portfolio_risk_pct', 'N/A')}%")
    print(f"Min confidence: {content.get('min_confidence_threshold', 'N/A')}")
    print("✅ Risk policy test PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 3: Validate trade (should PASS)
print("\n🛡️ Test 3: Validate trade - small position (should PASS)...")
result = make_mcp_call("tools/call", {
    "name": "validate_trade",
    "arguments": {
        "symbol": "AAPL",
        "side": "BUY",
        "quantity": 10,
        "price": 250.0,
        "portfolio_value": 100000.0,
        "confidence": 0.8
    }
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Approved: {content.get('approved', 'N/A')}")
    print(f"Risk level: {content.get('risk_level', 'N/A')}")
    if content.get("approved"):
        print("✅ Small trade validation PASSED")
    else:
        print("❌ Small trade REJECTED (unexpected)")
else:
    print("❌ Test FAILED:", result)

# Test 4: Validate trade (should FAIL - too large)
print("\n🛡️ Test 4: Validate trade - oversized position (should FAIL)...")
result = make_mcp_call("tools/call", {
    "name": "validate_trade",
    "arguments": {
        "symbol": "AAPL",
        "side": "BUY",
        "quantity": 500,
        "price": 250.0,
        "portfolio_value": 100000.0,
        "confidence": 0.8
    }
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Approved: {content.get('approved', 'N/A')}")
    if not content.get("approved"):
        print(f"Rejection reason: {content.get('violations', ['N/A'])[0]}")
        print("✅ Oversized trade correctly REJECTED")
    else:
        print("❌ Oversized trade APPROVED (unexpected)")
else:
    print("❌ Test FAILED:", result)

# Test 5: Validate trade (should FAIL - low confidence)
print("\n🛡️ Test 5: Validate trade - low confidence (should FAIL)...")
result = make_mcp_call("tools/call", {
    "name": "validate_trade",
    "arguments": {
        "symbol": "AAPL",
        "side": "BUY",
        "quantity": 10,
        "price": 250.0,
        "portfolio_value": 100000.0,
        "confidence": 0.5
    }
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Approved: {content.get('approved', 'N/A')}")
    if not content.get("approved"):
        print(f"Rejection reason: {content.get('violations', ['N/A'])[0]}")
        print("✅ Low confidence trade correctly REJECTED")
    else:
        print("❌ Low confidence trade APPROVED (unexpected)")
else:
    print("❌ Test FAILED:", result)

print("\n" + "=" * 80)
print("Risk Server Testing Complete!")
print("=" * 80)
