"""
AutoFinance Alert Engine Server

Self-monitoring price alert system with built-in polling.
When you create an alert, the server automatically:
1. Checks live prices periodically (via market server)
2. Triggers when conditions are met
3. Sends notifications (via notification gateway)

No external scripts needed — Archestra just calls create_alert.

Tools:
- create_alert: Set a price alert (monitoring starts automatically)
- list_alerts: View all alerts
- delete_alert: Remove an alert
- get_monitor_status: Check if the monitor is running
- start_monitor: Start/restart price monitoring
- stop_monitor: Pause monitoring
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import os
import threading
import time
from pathlib import Path

try:
    import requests
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


# Initialize MCP Server
mcp = FastMCP("auto-finance-alert-engine")

# Alert storage
ALERTS_FILE = Path(__file__).parent / "alerts_data.json"
ACTIVE_ALERTS: Dict[str, Dict] = {}

# Monitor state
_monitor_thread: Optional[threading.Thread] = None
_monitor_running = False
_monitor_interval = 60  # seconds
_monitor_log: List[Dict] = []
_MAX_LOG = 50

# Server URLs (same host, different ports)
MARKET_URL = "http://localhost:9001/mcp"
NOTIFICATION_URL = "http://localhost:9013/mcp"


def _load_alerts():
    """Load alerts from file."""
    global ACTIVE_ALERTS
    if ALERTS_FILE.exists():
        try:
            with open(ALERTS_FILE, 'r') as f:
                ACTIVE_ALERTS = json.load(f)
        except json.JSONDecodeError:
            ACTIVE_ALERTS = {}


def _save_alerts():
    """Save alerts to file."""
    with open(ALERTS_FILE, 'w') as f:
        json.dump(ACTIVE_ALERTS, f, indent=2)


class MCPCaller:
    """Lightweight MCP client for server-to-server calls."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = None
        self.msg_id = 0

    def _call(self, method, params=None):
        self.msg_id += 1
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        try:
            resp = self.session.post(
                self.base_url,
                json={"jsonrpc": "2.0", "id": self.msg_id, "method": method, "params": params or {}},
                headers=headers,
                timeout=15
            )
            if "mcp-session-id" in resp.headers:
                self.session_id = resp.headers["mcp-session-id"]
            for line in resp.text.strip().split("\n"):
                if line.startswith("data: "):
                    return json.loads(line[6:])
        except Exception:
            return None
        return None

    def initialize(self):
        return self._call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "alert-engine-monitor", "version": "1.0"}
        })

    def call_tool(self, tool_name: str, arguments: dict = None) -> dict:
        result = self._call("tools/call", {"name": tool_name, "arguments": arguments or {}})
        if result and "result" in result:
            try:
                return json.loads(result["result"]["content"][0]["text"])
            except (KeyError, json.JSONDecodeError):
                pass
        return {"error": f"Failed to call {tool_name}"}


# Server clients (initialized lazily)
_market_client: Optional[MCPCaller] = None
_notif_client: Optional[MCPCaller] = None


def _get_market_client():
    global _market_client
    if _market_client is None:
        _market_client = MCPCaller(MARKET_URL)
        _market_client.initialize()
    return _market_client


def _get_notif_client():
    global _notif_client
    if _notif_client is None:
        _notif_client = MCPCaller(NOTIFICATION_URL)
        _notif_client.initialize()
    return _notif_client


def _check_condition(condition: str, current_price: float, threshold: float, previous_price: float = None) -> bool:
    """Check if an alert condition is met."""
    if condition == "above" and current_price > threshold:
        return True
    if condition == "below" and current_price < threshold:
        return True
    if condition == "crosses_above" and previous_price and previous_price <= threshold < current_price:
        return True
    if condition == "crosses_below" and previous_price and previous_price >= threshold > current_price:
        return True
    return False


def _monitor_loop():
    """Background thread that monitors prices and triggers alerts."""
    global _monitor_running
    _monitor_running = True

    while _monitor_running:
        try:
            active_alerts = [a for a in ACTIVE_ALERTS.values() if not a.get("triggered")]

            if active_alerts:
                market = _get_market_client()
                notif = _get_notif_client()

                # Get unique symbols
                symbols = set(a["symbol"] for a in active_alerts)
                prices = {}

                for symbol in symbols:
                    result = market.call_tool("get_live_price", {"symbol": symbol})
                    if "price" in result:
                        prices[symbol] = result["price"]

                # Check each alert
                for alert in active_alerts:
                    symbol = alert["symbol"]
                    if symbol not in prices:
                        continue

                    current_price = prices[symbol]
                    previous_price = alert.get("last_price")

                    if _check_condition(alert["condition"], current_price, alert["threshold"], previous_price):
                        # TRIGGERED!
                        alert["triggered"] = True
                        alert["triggered_at"] = datetime.now().isoformat()
                        alert["triggered_price"] = current_price
                        alert["trigger_count"] = alert.get("trigger_count", 0) + 1
                        _save_alerts()

                        # Send notification
                        title = f"🔔 {symbol} Alert Triggered"
                        message = (
                            f"**{symbol}** is now **${current_price}**\n"
                            f"Condition: {alert['condition']} ${alert['threshold']}\n"
                            f"Alert set by: {alert.get('user_id', 'system')}"
                        )

                        notif.call_tool("send_alert", {
                            "title": title,
                            "message": message,
                            "severity": "critical"
                        })

                        _monitor_log.append({
                            "time": datetime.now().isoformat(),
                            "event": "triggered",
                            "symbol": symbol,
                            "price": current_price,
                            "condition": f"{alert['condition']} {alert['threshold']}"
                        })

                    # Save last known price for crossing detection
                    alert["last_price"] = current_price
                    alert["last_checked"] = datetime.now().isoformat()

                _save_alerts()

                _monitor_log.append({
                    "time": datetime.now().isoformat(),
                    "event": "check",
                    "alerts_checked": len(active_alerts),
                    "prices_fetched": len(prices)
                })
                if len(_monitor_log) > _MAX_LOG:
                    _monitor_log.pop(0)

        except Exception as e:
            _monitor_log.append({
                "time": datetime.now().isoformat(),
                "event": "error",
                "message": str(e)
            })

        time.sleep(_monitor_interval)

    _monitor_running = False


# Load alerts on startup
_load_alerts()


@mcp.tool()
def create_alert(
    symbol: str,
    condition: str,
    threshold: float,
    user_id: str = "archestra",
    channel: str = "discord"
) -> Dict[str, Any]:
    """
    Create a price alert. Monitoring starts automatically.

    Args:
        symbol: Trading symbol (e.g., 'AAPL', 'BTCUSDT', 'TSLA')
        condition: 'above', 'below', 'crosses_above', or 'crosses_below'
        threshold: Price threshold to trigger alert
        user_id: Who set the alert (default: archestra)
        channel: Notification channel (default: discord)

    Returns:
        Confirmation with alert_id

    Examples:
        "Notify me when TSLA drops to 89" → condition="below", threshold=89
        "Alert when BTC goes above 100000" → condition="above", threshold=100000
    """
    alert_id = f"{user_id}_{symbol}_{int(datetime.now().timestamp())}"

    ACTIVE_ALERTS[alert_id] = {
        "alert_id": alert_id,
        "user_id": user_id,
        "symbol": symbol,
        "condition": condition,
        "threshold": threshold,
        "channel": channel,
        "created_at": datetime.now().isoformat(),
        "triggered": False,
        "trigger_count": 0,
        "last_checked": None,
        "last_price": None
    }
    _save_alerts()

    # Auto-start monitor if not running
    global _monitor_thread, _monitor_running
    if not _monitor_running:
        _monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
        _monitor_thread.start()
        monitor_status = "Monitor started automatically"
    else:
        monitor_status = "Monitor already running"

    return {
        "success": True,
        "alert_id": alert_id,
        "message": f"Alert created: notify when {symbol} is {condition} ${threshold}",
        "monitor": monitor_status,
        "check_interval": f"{_monitor_interval}s",
        "total_active_alerts": sum(1 for a in ACTIVE_ALERTS.values() if not a.get("triggered"))
    }


@mcp.tool()
def list_alerts(user_id: str = "", active_only: bool = True) -> Dict[str, Any]:
    """
    List all alerts.

    Args:
        user_id: Filter by user (empty = all users)
        active_only: Only show non-triggered alerts
    """
    alerts = list(ACTIVE_ALERTS.values())

    if user_id:
        alerts = [a for a in alerts if a["user_id"] == user_id]
    if active_only:
        alerts = [a for a in alerts if not a.get("triggered")]

    return {
        "total": len(alerts),
        "alerts": alerts,
        "monitor_running": _monitor_running
    }


@mcp.tool()
def delete_alert(alert_id: str) -> Dict[str, Any]:
    """
    Delete an alert.

    Args:
        alert_id: Alert ID to delete
    """
    if alert_id not in ACTIVE_ALERTS:
        return {"error": f"Alert {alert_id} not found"}

    alert = ACTIVE_ALERTS.pop(alert_id)
    _save_alerts()

    return {
        "success": True,
        "message": f"Deleted alert for {alert['symbol']} ({alert['condition']} ${alert['threshold']})",
        "remaining_alerts": sum(1 for a in ACTIVE_ALERTS.values() if not a.get("triggered"))
    }


@mcp.tool()
def get_monitor_status() -> Dict[str, Any]:
    """
    Check the status of the price monitoring background thread.
    """
    active_count = sum(1 for a in ACTIVE_ALERTS.values() if not a.get("triggered"))
    triggered_count = sum(1 for a in ACTIVE_ALERTS.values() if a.get("triggered"))

    return {
        "monitor_running": _monitor_running,
        "check_interval_seconds": _monitor_interval,
        "active_alerts": active_count,
        "triggered_alerts": triggered_count,
        "total_alerts": len(ACTIVE_ALERTS),
        "recent_log": _monitor_log[-5:],
        "market_server": MARKET_URL,
        "notification_server": NOTIFICATION_URL,
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def start_monitor(interval: int = 60) -> Dict[str, Any]:
    """
    Start or restart the price monitoring thread.

    Args:
        interval: Check interval in seconds (default: 60)
    """
    global _monitor_thread, _monitor_running, _monitor_interval

    if _monitor_running:
        return {
            "message": "Monitor is already running",
            "interval": _monitor_interval,
            "active_alerts": sum(1 for a in ACTIVE_ALERTS.values() if not a.get("triggered"))
        }

    _monitor_interval = max(10, interval)  # Minimum 10 seconds
    _monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
    _monitor_thread.start()

    return {
        "success": True,
        "message": f"Monitor started, checking every {_monitor_interval}s",
        "active_alerts": sum(1 for a in ACTIVE_ALERTS.values() if not a.get("triggered"))
    }


@mcp.tool()
def stop_monitor() -> Dict[str, Any]:
    """
    Stop the price monitoring thread.
    """
    global _monitor_running

    if not _monitor_running:
        return {"message": "Monitor is not running"}

    _monitor_running = False

    return {
        "success": True,
        "message": "Monitor stopped. Alerts are saved but no longer being checked.",
        "active_alerts": sum(1 for a in ACTIVE_ALERTS.values() if not a.get("triggered"))
    }


@mcp.tool()
def check_alerts_now() -> Dict[str, Any]:
    """
    Manually trigger an immediate alert check (doesn't need monitor running).
    Fetches live prices and checks all active alerts right now.
    """
    active = [a for a in ACTIVE_ALERTS.values() if not a.get("triggered")]

    if not active:
        return {"message": "No active alerts to check", "checked": 0}

    market = _get_market_client()
    notif = _get_notif_client()

    symbols = set(a["symbol"] for a in active)
    prices = {}
    triggered_list = []

    for symbol in symbols:
        result = market.call_tool("get_live_price", {"symbol": symbol})
        if "price" in result:
            prices[symbol] = result["price"]

    for alert in active:
        symbol = alert["symbol"]
        if symbol not in prices:
            continue

        current_price = prices[symbol]

        if _check_condition(alert["condition"], current_price, alert["threshold"], alert.get("last_price")):
            alert["triggered"] = True
            alert["triggered_at"] = datetime.now().isoformat()
            alert["triggered_price"] = current_price
            alert["trigger_count"] = alert.get("trigger_count", 0) + 1

            notif.call_tool("send_alert", {
                "title": f"🔔 {symbol} Alert Triggered",
                "message": f"**{symbol}** is now **${current_price}**\nCondition: {alert['condition']} ${alert['threshold']}",
                "severity": "critical"
            })

            triggered_list.append({"symbol": symbol, "price": current_price, "condition": alert["condition"], "threshold": alert["threshold"]})

        alert["last_price"] = current_price
        alert["last_checked"] = datetime.now().isoformat()

    _save_alerts()

    return {
        "checked": len(active),
        "prices": prices,
        "triggered": triggered_list,
        "triggered_count": len(triggered_list),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    mcp.run()
