"""
AutoFinance Risk Server

Pure policy validation server.
- No execution authority
- No state mutation
- Only validates proposals against policy rules

Tools:
- validate_trade: Validate trading proposals
- validate_rebalance: Validate portfolio rebalancing proposals
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, Literal


# Initialize MCP Server
mcp = FastMCP("auto-finance-risk")


# Policy Configuration
RISK_POLICY = {
    "max_position_size": 0.15,  # 15% of portfolio
    "max_volatility": 0.5,      # 50% annualized volatility
    "min_confidence": 0.6,       # 60% minimum confidence
    "max_portfolio_exposure": 0.8,  # 80% max invested
    "max_single_trade_value": 20000,  # $20k per trade
}


def calculate_risk_score(proposal: Dict[str, Any]) -> float:
    """Calculate risk score from 0 (low risk) to 1 (high risk)"""
    risk_factors = []
    
    # Volatility risk
    volatility = proposal.get("volatility", 0)
    risk_factors.append(min(volatility / RISK_POLICY["max_volatility"], 1.0))
    
    # Confidence risk (inverse)
    confidence = proposal.get("confidence", 1.0)
    risk_factors.append(1.0 - confidence)
    
    # Position size risk
    position_size = proposal.get("position_size_pct", 0)
    risk_factors.append(position_size / RISK_POLICY["max_position_size"])
    
    # Return average risk
    return sum(risk_factors) / len(risk_factors) if risk_factors else 0.0


@mcp.tool()
def validate_trade(
    symbol: str,
    action: Literal["BUY", "SELL"],
    quantity: float,
    price: float,
    confidence: float,
    volatility: float,
    position_size_pct: float,
    trade_value: float
) -> Dict[str, Any]:
    """
    Validate a trade proposal against risk policy.
    
    Returns approval status with reason.
    """
    violations = []
    
    # Check confidence threshold
    if confidence < RISK_POLICY["min_confidence"]:
        violations.append(f"Confidence {confidence:.2%} below minimum {RISK_POLICY['min_confidence']:.2%}")
    
    # Check volatility threshold
    if volatility > RISK_POLICY["max_volatility"]:
        violations.append(f"Volatility {volatility:.2%} exceeds maximum {RISK_POLICY['max_volatility']:.2%}")
    
    # Check position size
    if position_size_pct > RISK_POLICY["max_position_size"]:
        violations.append(f"Position size {position_size_pct:.2%} exceeds maximum {RISK_POLICY['max_position_size']:.2%}")
    
    # Check trade value
    if trade_value > RISK_POLICY["max_single_trade_value"]:
        violations.append(f"Trade value ${trade_value:,.2f} exceeds maximum ${RISK_POLICY['max_single_trade_value']:,.2f}")
    
    # Calculate risk score
    risk_score = calculate_risk_score({
        "volatility": volatility,
        "confidence": confidence,
        "position_size_pct": position_size_pct
    })
    
    # Determine approval
    approved = len(violations) == 0
    
    return {
        "approved": approved,
        "risk_score": round(risk_score, 3),
        "violations": violations,
        "reason": "Approved - within policy bounds" if approved else f"Rejected - {len(violations)} violations",
        "timestamp": datetime.utcnow().isoformat(),
        "proposal_type": "trade",
        "symbol": symbol,
        "action": action
    }


@mcp.tool()
def validate_rebalance(
    changes: list,
    total_value: float,
    max_turnover_pct: float
) -> Dict[str, Any]:
    """
    Validate a portfolio rebalance proposal.
    
    Args:
        changes: List of dicts with {symbol, action, quantity, value}
        total_value: Total portfolio value
        max_turnover_pct: Maximum allowed turnover percentage
    """
    violations = []
    
    # Calculate total turnover
    total_turnover = sum(abs(change.get("value", 0)) for change in changes)
    turnover_pct = total_turnover / total_value if total_value > 0 else 0
    
    # Check turnover limits
    if turnover_pct > max_turnover_pct:
        violations.append(f"Turnover {turnover_pct:.2%} exceeds maximum {max_turnover_pct:.2%}")
    
    # Check individual position sizes
    for change in changes:
        position_value = abs(change.get("value", 0))
        position_pct = position_value / total_value if total_value > 0 else 0
        
        if position_pct > RISK_POLICY["max_position_size"]:
            violations.append(f"Position {change.get('symbol')} size {position_pct:.2%} exceeds maximum")
    
    # Calculate risk score
    risk_score = min(turnover_pct / max_turnover_pct, 1.0)
    
    approved = len(violations) == 0
    
    return {
        "approved": approved,
        "risk_score": round(risk_score, 3),
        "violations": violations,
        "reason": "Approved - rebalance within limits" if approved else f"Rejected - {len(violations)} violations",
        "timestamp": datetime.utcnow().isoformat(),
        "proposal_type": "rebalance",
        "total_turnover": round(total_turnover, 2),
        "turnover_pct": round(turnover_pct, 3)
    }


@mcp.tool()
def get_risk_policy() -> Dict[str, Any]:
    """
    Return current risk policy configuration.
    Useful for transparency and debugging.
    """
    return {
        "policy": RISK_POLICY,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    mcp.run()
