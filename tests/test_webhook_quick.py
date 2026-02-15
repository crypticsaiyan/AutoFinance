"""Quick test: send notifications to Discord and Slack"""
import requests, json

BASE_URL = "http://localhost:9013/mcp"
s = requests.Session()
sid = None
mid = 0

def call(method, params=None):
    global sid, mid
    mid += 1
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if sid: headers["mcp-session-id"] = sid
    r = s.post(BASE_URL, json={"jsonrpc":"2.0","id":mid,"method":method,"params":params or {}}, headers=headers)
    if "mcp-session-id" in r.headers: sid = r.headers["mcp-session-id"]
    for line in r.text.strip().split("\n"):
        if line.startswith("data: "): return json.loads(line[6:])

# Initialize
call("initialize", {"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}})

# Check status
print("=== Channel Status ===")
r = call("tools/call", {"name":"get_notification_status","arguments":{}})
content = json.loads(r["result"]["content"][0]["text"])
for name, info in content["channels"].items():
    icon = "✅" if info["available"] else "❌"
    print(f"  {icon} {name}: {info['details']}")

# Send to Discord
print("\n=== Testing Discord ===")
r = call("tools/call", {"name":"send_notification","arguments":{
    "message":"AAPL is up 3.2% today. Portfolio value: $127,450. All systems operational.",
    "channel":"discord","severity":"info","title":"AutoFinance Daily Update"
}})
content = json.loads(r["result"]["content"][0]["text"])
print(f"Discord: success={content.get('success')}, status={content.get('status_code','n/a')}")

# Send to Slack
print("\n=== Testing Slack ===")
r = call("tools/call", {"name":"send_notification","arguments":{
    "message":"TSLA dropped 5% in the last hour. Current price: $342.10",
    "channel":"slack","severity":"warning","title":"Price Alert: TSLA"
}})
content = json.loads(r["result"]["content"][0]["text"])
print(f"Slack: success={content.get('success')}, method={content.get('method','n/a')}")

# Send critical alert to ALL channels
print("\n=== Testing Broadcast Alert ===")
r = call("tools/call", {"name":"send_alert","arguments":{
    "title":"Portfolio Risk Alert",
    "message":"Position concentration in NVDA exceeds 30%. Consider rebalancing.",
    "severity":"critical"
}})
content = json.loads(r["result"]["content"][0]["text"])
print(f"Channels attempted: {content['channels_attempted']}, delivered: {content['channels_delivered']}")
for ch, result in content["results"].items():
    icon = "✅" if result.get("success") else "❌"
    print(f"  {icon} {ch}: {result}")

print("\n✅ Check your Discord and Slack for the messages!")
