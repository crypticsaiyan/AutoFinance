"""
AutoFinance Notification & Alerts Server

Unified notification system with self-monitoring price alerts.
- Send notifications: file, Discord, Slack, webhook, email
- Create price alerts that auto-monitor via market server
- Triggers send notifications automatically when conditions are met

Tools:
  Notifications:
  - send_notification: Send to a specific channel
  - send_alert: Broadcast formatted alert to all channels
  - send_multi_channel: Send to specific channel list
  - get_notification_history: View recent notifications
  - get_notification_status: Check channel availability

  Price Alerts:
  - create_price_alert: Set a price alert (auto-monitors)
  - list_price_alerts: View all alerts
  - delete_price_alert: Remove an alert
  - check_alerts_now: Manual one-shot price check
  - get_monitor_status: Check monitor thread status
  - start_monitor / stop_monitor: Control monitoring
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

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))


# Initialize MCP Server
mcp = FastMCP("auto-finance-notifications")

# ─── Configuration ───────────────────────────────────────────────────────────

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#autofinance")
WEBHOOK_URL = os.getenv("NOTIFICATION_WEBHOOK_URL", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")

# Market server for price checks
MARKET_URL = "http://localhost:9001/mcp"

# ─── Notification Log ────────────────────────────────────────────────────────

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "notifications.jsonl"
NOTIFICATION_HISTORY: List[Dict] = []
MAX_HISTORY = 200

# ─── Alert Storage ───────────────────────────────────────────────────────────

ALERTS_FILE = Path(__file__).parent / "alerts_data.json"
ACTIVE_ALERTS: Dict[str, Dict] = {}

# Monitor state
_monitor_thread: Optional[threading.Thread] = None
_monitor_running = False
_monitor_interval = 60
_monitor_log: List[Dict] = []
_MAX_LOG = 50


def _load_alerts():
    global ACTIVE_ALERTS
    if ALERTS_FILE.exists():
        try:
            with open(ALERTS_FILE, 'r') as f:
                ACTIVE_ALERTS = json.load(f)
        except json.JSONDecodeError:
            ACTIVE_ALERTS = {}


def _save_alerts():
    with open(ALERTS_FILE, 'w') as f:
        json.dump(ACTIVE_ALERTS, f, indent=2)


_load_alerts()


# ─── Notification Internals ──────────────────────────────────────────────────

def _log_notification(notification: Dict):
    NOTIFICATION_HISTORY.append(notification)
    if len(NOTIFICATION_HISTORY) > MAX_HISTORY:
        NOTIFICATION_HISTORY.pop(0)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(notification) + "\n")


def _send_file_log(message: str, severity: str = "info", title: str = "") -> Dict:
    icons = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}
    log_line = f"[{datetime.now().isoformat()}] {icons.get(severity, '📌')} [{severity.upper()}]"
    if title:
        log_line += f" {title}:"
    log_line += f" {message}\n"
    log_path = LOG_DIR / f"alerts_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_path, "a") as f:
        f.write(log_line)
    return {"success": True, "channel": "file", "log_path": str(log_path)}


def _send_discord(message: str, severity: str = "info", title: str = "") -> Dict:
    if not DISCORD_WEBHOOK_URL:
        return {"success": False, "channel": "discord", "error": "DISCORD_WEBHOOK_URL not configured"}
    colors = {"info": 3066993, "warning": 16776960, "critical": 15158332}
    icons = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}
    embed = {
        "title": f"{icons.get(severity, '📌')} {title}" if title else f"{icons.get(severity, '📌')} AutoFinance Alert",
        "description": message,
        "color": colors.get(severity, 3447003),
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "AutoFinance"}
    }
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
        return {"success": resp.status_code in [200, 204], "channel": "discord", "status_code": resp.status_code}
    except Exception as e:
        return {"success": False, "channel": "discord", "error": str(e)}


def _send_slack(message: str, severity: str = "info", title: str = "", channel: str = "") -> Dict:
    colors = {"info": "#36a64f", "warning": "#ff9900", "critical": "#ff0000"}
    icons = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}
    text = f"{icons.get(severity, '📌')} *{title}*\n{message}" if title else f"{icons.get(severity, '📌')} {message}"

    if SLACK_WEBHOOK_URL:
        try:
            resp = requests.post(SLACK_WEBHOOK_URL, json={
                "text": text,
                "attachments": [{"color": colors.get(severity, "#439FE0"), "text": message, "title": title}]
            }, timeout=10)
            return {"success": resp.status_code == 200, "channel": "slack", "method": "webhook"}
        except Exception as e:
            return {"success": False, "channel": "slack", "error": str(e)}

    if SLACK_BOT_TOKEN:
        try:
            resp = requests.post("https://slack.com/api/chat.postMessage", json={
                "channel": channel or SLACK_CHANNEL, "text": text,
                "attachments": [{"color": colors.get(severity, "#439FE0"), "text": message}]
            }, headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}, timeout=10)
            data = resp.json()
            return {"success": data.get("ok", False), "channel": "slack", "method": "bot_token"}
        except Exception as e:
            return {"success": False, "channel": "slack", "error": str(e)}

    return {"success": False, "channel": "slack", "error": "No Slack config"}


def _send_webhook(message: str, severity: str = "info", title: str = "") -> Dict:
    if not WEBHOOK_URL:
        return {"success": False, "channel": "webhook", "error": "NOTIFICATION_WEBHOOK_URL not configured"}
    try:
        resp = requests.post(WEBHOOK_URL, json={
            "text": message, "title": title, "severity": severity,
            "timestamp": datetime.now().isoformat(), "source": "AutoFinance"
        }, timeout=10)
        return {"success": resp.status_code < 400, "channel": "webhook", "status_code": resp.status_code}
    except Exception as e:
        return {"success": False, "channel": "webhook", "error": str(e)}


def _send_email(to_email: str, subject: str, body: str) -> Dict:
    if not SMTP_HOST or not SMTP_USER:
        return {"success": False, "channel": "email", "error": "SMTP not configured"}
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM or SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return {"success": True, "channel": "email", "to": to_email}
    except Exception as e:
        return {"success": False, "channel": "email", "error": str(e)}


def _broadcast(message: str, severity: str, title: str) -> Dict:
    """Send to all available channels."""
    results = {"file": _send_file_log(message, severity, title)}
    if DISCORD_WEBHOOK_URL:
        results["discord"] = _send_discord(message, severity, title)
    if SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN:
        results["slack"] = _send_slack(message, severity, title)
    if WEBHOOK_URL:
        results["webhook"] = _send_webhook(message, severity, title)
    return results


# ─── Market Client for Alert Monitoring ──────────────────────────────────────

class MCPCaller:
    def __init__(self, base_url):
        self.base_url, self.session, self.session_id, self.msg_id = base_url, requests.Session(), None, 0
        self._ready = False

    def _call(self, method, params=None):
        self.msg_id += 1
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        try:
            resp = self.session.post(self.base_url, json={
                "jsonrpc": "2.0", "id": self.msg_id, "method": method, "params": params or {}
            }, headers=headers, timeout=15)
            if "mcp-session-id" in resp.headers:
                self.session_id = resp.headers["mcp-session-id"]
            for line in resp.text.strip().split("\n"):
                if line.startswith("data: "):
                    return json.loads(line[6:])
        except Exception:
            pass
        return None

    def initialize(self):
        if not self._ready:
            r = self._call("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "notif-monitor", "version": "1.0"}})
            self._ready = r is not None
        return self._ready

    def call_tool(self, tool_name, arguments=None):
        result = self._call("tools/call", {"name": tool_name, "arguments": arguments or {}})
        if result and "result" in result:
            try:
                return json.loads(result["result"]["content"][0]["text"])
            except (KeyError, json.JSONDecodeError):
                pass
        return {"error": f"Failed to call {tool_name}"}


_market_client: Optional[MCPCaller] = None


def _get_market():
    global _market_client
    if _market_client is None:
        _market_client = MCPCaller(MARKET_URL)
        _market_client.initialize()
    return _market_client


# ─── Alert Monitor Thread ────────────────────────────────────────────────────

def _check_condition(condition, price, threshold, prev_price=None):
    if condition == "above" and price > threshold: return True
    if condition == "below" and price < threshold: return True
    if condition == "crosses_above" and prev_price and prev_price <= threshold < price: return True
    if condition == "crosses_below" and prev_price and prev_price >= threshold > price: return True
    return False


def _monitor_loop():
    global _monitor_running
    _monitor_running = True
    while _monitor_running:
        try:
            active = [a for a in ACTIVE_ALERTS.values() if not a.get("triggered")]
            if active:
                market = _get_market()
                symbols = set(a["symbol"] for a in active)
                prices = {}
                for sym in symbols:
                    r = market.call_tool("get_live_price", {"symbol": sym})
                    if "price" in r:
                        prices[sym] = r["price"]

                for alert in active:
                    sym = alert["symbol"]
                    if sym not in prices:
                        continue
                    price = prices[sym]
                    if _check_condition(alert["condition"], price, alert["threshold"], alert.get("last_price")):
                        alert["triggered"] = True
                        alert["triggered_at"] = datetime.now().isoformat()
                        alert["triggered_price"] = price
                        alert["trigger_count"] = alert.get("trigger_count", 0) + 1

                        title = f"🔔 {sym} Alert Triggered"
                        msg = f"**{sym}** is now **${price}**\nCondition: {alert['condition']} ${alert['threshold']}"
                        _broadcast(msg, "critical", title)
                        _log_notification({"timestamp": datetime.now().isoformat(), "message": msg, "title": title, "severity": "critical", "channel": "alert_trigger", "delivered": True})
                        _monitor_log.append({"time": datetime.now().isoformat(), "event": "triggered", "symbol": sym, "price": price})

                    alert["last_price"] = price
                    alert["last_checked"] = datetime.now().isoformat()

                _save_alerts()
                _monitor_log.append({"time": datetime.now().isoformat(), "event": "check", "alerts": len(active), "prices": len(prices)})
                if len(_monitor_log) > _MAX_LOG:
                    _monitor_log.pop(0)
        except Exception as e:
            _monitor_log.append({"time": datetime.now().isoformat(), "event": "error", "msg": str(e)})
        time.sleep(_monitor_interval)
    _monitor_running = False


def _ensure_monitor():
    global _monitor_thread, _monitor_running
    if not _monitor_running:
        _monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
        _monitor_thread.start()


# ═══════════════════════════════════════════════════════════════════════════════
# NOTIFICATION TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def send_notification(message: str, channel: str = "file", severity: str = "info", title: str = "") -> Dict[str, Any]:
    """
    Send a notification via a specific channel.

    Args:
        message: Notification message
        channel: 'file', 'discord', 'slack', 'webhook'
        severity: 'info', 'warning', or 'critical'
        title: Optional title
    """
    handlers = {
        "file": lambda: _send_file_log(message, severity, title),
        "discord": lambda: _send_discord(message, severity, title),
        "slack": lambda: _send_slack(message, severity, title),
        "webhook": lambda: _send_webhook(message, severity, title),
    }
    result = handlers.get(channel, lambda: {"success": False, "error": f"Unknown channel: {channel}"})()
    _log_notification({"timestamp": datetime.now().isoformat(), "message": message, "title": title, "severity": severity, "channel": channel, "delivered": result.get("success", False)})
    return result


@mcp.tool()
def send_alert(title: str, message: str, severity: str = "info") -> Dict[str, Any]:
    """
    Broadcast alert to ALL available channels.

    Args:
        title: Alert title
        message: Alert details
        severity: 'info', 'warning', or 'critical'
    """
    results = _broadcast(message, severity, title)
    _log_notification({"timestamp": datetime.now().isoformat(), "message": message, "title": title, "severity": severity, "channel": "broadcast", "delivered": any(r.get("success") for r in results.values())})
    return {
        "title": title, "severity": severity,
        "channels_attempted": len(results),
        "channels_delivered": sum(1 for r in results.values() if r.get("success")),
        "results": results, "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def send_multi_channel(message: str, channels: List[str], severity: str = "info", title: str = "", email_to: str = "", email_subject: str = "") -> Dict[str, Any]:
    """
    Send to specific channels.

    Args:
        message: Message text
        channels: List of channels ('file', 'discord', 'slack', 'webhook', 'email')
        severity: 'info', 'warning', or 'critical'
        title: Optional title
        email_to: Email recipient (required for email)
        email_subject: Email subject
    """
    results = {}
    for ch in channels:
        if ch == "file": results["file"] = _send_file_log(message, severity, title)
        elif ch == "discord": results["discord"] = _send_discord(message, severity, title)
        elif ch == "slack": results["slack"] = _send_slack(message, severity, title)
        elif ch == "webhook": results["webhook"] = _send_webhook(message, severity, title)
        elif ch == "email" and email_to:
            subj = email_subject or f"[AutoFinance {severity.upper()}] {title or 'Notification'}"
            results["email"] = _send_email(email_to, subj, message)
    _log_notification({"timestamp": datetime.now().isoformat(), "message": message, "title": title, "severity": severity, "channel": ",".join(channels), "delivered": any(r.get("success") for r in results.values())})
    return {"channels_attempted": len(results), "channels_delivered": sum(1 for r in results.values() if r.get("success")), "results": results}


@mcp.tool()
def get_notification_history(limit: int = 20) -> Dict[str, Any]:
    """Get recent notification history."""
    recent = NOTIFICATION_HISTORY[-limit:] if len(NOTIFICATION_HISTORY) > limit else NOTIFICATION_HISTORY
    return {"count": len(recent), "total_sent": len(NOTIFICATION_HISTORY), "notifications": list(reversed(recent)), "log_file": str(LOG_FILE)}


@mcp.tool()
def get_notification_status() -> Dict[str, Any]:
    """Check which channels are configured."""
    channels = {
        "file": {"available": True, "details": f"Logging to {LOG_DIR}"},
        "discord": {"available": bool(DISCORD_WEBHOOK_URL), "details": "Connected" if DISCORD_WEBHOOK_URL else "Set DISCORD_WEBHOOK_URL in .env"},
        "slack": {"available": bool(SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN), "details": ("Webhook" if SLACK_WEBHOOK_URL else f"Bot → {SLACK_CHANNEL}") if (SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN) else "Set SLACK_WEBHOOK_URL in .env"},
        "webhook": {"available": bool(WEBHOOK_URL), "details": f"URL configured" if WEBHOOK_URL else "Set NOTIFICATION_WEBHOOK_URL in .env"},
        "email": {"available": bool(SMTP_HOST and SMTP_USER), "details": f"SMTP: {SMTP_HOST}" if SMTP_HOST else "Set SMTP_HOST in .env"},
    }
    return {"channels": channels, "available_count": sum(1 for c in channels.values() if c["available"]), "total_sent": len(NOTIFICATION_HISTORY)}


# ═══════════════════════════════════════════════════════════════════════════════
# PRICE ALERT TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def create_price_alert(symbol: str, condition: str, threshold: float, user_id: str = "archestra") -> Dict[str, Any]:
    """
    Create a price alert. Monitoring starts automatically.

    Args:
        symbol: Trading symbol (e.g., 'AAPL', 'BTCUSDT', 'TSLA')
        condition: 'above', 'below', 'crosses_above', or 'crosses_below'
        threshold: Price to trigger at
        user_id: Who set the alert

    Examples:
        "Notify me when TSLA drops to 89" → condition="below", threshold=89
        "Alert when BTC hits 100k" → condition="above", threshold=100000
    """
    alert_id = f"{user_id}_{symbol}_{int(datetime.now().timestamp())}"
    ACTIVE_ALERTS[alert_id] = {
        "alert_id": alert_id, "user_id": user_id, "symbol": symbol,
        "condition": condition, "threshold": threshold,
        "created_at": datetime.now().isoformat(),
        "triggered": False, "trigger_count": 0, "last_checked": None, "last_price": None
    }
    _save_alerts()
    _ensure_monitor()

    active_count = sum(1 for a in ACTIVE_ALERTS.values() if not a.get("triggered"))
    return {
        "success": True, "alert_id": alert_id,
        "message": f"Alert set: notify when {symbol} is {condition} ${threshold}",
        "monitor_running": _monitor_running, "check_interval": f"{_monitor_interval}s",
        "total_active_alerts": active_count
    }


@mcp.tool()
def list_price_alerts(user_id: str = "", active_only: bool = True) -> Dict[str, Any]:
    """
    List price alerts.

    Args:
        user_id: Filter by user (empty = all)
        active_only: Only non-triggered alerts
    """
    alerts = list(ACTIVE_ALERTS.values())
    if user_id: alerts = [a for a in alerts if a["user_id"] == user_id]
    if active_only: alerts = [a for a in alerts if not a.get("triggered")]
    return {"total": len(alerts), "alerts": alerts, "monitor_running": _monitor_running}


@mcp.tool()
def delete_price_alert(alert_id: str) -> Dict[str, Any]:
    """Delete a price alert."""
    if alert_id not in ACTIVE_ALERTS:
        return {"error": f"Alert {alert_id} not found"}
    alert = ACTIVE_ALERTS.pop(alert_id)
    _save_alerts()
    return {"success": True, "message": f"Deleted: {alert['symbol']} {alert['condition']} ${alert['threshold']}", "remaining": sum(1 for a in ACTIVE_ALERTS.values() if not a.get("triggered"))}


@mcp.tool()
def check_alerts_now() -> Dict[str, Any]:
    """Manually check all alerts against live prices right now."""
    active = [a for a in ACTIVE_ALERTS.values() if not a.get("triggered")]
    if not active:
        return {"message": "No active alerts", "checked": 0}

    market = _get_market()
    symbols = set(a["symbol"] for a in active)
    prices = {}
    triggered_list = []

    for sym in symbols:
        r = market.call_tool("get_live_price", {"symbol": sym})
        if "price" in r: prices[sym] = r["price"]

    for alert in active:
        sym = alert["symbol"]
        if sym not in prices: continue
        price = prices[sym]
        if _check_condition(alert["condition"], price, alert["threshold"], alert.get("last_price")):
            alert["triggered"] = True
            alert["triggered_at"] = datetime.now().isoformat()
            alert["triggered_price"] = price
            alert["trigger_count"] = alert.get("trigger_count", 0) + 1
            title = f"🔔 {sym} Alert Triggered"
            msg = f"**{sym}** is now **${price}**\nCondition: {alert['condition']} ${alert['threshold']}"
            _broadcast(msg, "critical", title)
            triggered_list.append({"symbol": sym, "price": price, "condition": alert["condition"], "threshold": alert["threshold"]})
        alert["last_price"] = price
        alert["last_checked"] = datetime.now().isoformat()

    _save_alerts()
    return {"checked": len(active), "prices": prices, "triggered": triggered_list, "triggered_count": len(triggered_list)}


@mcp.tool()
def get_monitor_status() -> Dict[str, Any]:
    """Check alert monitor status."""
    return {
        "monitor_running": _monitor_running,
        "interval_seconds": _monitor_interval,
        "active_alerts": sum(1 for a in ACTIVE_ALERTS.values() if not a.get("triggered")),
        "triggered_alerts": sum(1 for a in ACTIVE_ALERTS.values() if a.get("triggered")),
        "recent_log": _monitor_log[-5:]
    }


@mcp.tool()
def start_monitor(interval: int = 60) -> Dict[str, Any]:
    """Start the background price monitor."""
    global _monitor_interval
    if _monitor_running:
        return {"message": "Already running", "interval": _monitor_interval}
    _monitor_interval = max(10, interval)
    _ensure_monitor()
    return {"success": True, "message": f"Monitor started ({_monitor_interval}s interval)"}


@mcp.tool()
def stop_monitor() -> Dict[str, Any]:
    """Stop the background price monitor."""
    global _monitor_running
    if not _monitor_running:
        return {"message": "Not running"}
    _monitor_running = False
    return {"success": True, "message": "Monitor stopped"}


if __name__ == "__main__":
    mcp.run()
