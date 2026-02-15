"""
AutoFinance Portfolio Analytics Server

Portfolio analysis and optimization recommendations.
- Portfolio composition analysis
- Risk/return metrics
- Rebalancing recommendations

Tools:
- evaluate_portfolio: Comprehensive portfolio evaluation
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, List
import math


# Initialize MCP Server
mcp = FastMCP("auto-finance-portfolio-analytics")


# Simulation mode
SIMULATION_MODE = {
    "enabled": False,
    "portfolio_data": None
}


def calculate_portfolio_metrics(portfolio: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate portfolio risk/return metrics"""
    positions = portfolio.get("positions", {})
    total_value = portfolio.get("total_value", 100000)
    cash = portfolio.get("cash", 0)
    
    if not positions:
        return {
            "concentration_risk": 0.0,
            "diversification_score": 0.0,
            "cash_allocation": 1.0,
            "num_positions": 0
        }
    
    # Calculate concentration (Herfindahl index)
    weights = []
    for pos in positions.values():
        weight = pos.get("current_value", 0) / total_value
        weights.append(weight)
    
    herfindahl = sum(w ** 2 for w in weights)
    concentration_risk = herfindahl
    
    # Diversification score (inverse of concentration)
    diversification_score = (1.0 - herfindahl) if len(positions) > 1 else 0.0
    
    # Cash allocation
    cash_allocation = cash / total_value if total_value > 0 else 0
    
    return {
        "concentration_risk": round(concentration_risk, 3),
        "diversification_score": round(diversification_score, 3),
        "cash_allocation": round(cash_allocation, 3),
        "num_positions": len(positions),
        "invested_pct": round(1.0 - cash_allocation, 3)
    }


def identify_overexposure(portfolio: Dict[str, Any], threshold: float = 0.20) -> List[Dict]:
    """Identify positions exceeding concentration threshold"""
    positions = portfolio.get("positions", {})
    total_value = portfolio.get("total_value", 100000)
    
    overexposed = []
    
    for symbol, pos in positions.items():
        weight = pos.get("current_value", 0) / total_value
        
        if weight > threshold:
            overexposed.append({
                "symbol": symbol,
                "current_weight": round(weight, 3),
                "threshold": threshold,
                "excess_weight": round(weight - threshold, 3),
                "excess_value": round((weight - threshold) * total_value, 2)
            })
    
    return overexposed


def generate_rebalancing_suggestions(
    portfolio: Dict[str, Any],
    target_allocation: Dict[str, float] = None
) -> List[Dict]:
    """Generate rebalancing suggestions"""
    positions = portfolio.get("positions", {})
    total_value = portfolio.get("total_value", 100000)
    cash = portfolio.get("cash", 0)
    
    suggestions = []
    
    # Default target: equal weight if not specified
    if not target_allocation and positions:
        target_weight = 0.70 / len(positions)  # 70% invested, equal weight
        target_allocation = {symbol: target_weight for symbol in positions.keys()}
    
    if not target_allocation:
        return suggestions
    
    # Calculate current vs target
    for symbol, target_weight in target_allocation.items():
        current_value = positions.get(symbol, {}).get("current_value", 0)
        current_weight = current_value / total_value
        
        weight_diff = target_weight - current_weight
        value_diff = weight_diff * total_value
        
        if abs(value_diff) > total_value * 0.02:  # > 2% difference
            action = "BUY" if value_diff > 0 else "SELL"
            
            suggestions.append({
                "symbol": symbol,
                "action": action,
                "current_weight": round(current_weight, 3),
                "target_weight": round(target_weight, 3),
                "weight_diff": round(weight_diff, 3),
                "value_change": round(abs(value_diff), 2),
                "quantity": round(abs(value_diff) / positions.get(symbol, {}).get("current_price", 1), 4)
            })
    
    return suggestions


@mcp.tool()
def evaluate_portfolio(portfolio_state: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Comprehensive portfolio evaluation and analysis.
    
    Args:
        portfolio_state: Portfolio state (if None, fetches from execution server)
    
    Returns:
        Metrics, analysis, and recommendations
    """
    # Check simulation mode
    if SIMULATION_MODE["enabled"] and SIMULATION_MODE["portfolio_data"]:
        return SIMULATION_MODE["portfolio_data"]
    
    # Use provided state or mock default
    if not portfolio_state:
        portfolio_state = {
            "cash": 30000,
            "total_value": 100000,
            "positions": {
                "BTCUSDT": {
                    "quantity": 1.0,
                    "avg_price": 45000,
                    "current_price": 48000,
                    "current_value": 48000
                },
                "ETHUSDT": {
                    "quantity": 8.0,
                    "avg_price": 2600,
                    "current_price": 2800,
                    "current_value": 22400
                }
            }
        }
    
    # Calculate metrics
    metrics = calculate_portfolio_metrics(portfolio_state)
    
    # Identify issues
    overexposed = identify_overexposure(portfolio_state, threshold=0.20)
    
    # Generate recommendations
    rebalance_suggestions = generate_rebalancing_suggestions(portfolio_state)
    
    # Overall health score (0-1)
    health_factors = []
    
    # Diversification health
    div_score = metrics["diversification_score"]
    health_factors.append(div_score)
    
    # Cash allocation health (prefer 20-40%)
    cash_alloc = metrics["cash_allocation"]
    if 0.2 <= cash_alloc <= 0.4:
        cash_health = 1.0
    elif cash_alloc < 0.1 or cash_alloc > 0.5:
        cash_health = 0.3
    else:
        cash_health = 0.7
    health_factors.append(cash_health)
    
    # Concentration health
    concentration_health = 1.0 - metrics["concentration_risk"]
    health_factors.append(concentration_health)
    
    overall_health = sum(health_factors) / len(health_factors)
    
    # Health rating
    if overall_health > 0.75:
        health_rating = "EXCELLENT"
    elif overall_health > 0.60:
        health_rating = "GOOD"
    elif overall_health > 0.45:
        health_rating = "FAIR"
    else:
        health_rating = "POOR"
    
    # Generate insights
    insights = []
    
    if metrics["num_positions"] < 3:
        insights.append("Portfolio lacks diversification - consider adding positions")
    
    if metrics["cash_allocation"] < 0.15:
        insights.append("Low cash reserves - limited dry powder for opportunities")
    elif metrics["cash_allocation"] > 0.50:
        insights.append("High cash allocation - consider deploying capital")
    
    if overexposed:
        insights.append(f"Concentration risk detected in {len(overexposed)} position(s)")
    
    if not insights:
        insights.append("Portfolio allocation within acceptable parameters")
    
    return {
        "portfolio_health": health_rating,
        "health_score": round(overall_health, 3),
        "metrics": metrics,
        "overexposed_positions": overexposed,
        "rebalancing_needed": len(rebalance_suggestions) > 0,
        "rebalance_suggestions": rebalance_suggestions,
        "insights": insights,
        "total_value": portfolio_state.get("total_value", 0),
        "num_positions": metrics["num_positions"],
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def calculate_rebalance_proposal(
    portfolio_state: Dict[str, Any],
    target_allocation: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calculate detailed rebalance proposal.
    
    Args:
        portfolio_state: Current portfolio state
        target_allocation: Desired allocation {symbol: weight}
    """
    suggestions = generate_rebalancing_suggestions(portfolio_state, target_allocation)
    
    total_turnover = sum(abs(s["value_change"]) for s in suggestions)
    total_value = portfolio_state.get("total_value", 100000)
    turnover_pct = total_turnover / total_value if total_value > 0 else 0
    
    # Group by action
    buys = [s for s in suggestions if s["action"] == "BUY"]
    sells = [s for s in suggestions if s["action"] == "SELL"]
    
    return {
        "total_changes": len(suggestions),
        "buys": buys,
        "sells": sells,
        "total_turnover": round(total_turnover, 2),
        "turnover_pct": round(turnover_pct, 3),
        "estimated_impact": "LOW" if turnover_pct < 0.2 else "MEDIUM" if turnover_pct < 0.4 else "HIGH",
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def get_allocation_summary(portfolio_state: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get high-level allocation summary.
    """
    if not portfolio_state:
        portfolio_state = {
            "cash": 30000,
            "total_value": 100000,
            "positions": {}
        }
    
    positions = portfolio_state.get("positions", {})
    total_value = portfolio_state.get("total_value", 100000)
    cash = portfolio_state.get("cash", 0)
    
    allocations = []
    
    # Cash
    allocations.append({
        "asset": "CASH",
        "value": cash,
        "weight": round(cash / total_value, 3) if total_value > 0 else 0
    })
    
    # Positions
    for symbol, pos in positions.items():
        allocations.append({
            "asset": symbol,
            "value": pos.get("current_value", 0),
            "weight": round(pos.get("current_value", 0) / total_value, 3) if total_value > 0 else 0
        })
    
    # Sort by weight
    allocations.sort(key=lambda x: x["weight"], reverse=True)
    
    return {
        "total_value": total_value,
        "allocations": allocations,
        "largest_position": allocations[0] if len(allocations) > 1 else None,
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def set_simulation_portfolio(
    health_rating: str,
    health_score: float,
    rebalancing_needed: bool
) -> Dict[str, Any]:
    """
    Set deterministic portfolio evaluation for demo mode.
    """
    SIMULATION_MODE["enabled"] = True
    SIMULATION_MODE["portfolio_data"] = {
        "portfolio_health": health_rating,
        "health_score": health_score,
        "metrics": {
            "concentration_risk": 0.3,
            "diversification_score": 0.7,
            "cash_allocation": 0.3,
            "num_positions": 3,
            "invested_pct": 0.7
        },
        "overexposed_positions": [],
        "rebalancing_needed": rebalancing_needed,
        "rebalance_suggestions": [],
        "insights": ["Simulated portfolio"],
        "total_value": 100000,
        "num_positions": 3,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return {
        "success": True,
        "configured_health": health_rating,
        "health_score": health_score,
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def clear_simulation_mode() -> Dict[str, Any]:
    """Clear simulation mode."""
    SIMULATION_MODE["enabled"] = False
    SIMULATION_MODE["portfolio_data"] = None
    
    return {
        "success": True,
        "message": "Simulation mode cleared",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    mcp.run()
