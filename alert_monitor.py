"""
AutoFinance Alert Monitor

Runs as a background daemon that:
1. Loads active alerts from the Alert Engine
2. Fetches live prices from the Market Server
3. Checks if any alert conditions are met
4. Sends notifications via the Notification Gateway when triggered

Usage:
    python alert_monitor.py                    # Check every 60 seconds
    python alert_monitor.py --interval 30      # Check every 30 seconds
    python alert_monitor.py --once             # Check once and exit
"""

import requests
import json
import time
import argparse
import sys
from datetime import datetime


class MCPClient:
    """Simple MCP client for calling server tools."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = None
        self.message_id = 0
        self._initialized = False

    def _parse_sse(self, response):
        if 'mcp-session-id' in response.headers:
            self.session_id = response.headers['mcp-session-id']
        for line in response.text.strip().split('\n'):
            if line.startswith('data: '):
                return json.loads(line[6:])
        return None

    def _call(self, method, params=None):
        self.message_id += 1
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        try:
            resp = self.session.post(
                self.base_url,
                json={"jsonrpc": "2.0", "id": self.message_id, "method": method, "params": params or {}},
                headers=headers,
                timeout=15
            )
            return self._parse_sse(resp)
        except Exception as e:
            return None

    def initialize(self):
        if not self._initialized:
            result = self._call("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "alert-monitor", "version": "1.0"}
            })
            self._initialized = result is not None
        return self._initialized

    def call_tool(self, tool_name: str, arguments: dict = None) -> dict:
        if not self._initialized:
            self.initialize()
        result = self._call("tools/call", {"name": tool_name, "arguments": arguments or {}})
        if result and "result" in result:
            return json.loads(result["result"]["content"][0]["text"])
        return {"error": f"Failed to call {tool_name}"}


# Server connections
MARKET_URL = "http://localhost:9001/mcp"
ALERT_URL = "http://localhost:9011/mcp"
NOTIFICATION_URL = "http://localhost:9013/mcp"


def check_alerts(market: MCPClient, alerts: MCPClient, notifications: MCPClient, verbose: bool = True):
    """Check all active alerts against live prices."""
    # Get active alerts
    active = alerts.call_tool("get_all_active_alerts")

    if "error" in active:
        print(f"  ❌ Could not fetch alerts: {active['error']}")
        return 0

    alert_list = active.get("alerts", [])
    if not alert_list:
        if verbose:
            print(f"  📭 No active alerts")
        return 0

    if verbose:
        print(f"  📋 Checking {len(alert_list)} active alerts...")

    triggered_count = 0
    # Group by symbol to minimize API calls
    symbols = set(a["symbol"] for a in alert_list)
    prices = {}

    for symbol in symbols:
        price_data = market.call_tool("get_live_price", {"symbol": symbol})
        if "price" in price_data:
            prices[symbol] = price_data["price"]
            if verbose:
                print(f"  📊 {symbol}: ${price_data['price']}")

    # Check each alert
    for alert in alert_list:
        symbol = alert["symbol"]
        if symbol not in prices:
            continue

        current_price = prices[symbol]
        result = alerts.call_tool("check_alert_condition", {
            "alert_id": alert["alert_id"],
            "current_price": current_price
        })

        if result.get("triggered"):
            triggered_count += 1
            channel = alert.get("channel", "discord")
            severity = "critical"
            title = f"🔔 Alert Triggered: {symbol}"
            message = (
                f"{alert['condition'].upper()} ${alert['threshold']}\n"
                f"Current price: ${current_price}\n"
                f"Alert set by: {alert.get('user_id', 'unknown')}"
            )

            print(f"  🚨 TRIGGERED: {symbol} {alert['condition']} ${alert['threshold']} (now ${current_price})")

            # Send notification
            notif_result = notifications.call_tool("send_alert", {
                "title": title,
                "message": message,
                "severity": severity
            })
            delivered = notif_result.get("channels_delivered", 0)
            print(f"  📤 Notification sent to {delivered} channel(s)")

    return triggered_count


def main():
    parser = argparse.ArgumentParser(description="AutoFinance Alert Monitor")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds (default: 60)")
    parser.add_argument("--once", action="store_true", help="Check once and exit")
    args = parser.parse_args()

    print("=" * 60)
    print("AutoFinance Alert Monitor")
    print("=" * 60)

    # Connect to servers
    print("\n🔌 Connecting to servers...")
    market = MCPClient(MARKET_URL)
    alert_engine = MCPClient(ALERT_URL)
    notifier = MCPClient(NOTIFICATION_URL)

    for name, client in [("Market", market), ("Alert Engine", alert_engine), ("Notifications", notifier)]:
        if client.initialize():
            print(f"  ✅ {name}: connected")
        else:
            print(f"  ❌ {name}: FAILED - is it running?")
            sys.exit(1)

    if args.once:
        print(f"\n🔍 Checking alerts (one-time)...")
        triggered = check_alerts(market, alert_engine, notifier)
        print(f"\n{'🚨' if triggered else '✅'} {triggered} alert(s) triggered")
        return

    print(f"\n🔄 Monitoring every {args.interval}s (Ctrl+C to stop)\n")

    try:
        while True:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] Checking alerts...")
            triggered = check_alerts(market, alert_engine, notifier, verbose=True)
            if triggered:
                print(f"  🚨 {triggered} alert(s) triggered!")
            print()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n\n🛑 Alert monitor stopped")


if __name__ == "__main__":
    main()
