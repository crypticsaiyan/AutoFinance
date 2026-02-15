"""
Test script for Execution Server
Port: 9003
"""

import requests
import json

BASE_URL = "http://172.17.0.1:9003/mcp"

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
print("Testing Execution Server (Port 9003)")
print("=" * 80)

# Test 1: Initialize
print("\n💼 Test 1: Initialize MCP session...")
result = make_mcp_call("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "test", "version": "1.0"}
})
print(f"✅ Initialized: {result.get('result', {}).get('serverInfo', {}).get('name')}")

# Test 2: Get portfolio state (initial)
print("\n💼 Test 2: Get initial portfolio state...")
result = make_mcp_call("tools/call", {
    "name": "get_portfolio_state",
    "arguments": {}
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Cash balance: ${content.get('cash', 'N/A'):,.2f}")
    print(f"Total value: ${content.get('total_value', 'N/A'):,.2f}")
    print(f"Positions: {len(content.get('positions', []))}")
    print("✅ Portfolio state test PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 3: Execute trade (BUY)
print("\n💼 Test 3: Execute BUY trade for AAPL...")
result = make_mcp_call("tools/call", {
    "name": "execute_trade",
    "arguments": {
        "symbol": "AAPL",
        "side": "BUY",
        "quantity": 10,
        "price": 250.0
    }
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Status: {content.get('status', 'N/A')}")
    print(f"Order ID: {content.get('order_id', 'N/A')}")
    print(f"Total cost: ${content.get('total_cost', 'N/A'):,.2f}")
    print("✅ BUY trade execution PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 4: Get portfolio state (after buy)
print("\n💼 Test 4: Get portfolio state after BUY...")
result = make_mcp_call("tools/call", {
    "name": "get_portfolio_state",
    "arguments": {}
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Cash balance: ${content.get('cash', 'N/A'):,.2f}")
    print(f"Positions: {len(content.get('positions', []))}")
    if content.get("positions"):
        for pos in content["positions"]:
            print(f"  - {pos['symbol']}: {pos['quantity']} shares @ ${pos['avg_price']}")
    print("✅ Post-trade portfolio state PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 5: Execute trade (SELL)
print("\n💼 Test 5: Execute SELL trade for AAPL...")
result = make_mcp_call("tools/call", {
    "name": "execute_trade",
    "arguments": {
        "symbol": "AAPL",
        "side": "SELL",
        "quantity": 5,
        "price": 255.0
    }
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Status: {content.get('status', 'N/A')}")
    print(f"Total proceeds: ${content.get('total_proceeds', 'N/A'):,.2f}")
    print("✅ SELL trade execution PASSED")
else:
    print("❌ Test FAILED:", result)

# Test 6: Get trade history
print("\n💼 Test 6: Get trade history...")
result = make_mcp_call("tools/call", {
    "name": "get_trade_history",
    "arguments": {"limit": 5}
})
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Total trades: {len(content.get('trades', []))}")
    for trade in content.get("trades", [])[:3]:
        print(f"  - {trade['symbol']} {trade['side']} {trade['quantity']} @ ${trade['price']}")
    print("✅ Trade history test PASSED")
else:
    print("❌ Test FAILED:", result)

print("\n" + "=" * 80)
print("Execution Server Testing Complete!")
print("=" * 80)
