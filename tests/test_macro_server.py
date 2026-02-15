"""Test script for Macro Economics Server (FRED API) - Port: 9007"""
import requests, json

BASE_URL = "http://172.17.0.1:9007/mcp"

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

print("="*80 + "\nTesting Macro Economics Server - FRED API (Port 9007)\n" + "="*80)
mcp = MCPSession(BASE_URL)

print("\n🌍 Test 1: Initialize...")
result = mcp.initialize()
if result:
    print(f"✅ Initialized: {result.get('result',{}).get('serverInfo',{}).get('name')}")
else:
    print("❌ FAILED"); exit(1)

print("\n🌍 Test 2: Analyze macro environment...")
result = mcp.call("tools/call", {"name":"analyze_macro","arguments":{}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Regime: {content.get('market_regime')}, Stance: {content.get('investment_stance')}")
    print(f"Risk: {content.get('risk_environment')}, Source: {content.get('source')}")
    indicators = content.get("indicators", {})
    if indicators.get("gdp_growth") is not None:
        print(f"GDP: {indicators['gdp_growth']}%, Inflation: {indicators.get('inflation_rate')}%")
        print(f"Unemployment: {indicators.get('unemployment_rate')}%, Fed Rate: {indicators.get('interest_rate')}%")
        print(f"VIX: {indicators.get('vix')}, Yield Spread: {indicators.get('yield_spread')}")
    if content.get("insights"):
        for insight in content["insights"][:3]:
            print(f"  → {insight}")
    if content.get("error"):
        print(f"⚠️  {content['error']}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n🌍 Test 3: Get macro indicators...")
result = mcp.call("tools/call", {"name":"get_macro_indicators","arguments":{}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Source: {content.get('source')}")
    for key in ["gdp_growth", "inflation_rate", "unemployment_rate", "interest_rate", "vix"]:
        val = content.get(key)
        print(f"  {key}: {val if val is not None else 'N/A'}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n🌍 Test 4: Get technology sector outlook...")
result = mcp.call("tools/call", {"name":"get_sector_outlook","arguments":{"sector":"technology"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Sector: {content.get('sector')}, Outlook: {content.get('sector_outlook')}")
    print(f"Confidence: {content.get('confidence')}, Source: {content.get('source')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n" + "="*80 + "\nMacro Server Testing Complete!\n" + "="*80)
