"""Test script for Notification & Alerts Server - Port: 9013"""
import requests, json

BASE_URL = "http://172.17.0.1:9013/mcp"

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

print("="*80 + "\nTesting Notification & Alerts Server (Port 9013)\n" + "="*80)
mcp = MCPSession(BASE_URL)

print("\n🔔 Test 1: Initialize...")
result = mcp.initialize()
if result:
    print(f"✅ Initialized: {result.get('result',{}).get('serverInfo',{}).get('name')}")
else:
    print("❌ FAILED"); exit(1)

# --- Notification Tests ---

print("\n📤 Test 2: Check notification status...")
result = mcp.call("tools/call", {"name":"get_notification_status","arguments":{}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Available channels: {content.get('available_count')}")
    for name, info in content.get("channels", {}).items():
        icon = "✅" if info.get("available") else "❌"
        print(f"  {icon} {name}: {info.get('details','')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📤 Test 3: Send file notification...")
result = mcp.call("tools/call", {"name":"send_notification","arguments":{
    "message":"Test notification from unified server","channel":"file","severity":"info","title":"Test"
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Delivered: {content.get('success')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n📤 Test 4: Send broadcast alert...")
result = mcp.call("tools/call", {"name":"send_alert","arguments":{
    "title":"Test Alert","message":"This is a test broadcast","severity":"warning"
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Channels attempted: {content.get('channels_attempted')}, delivered: {content.get('channels_delivered')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

# --- Price Alert Tests ---

print("\n🔔 Test 5: Create price alert (AAPL above $300)...")
result = mcp.call("tools/call", {"name":"create_price_alert","arguments":{
    "symbol":"AAPL","condition":"above","threshold":300.0,"user_id":"test"
}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    alert_id = content.get("alert_id")
    print(f"Alert: {content.get('message')}")
    print(f"Monitor: {content.get('monitor_running')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")
    alert_id = None

print("\n🔔 Test 6: List price alerts...")
result = mcp.call("tools/call", {"name":"list_price_alerts","arguments":{"user_id":"test"}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Total: {content.get('total')}")
    for a in content.get("alerts", []):
        print(f"  {a['symbol']}: {a['condition']} ${a['threshold']}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n🔔 Test 7: Manual check (check_alerts_now)...")
result = mcp.call("tools/call", {"name":"check_alerts_now","arguments":{}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Checked: {content.get('checked')} alerts")
    for sym, price in content.get("prices", {}).items():
        print(f"  {sym}: ${price}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n🔔 Test 8: Monitor status...")
result = mcp.call("tools/call", {"name":"get_monitor_status","arguments":{}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"Running: {content.get('monitor_running')}, Interval: {content.get('interval_seconds')}s")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

# Cleanup
if alert_id:
    print("\n🔔 Test 9: Delete alert...")
    result = mcp.call("tools/call", {"name":"delete_price_alert","arguments":{"alert_id":alert_id}})
    if result and "result" in result:
        content = json.loads(result["result"]["content"][0]["text"])
        print(f"Deleted: {content.get('message')}")
        print("✅ PASSED")
    else:
        print(f"❌ FAILED: {result}")

print("\n📤 Test 10: Notification history...")
result = mcp.call("tools/call", {"name":"get_notification_history","arguments":{"limit":5}})
if result and "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print(f"History: {content.get('count')} items, Total: {content.get('total_sent')}")
    print("✅ PASSED")
else:
    print(f"❌ FAILED: {result}")

print("\n" + "="*80 + "\nNotification & Alerts Server Testing Complete!\n" + "="*80)
