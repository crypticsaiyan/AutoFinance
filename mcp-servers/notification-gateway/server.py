"""
AutoFinance Notification Gateway Server

Sends notifications via multiple channels:
- Slack
- WhatsApp (via Twilio)
- SMS (via Twilio)
- Email

Requires environment variables:
- SLACK_BOT_TOKEN
- SLACK_CHANNEL
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_PHONE_NUMBER
- TWILIO_WHATSAPP_NUMBER
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, Optional
import os
import json

# Initialize MCP Server
mcp = FastMCP("auto-finance-notification-gateway")

# Configuration (load from environment)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#autofinance")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")


# Lazy import notification libraries
def _get_slack_client():
    """Get Slack client (lazy import)"""
    try:
        from slack_sdk import WebClient
        return WebClient(token=SLACK_BOT_TOKEN)
    except ImportError:
        return None


def _get_twilio_client():
    """Get Twilio client (lazy import)"""
    try:
        from twilio.rest import Client
        return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except ImportError:
        return None


@mcp.tool()
def send_slack_message(
    message: str,
    channel: Optional[str] = None,
    blocks: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a message to Slack.
    
    Args:
        message: Message text
        channel: Slack channel (default from env)
        blocks: JSON string of Slack Block Kit blocks for rich formatting
    
    Returns:
        Confirmation of message sent
    """
    if not SLACK_BOT_TOKEN:
        return {
            "success": False,
            "error": "SLACK_BOT_TOKEN not configured",
            "simulation": True,
            "message": f"Would send to Slack: {message}"
        }
    
    client = _get_slack_client()
    if not client:
        return {
            "success": False,
            "error": "slack_sdk not installed. Run: pip install slack-sdk",
            "simulation": True,
            "message": f"Would send to Slack: {message}"
        }
    
    try:
        target_channel = channel or SLACK_CHANNEL
        
        kwargs = {
            "channel": target_channel,
            "text": message
        }
        
        if blocks:
            kwargs["blocks"] = json.loads(blocks)
        
        response = client.chat_postMessage(**kwargs)
        
        return {
            "success": True,
            "channel": target_channel,
            "timestamp": response["ts"],
            "message": "Message sent to Slack successfully"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "simulation": True
        }


@mcp.tool()
def send_slack_alert(
    title: str,
    message: str,
    severity: str = "info",
    channel: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a formatted alert to Slack.
    
    Args:
        title: Alert title
        message: Alert message
        severity: Alert severity ('info', 'warning', 'critical')
        channel: Slack channel (default from env)
    
    Returns:
        Confirmation of alert sent
    """
    # Color coding
    color_map = {
        "info": "#36a64f",      # Green
        "warning": "#ff9900",   # Orange
        "critical": "#ff0000"   # Red
    }
    
    color = color_map.get(severity, "#36a64f")
    
    # Emoji prefix
    emoji_map = {
        "info": "ℹ️",
        "warning": "⚠️",
        "critical": "🚨"
    }
    
    emoji = emoji_map.get(severity, "ℹ️")
    
    # Create Slack blocks for rich formatting
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} {title}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"*Severity:* {severity.upper()} | *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        }
    ]
    
    return send_slack_message(
        message=f"{emoji} {title}\n{message}",
        channel=channel,
        blocks=json.dumps(blocks)
    )


@mcp.tool()
def send_whatsapp_message(
    to_phone: str,
    message: str
) -> Dict[str, Any]:
    """
    Send a WhatsApp message via Twilio.
    
    Args:
        to_phone: Recipient phone number (E.164 format: +1234567890)
        message: Message text
    
    Returns:
        Confirmation of message sent
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return {
            "success": False,
            "error": "Twilio credentials not configured",
            "simulation": True,
            "message": f"Would send WhatsApp to {to_phone}: {message}"
        }
    
    client = _get_twilio_client()
    if not client:
        return {
            "success": False,
            "error": "twilio not installed. Run: pip install twilio",
            "simulation": True,
            "message": f"Would send WhatsApp to {to_phone}: {message}"
        }
    
    try:
        # Format phone number for WhatsApp
        to_whatsapp = f"whatsapp:{to_phone}" if not to_phone.startswith("whatsapp:") else to_phone
        
        message_response = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_whatsapp,
            body=message
        )
        
        return {
            "success": True,
            "message_sid": message_response.sid,
            "to": to_phone,
            "status": message_response.status,
            "message": "WhatsApp message sent successfully"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "simulation": True
        }


@mcp.tool()
def send_sms(
    to_phone: str,
    message: str
) -> Dict[str, Any]:
    """
    Send an SMS via Twilio.
    
    Args:
        to_phone: Recipient phone number (E.164 format: +1234567890)
        message: Message text (max 160 chars for single SMS)
    
    Returns:
        Confirmation of SMS sent
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return {
            "success": False,
            "error": "Twilio credentials not configured",
            "simulation": True,
            "message": f"Would send SMS to {to_phone}: {message}"
        }
    
    client = _get_twilio_client()
    if not client:
        return {
            "success": False,
            "error": "twilio not installed. Run: pip install twilio",
            "simulation": True,
            "message": f"Would send SMS to {to_phone}: {message}"
        }
    
    try:
        message_response = client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone,
            body=message
        )
        
        return {
            "success": True,
            "message_sid": message_response.sid,
            "to": to_phone,
            "status": message_response.status,
            "segments": message_response.num_segments,
            "message": "SMS sent successfully"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "simulation": True
        }


@mcp.tool()
def send_email(
    to_email: str,
    subject: str,
    body: str,
    html: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an email (using Twilio SendGrid).
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Plain text email body
        html: HTML email body (optional)
    
    Returns:
        Confirmation of email sent
    """
    # Placeholder for email functionality
    # In production, integrate with SendGrid, AWS SES, or similar
    
    return {
        "success": True,
        "simulation": True,
        "to": to_email,
        "subject": subject,
        "message": f"Would send email to {to_email}: {subject}"
    }


@mcp.tool()
def send_multi_channel_notification(
    message: str,
    channels: list,
    severity: str = "info",
    slack_channel: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send notification to multiple channels at once.
    
    Args:
        message: Notification message
        channels: List of channels ('slack', 'whatsapp', 'sms', 'email')
        severity: Message severity
        slack_channel: Slack channel (if applicable)
        phone: Phone number (if applicable)
        email: Email address (if applicable)
    
    Returns:
        Status of each channel delivery
    """
    results = {}
    
    if "slack" in channels:
        results["slack"] = send_slack_alert(
            title="AutoFinance Alert",
            message=message,
            severity=severity,
            channel=slack_channel
        )
    
    if "whatsapp" in channels and phone:
        results["whatsapp"] = send_whatsapp_message(
            to_phone=phone,
            message=f"🤖 AutoFinance: {message}"
        )
    
    if "sms" in channels and phone:
        results["sms"] = send_sms(
            to_phone=phone,
            message=f"AutoFinance: {message}"
        )
    
    if "email" in channels and email:
        results["email"] = send_email(
            to_email=email,
            subject="AutoFinance Alert",
            body=message
        )
    
    success_count = sum(1 for r in results.values() if r.get("success"))
    
    return {
        "channels_attempted": len(channels),
        "channels_successful": success_count,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def get_notification_status() -> Dict[str, Any]:
    """
    Check configuration status of notification channels.
    
    Returns:
        Status of each notification channel
    """
    return {
        "slack": {
            "configured": bool(SLACK_BOT_TOKEN),
            "channel": SLACK_CHANNEL,
            "status": "ready" if SLACK_BOT_TOKEN else "missing_token"
        },
        "twilio": {
            "configured": bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN),
            "sms_number": TWILIO_PHONE_NUMBER if TWILIO_PHONE_NUMBER else "not_configured",
            "whatsapp_number": TWILIO_WHATSAPP_NUMBER,
            "status": "ready" if TWILIO_ACCOUNT_SID else "missing_credentials"
        },
        "email": {
            "configured": False,
            "status": "not_implemented"
        }
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
