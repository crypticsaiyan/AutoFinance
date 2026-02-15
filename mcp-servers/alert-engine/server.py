"""
AutoFinance Alert Engine Server

Manages price alerts and monitoring rules.
Users can set alerts like "notify me when BTC > $50k"
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import os
from pathlib import Path

# Initialize MCP Server
mcp = FastMCP("auto-finance-alert-engine")

# Alert storage (in production, use a real database)
ALERTS_FILE = Path(__file__).parent / "alerts_data.json"
ACTIVE_ALERTS: Dict[str, Dict] = {}


def _load_alerts():
    """Load alerts from file"""
    global ACTIVE_ALERTS
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE, 'r') as f:
            ACTIVE_ALERTS = json.load(f)


def _save_alerts():
    """Save alerts to file"""
    with open(ALERTS_FILE, 'w') as f:
        json.dump(ACTIVE_ALERTS, f, indent=2)


# Load alerts on startup
_load_alerts()


@mcp.tool()
def create_alert(
    user_id: str,
    symbol: str,
    condition: str,
    threshold: float,
    channel: str = "slack",
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new price alert.
    
    Args:
        user_id: User identifier
        symbol: Trading symbol (e.g., 'AAPL', 'BTC-USD')
        condition: Condition type ('above', 'below', 'crosses_above', 'crosses_below')
        threshold: Price threshold
        channel: Notification channel ('slack', 'whatsapp', 'sms', 'email')
        message: Custom message template
    
    Returns:
        Dictionary with alert_id and confirmation
    """
    alert_id = f"{user_id}_{symbol}_{datetime.now().timestamp()}"
    
    alert_data = {
        "alert_id": alert_id,
        "user_id": user_id,
        "symbol": symbol,
        "condition": condition,
        "threshold": threshold,
        "channel": channel,
        "message": message or f"{symbol} has {condition} {threshold}",
        "created_at": datetime.now().isoformat(),
        "triggered": False,
        "last_checked": None,
        "trigger_count": 0
    }
    
    ACTIVE_ALERTS[alert_id] = alert_data
    _save_alerts()
    
    return {
        "success": True,
        "alert_id": alert_id,
        "message": f"Alert created: {symbol} {condition} {threshold}. Will notify via {channel}.",
        "alert_data": alert_data
    }


@mcp.tool()
def check_alert_condition(
    alert_id: str,
    current_price: float,
    previous_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Check if an alert condition is triggered.
    
    Args:
        alert_id: Alert identifier
        current_price: Current market price
        previous_price: Previous price (for crossing conditions)
    
    Returns:
        Dictionary with triggered status and details
    """
    if alert_id not in ACTIVE_ALERTS:
        return {"error": f"Alert {alert_id} not found"}
    
    alert = ACTIVE_ALERTS[alert_id]
    threshold = alert["threshold"]
    condition = alert["condition"]
    
    triggered = False
    
    if condition == "above" and current_price > threshold:
        triggered = True
    elif condition == "below" and current_price < threshold:
        triggered = True
    elif condition == "crosses_above" and previous_price:
        if previous_price <= threshold < current_price:
            triggered = True
    elif condition == "crosses_below" and previous_price:
        if previous_price >= threshold > current_price:
            triggered = True
    
    if triggered:
        alert["triggered"] = True
        alert["trigger_count"] += 1
        alert["last_triggered"] = datetime.now().isoformat()
        _save_alerts()
    
    alert["last_checked"] = datetime.now().isoformat()
    _save_alerts()
    
    return {
        "alert_id": alert_id,
        "triggered": triggered,
        "current_price": current_price,
        "threshold": threshold,
        "condition": condition,
        "message": alert["message"],
        "channel": alert["channel"],
        "user_id": alert["user_id"]
    }


@mcp.tool()
def list_user_alerts(user_id: str, active_only: bool = True) -> Dict[str, Any]:
    """
    List all alerts for a user.
    
    Args:
        user_id: User identifier
        active_only: If True, only return non-triggered alerts
    
    Returns:
        List of alerts for the user
    """
    user_alerts = []
    
    for alert_id, alert in ACTIVE_ALERTS.items():
        if alert["user_id"] == user_id:
            if not active_only or not alert["triggered"]:
                user_alerts.append(alert)
    
    return {
        "user_id": user_id,
        "alert_count": len(user_alerts),
        "alerts": user_alerts
    }


@mcp.tool()
def delete_alert(alert_id: str) -> Dict[str, Any]:
    """
    Delete an alert.
    
    Args:
        alert_id: Alert identifier
    
    Returns:
        Confirmation of deletion
    """
    if alert_id not in ACTIVE_ALERTS:
        return {"error": f"Alert {alert_id} not found"}
    
    alert = ACTIVE_ALERTS.pop(alert_id)
    _save_alerts()
    
    return {
        "success": True,
        "message": f"Deleted alert for {alert['symbol']}",
        "alert_id": alert_id
    }


@mcp.tool()
def get_all_active_alerts() -> Dict[str, Any]:
    """
    Get all active (non-triggered) alerts for monitoring.
    
    Returns:
        List of all active alerts across all users
    """
    active = [
        alert for alert in ACTIVE_ALERTS.values()
        if not alert["triggered"]
    ]
    
    return {
        "total_alerts": len(ACTIVE_ALERTS),
        "active_alerts": len(active),
        "alerts": active
    }


@mcp.tool()
def reset_alert(alert_id: str) -> Dict[str, Any]:
    """
    Reset a triggered alert so it can fire again.
    
    Args:
        alert_id: Alert identifier
    
    Returns:
        Confirmation of reset
    """
    if alert_id not in ACTIVE_ALERTS:
        return {"error": f"Alert {alert_id} not found"}
    
    ACTIVE_ALERTS[alert_id]["triggered"] = False
    _save_alerts()
    
    return {
        "success": True,
        "message": f"Alert {alert_id} reset",
        "alert_id": alert_id
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
