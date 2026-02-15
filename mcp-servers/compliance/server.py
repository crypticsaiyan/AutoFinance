"""
AutoFinance Compliance Server

Structured audit logging and compliance tracking.
- Logs every proposal
- Logs every risk decision
- Logs every execution result
- Generates audit reports

Tools:
- log_event: Log a compliance event
- generate_audit_report: Generate compliance audit report
- get_recent_events: Get recent audit events
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, Optional, Literal
import copy


# Initialize MCP Server
mcp = FastMCP("auto-finance-compliance")


# Audit Log (in-memory for demo)
AUDIT_LOG = []


@mcp.tool()
def log_event(
    event_type: Literal["proposal", "risk_decision", "execution", "error", "system"],
    agent_name: str,
    action: str,
    details: Dict[str, Any],
    severity: Literal["info", "warning", "critical"] = "info"
) -> Dict[str, Any]:
    """
    Log a compliance event to the audit trail.
    
    Args:
        event_type: Type of event
        agent_name: Name of the agent/server generating the event
        action: Action being performed
        details: Event-specific details
        severity: Event severity level
    """
    event = {
        "event_id": f"EVT_{len(AUDIT_LOG) + 1:06d}",
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "agent_name": agent_name,
        "action": action,
        "details": details,
        "severity": severity
    }
    
    AUDIT_LOG.append(event)
    
    return {
        "success": True,
        "event_id": event["event_id"],
        "logged_at": event["timestamp"],
        "total_events": len(AUDIT_LOG)
    }


@mcp.tool()
def generate_audit_report(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    event_type: Optional[str] = None,
    agent_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a compliance audit report.
    
    Filters events by time range, type, and agent.
    Returns summary statistics and detailed events.
    """
    filtered_events = AUDIT_LOG.copy()
    
    # Apply filters
    if start_time:
        filtered_events = [e for e in filtered_events if e["timestamp"] >= start_time]
    
    if end_time:
        filtered_events = [e for e in filtered_events if e["timestamp"] <= end_time]
    
    if event_type:
        filtered_events = [e for e in filtered_events if e["event_type"] == event_type]
    
    if agent_name:
        filtered_events = [e for e in filtered_events if e["agent_name"] == agent_name]
    
    # Calculate statistics
    event_types_count = {}
    agents_count = {}
    severity_count = {}
    
    for event in filtered_events:
        # Count by type
        event_types_count[event["event_type"]] = event_types_count.get(event["event_type"], 0) + 1
        
        # Count by agent
        agents_count[event["agent_name"]] = agents_count.get(event["agent_name"], 0) + 1
        
        # Count by severity
        severity_count[event["severity"]] = severity_count.get(event["severity"], 0) + 1
    
    # Count approvals vs rejections in risk decisions
    approvals = 0
    rejections = 0
    for event in filtered_events:
        if event["event_type"] == "risk_decision":
            if event["details"].get("approved"):
                approvals += 1
            else:
                rejections += 1
    
    return {
        "report_id": f"RPT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "generated_at": datetime.utcnow().isoformat(),
        "filters": {
            "start_time": start_time,
            "end_time": end_time,
            "event_type": event_type,
            "agent_name": agent_name
        },
        "summary": {
            "total_events": len(filtered_events),
            "by_type": event_types_count,
            "by_agent": agents_count,
            "by_severity": severity_count,
            "risk_decisions": {
                "approved": approvals,
                "rejected": rejections,
                "approval_rate": approvals / (approvals + rejections) if (approvals + rejections) > 0 else 0
            }
        },
        "events": filtered_events[-50:]  # Last 50 events for readability
    }


@mcp.tool()
def get_recent_events(limit: int = 20, event_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get most recent audit events.
    
    Args:
        limit: Maximum number of events to return
        event_type: Optional filter by event type
    """
    filtered_events = AUDIT_LOG
    
    if event_type:
        filtered_events = [e for e in filtered_events if e["event_type"] == event_type]
    
    recent = filtered_events[-limit:] if len(filtered_events) > limit else filtered_events
    
    return {
        "count": len(recent),
        "total_events": len(AUDIT_LOG),
        "events": recent
    }


@mcp.tool()
def get_compliance_metrics() -> Dict[str, Any]:
    """
    Get key compliance metrics and KPIs.
    """
    if not AUDIT_LOG:
        return {
            "total_events": 0,
            "message": "No audit events recorded yet"
        }
    
    # Calculate metrics
    total_events = len(AUDIT_LOG)
    
    # Count by type
    proposals = len([e for e in AUDIT_LOG if e["event_type"] == "proposal"])
    risk_decisions = len([e for e in AUDIT_LOG if e["event_type"] == "risk_decision"])
    executions = len([e for e in AUDIT_LOG if e["event_type"] == "execution"])
    errors = len([e for e in AUDIT_LOG if e["event_type"] == "error"])
    
    # Approval metrics
    approved = len([e for e in AUDIT_LOG if e["event_type"] == "risk_decision" and e["details"].get("approved")])
    rejected = len([e for e in AUDIT_LOG if e["event_type"] == "risk_decision" and not e["details"].get("approved")])
    
    # Execution success rate
    successful_executions = len([e for e in AUDIT_LOG if e["event_type"] == "execution" and e["details"].get("success")])
    failed_executions = len([e for e in AUDIT_LOG if e["event_type"] == "execution" and not e["details"].get("success")])
    
    return {
        "total_events": total_events,
        "events_by_type": {
            "proposals": proposals,
            "risk_decisions": risk_decisions,
            "executions": executions,
            "errors": errors
        },
        "risk_metrics": {
            "approved": approved,
            "rejected": rejected,
            "approval_rate": approved / (approved + rejected) if (approved + rejected) > 0 else 0
        },
        "execution_metrics": {
            "successful": successful_executions,
            "failed": failed_executions,
            "success_rate": successful_executions / (successful_executions + failed_executions) if (successful_executions + failed_executions) > 0 else 0
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def clear_audit_log() -> Dict[str, Any]:
    """
    Clear audit log (for testing/demo reset).
    """
    global AUDIT_LOG
    events_cleared = len(AUDIT_LOG)
    AUDIT_LOG = []
    
    return {
        "success": True,
        "events_cleared": events_cleared,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    mcp.run()
