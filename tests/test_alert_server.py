"""Test script for Alert Engine Server (Self-Monitoring) - Port: 9011"""
import requests, json

BASE_URL = "http://172.17.0.1:9011/mcp"

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

print("="*80 + "\nTesting Alert Engine Server (Port 9011)\n" + "="*80)
mcp = MCPSession(BASE_URL)

print("\n🔔 Test 1: Initialize...")
result = mcp.initialize()
if result:
    print(f"✅ Initialized: {result.get('result',{}).get('serverInfo',{}).get('name')}")
else:
    print("❌ FAILED"); exit(1)

print("\n🔔 Test 2: Create alert (AAPL above $300)...")
result = mcp.call("tools/call", {"name":"create_alert","arguments":{
    "symbol":"AAPL","condition":"above","threshold":300.0,"user_id":"test_user"
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    alert_id = content.get("alert_id")
    print(f"Alert: {content.get('message')}")
    print(f"Monitor: {content.get('monitor')}")
    print(f"ID: {alert_id}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")
    alert_id = None

print("\n🔔 Test 3: Create alert (TSLA below $200)...")
result = mcp.call("tools/call", {"name":"create_alert","arguments":{
    "symbol":"TSLA","condition":"below","threshold":200.0,"user_id":"test_user"
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Alert: {content.get('message')}")
    print(f"Active alerts: {content.get('total_active_alerts')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n🔔 Test 4: List alerts...")
result = mcp.call("tools/call", {"name":"list_alerts","arguments":{"user_id":"test_user"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Total: {content.get('total')}, Monitor running: {content.get('monitor_running')}")
    for a in content.get("alerts", []):
        print(f"  {a['symbol']}: {a['condition']} ${a['threshold']}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n🔔 Test 5: Get monitor status...")
result = mcp.call("tools/call", {"name":"get_monitor_status","arguments":{}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Running: {content.get('monitor_running')}")
    print(f"Interval: {content.get('check_interval_seconds')}s")
    print(f"Active: {content.get('active_alerts')}, Triggered: {content.get('triggered_alerts')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n🔔 Test 6: Manual check (check_alerts_now)...")
result = mcp.call("tools/call", {"name":"check_alerts_now","arguments":{}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Checked: {content.get('checked')} alerts")
    prices = content.get("prices", {})
    for sym, price in prices.items():
        print(f"  {sym}: ${price}")
    triggered = content.get("triggered", [])
    if triggered:
        for t in triggered:
            print(f"  🚨 TRIGGERED: {t['symbol']} {t['condition']} ${t['threshold']} (now ${t['price']})")
    else:
        print("  No alerts triggered (conditions not met)")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

# Cleanup
if alert_id:
    print("\n🔔 Test 7: Delete alert...")
    result = mcp.call("tools/call", {"name":"delete_alert","arguments":{"alert_id":alert_id}})
    if result and "result" in result:
        content = json.loads(result["result"]["content"][0]["text"])
        print(f"Deleted: {content.get('message')}")
        print(f"Remaining: {content.get('remaining_alerts')}")
        print("✅ PASSED")
    else:
        print(f"❌ FAILED: {result}")

print("\n" + "="*80 + "\nAlert Engine Testing Complete!\n" + "="*80)
