import requests
import json
import sys

BASE_URL = "http://localhost:9003/mcp"

def call_tool(name, args={}):
    try:
        resp = requests.post(BASE_URL, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": args
            }
        })
        print(f"[{name}] Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}...")
        return resp.json()
    except Exception as e:
        print(f"Error calling {name}: {e}")
        return None

# 1. Check initial state
print("\n--- Checking Portfolio ---")
portfolio = call_tool("get_portfolio_state")

# 2. Reset if needed
print("\n--- Resetting Portfolio ---")
call_tool("reset_portfolio", {"initial_cash": 100000})

# 3. Apply a Trade (Buy BTC)
print("\n--- Executing Trade (Buy 0.1 BTC at $95000) ---")
# Note: execution server requires 'risk_validation' dict as argument 
# because it normally comes from risk server. We mock it here.
trade = call_tool("execute_trade", {
    "trade_id": "test_1",
    "symbol": "BTC",
    "action": "BUY",
    "quantity": 0.1,
    "price": 95000.0,
    "approved": True,
    "risk_validation": {"risk_score": 0.1, "approved": True}
})

# 4. Check State Again
print("\n--- Checking Portfolio After Trade ---")
portfolio_after = call_tool("get_portfolio_state")
