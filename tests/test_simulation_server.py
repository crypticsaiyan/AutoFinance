"""Test script for Simulation Engine Server (Real Data) - Port: 9012"""
import requests, json

BASE_URL = "http://172.17.0.1:9012/mcp"

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

print("="*80 + "\nTesting Simulation Engine Server (Port 9012)\n" + "="*80)
mcp = MCPSession(BASE_URL)

print("\n🎲 Test 1: Initialize...")
result = mcp.initialize()
if result:
    print(f"✅ Initialized: {result.get('result',{}).get('serverInfo',{}).get('name')}")
else:
    print("❌ FAILED"); exit(1)

print("\n🎲 Test 2: Simulate AAPL trade (real volatility)...")
result = mcp.call("tools/call", {"name":"simulate_trade","arguments":{
    "symbol":"AAPL","quantity":50,"action":"buy","entry_price":230.0,"current_portfolio_value":100000
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    scenarios = content.get("scenarios", {})
    risk = content.get("risk_metrics", {})
    print(f"Source: {content.get('source')}")
    print(f"Bull: ${scenarios.get('bull',{}).get('price')} ({scenarios.get('bull',{}).get('return_pct')}%)")
    print(f"Base: ${scenarios.get('base',{}).get('price')} ({scenarios.get('base',{}).get('return_pct')}%)")
    print(f"Bear: ${scenarios.get('bear',{}).get('price')} ({scenarios.get('bear',{}).get('return_pct')}%)")
    print(f"Volatility: {risk.get('annualized_volatility')}%, Max DD: {risk.get('max_historical_drawdown')}%")
    print(f"Recommendation: {content.get('recommendation')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n🎲 Test 3: Backtest momentum strategy on TSLA (real data)...")
result = mcp.call("tools/call", {"name":"simulate_strategy","arguments":{
    "strategy_type":"momentum","symbol":"TSLA","initial_capital":10000,"timeframe_days":90
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Source: {content.get('source')}")
    print(f"Strategy: {content.get('strategy')}, Return: {content.get('total_return_pct')}%")
    print(f"Buy & Hold: {content.get('buy_hold_return_pct')}%, Alpha: {content.get('alpha')}%")
    print(f"Sharpe: {content.get('sharpe_ratio')}, Max DD: {content.get('max_drawdown_pct')}%")
    print(f"Trades: {content.get('total_trades')}, Verdict: {content.get('verdict')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n🎲 Test 4: Backtest buy & hold on BTCUSDT...")
result = mcp.call("tools/call", {"name":"simulate_strategy","arguments":{
    "strategy_type":"buy_and_hold","symbol":"BTCUSDT","initial_capital":5000,"timeframe_days":60
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Return: {content.get('total_return_pct')}%, Final Value: ${content.get('final_value')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n🎲 Test 5: Calculate position size...")
result = mcp.call("tools/call", {"name":"calculate_position_size","arguments":{
    "account_value":100000,"risk_per_trade_pct":2.0,"entry_price":230.0,"stop_loss_price":220.0
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Shares: {content.get('recommended_shares')}, Value: ${content.get('position_value')}")
    print(f"Risk: ${content.get('risk_amount')} ({content.get('risk_pct')}%)")
    print(f"Targets: 1R={content.get('targets',{}).get('1R')}, 2R={content.get('targets',{}).get('2R')}, 3R={content.get('targets',{}).get('3R')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n" + "="*80 + "\nSimulation Engine Testing Complete!\n" + "="*80)
