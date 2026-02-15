"""
AutoFinance Investing Supervisor Server

Orchestrates investing domain analytical agents for long-term portfolio management.
- Aggregates intelligence from fundamental, macro, portfolio analytics servers
- Builds structured rebalancing proposals
- Enforces risk validation
- Coordinates execution
- Logs all decisions

Tools:
- process_investment_review: Orchestrate full investment review and rebalancing
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, List
import uuid
import asyncio


# Initialize MCP Server
mcp = FastMCP("auto-finance-investing-supervisor")


# MCP Server endpoints
MCP_SERVERS = {
    "fundamental": "auto-finance-fundamental",
    "macro": "auto-finance-macro",
    "portfolio_analytics": "auto-finance-portfolio-analytics",
    "news": "auto-finance-news",
    "risk": "auto-finance-risk",
    "execution": "auto-finance-execution",
    "compliance": "auto-finance-compliance"
}


async def call_mcp_tool(server_name: str, tool_name: str, arguments: Dict) -> Any:
    """
    Call an MCP tool on another server.
    
    In production with Archestra, this would use proper MCP client connections.
    """
    print(f"[MCP Call] {server_name}.{tool_name}({arguments})")
    await asyncio.sleep(0.1)
    return {"simulated": True, "server": server_name, "tool": tool_name}


def calculate_target_allocation(
    fundamental_analysis: Dict[str, Any],
    macro_analysis: Dict[str, Any],
    current_portfolio: Dict[str, Any]
) -> Dict[str, float]:
    """
    Calculate target allocation based on fundamental and macro analysis.
    
    Returns: {symbol: target_weight}
    """
    # Extract key signals
    investment_stance = macro_analysis.get("investment_stance", "BALANCED")
    macro_confidence = macro_analysis.get("confidence", 0.6)
    
    # Base allocation by stance
    if investment_stance == "AGGRESSIVE":
        target_invested = 0.80  # 80% invested
    elif investment_stance == "DEFENSIVE":
        target_invested = 0.50  # 50% invested
    else:
        target_invested = 0.70  # 70% invested
    
    # For demo, create simple equal-weight target for existing positions
    positions = current_portfolio.get("positions", {})
    num_positions = len(positions)
    
    if num_positions == 0:
        return {}
    
    # Equal weight allocation
    weight_per_position = target_invested / num_positions
    
    target_allocation = {
        symbol: weight_per_position
        for symbol in positions.keys()
    }
    
    return target_allocation


def build_rebalance_changes(
    current_portfolio: Dict[str, Any],
    target_allocation: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Build list of changes needed to reach target allocation.
    """
    changes = []
    total_value = current_portfolio.get("total_value", 100000)
    positions = current_portfolio.get("positions", {})
    
    for symbol, target_weight in target_allocation.items():
        current_pos = positions.get(symbol, {})
        current_value = current_pos.get("current_value", 0)
        current_weight = current_value / total_value if total_value > 0 else 0
        
        target_value = target_weight * total_value
        value_diff = target_value - current_value
        
        # Only include if difference > 1% of portfolio
        if abs(value_diff) > total_value * 0.01:
            current_price = current_pos.get("current_price", 100)
            quantity_diff = abs(value_diff) / current_price
            
            changes.append({
                "symbol": symbol,
                "action": "BUY" if value_diff > 0 else "SELL",
                "quantity": round(quantity_diff, 4),
                "price": current_price,
                "value": round(abs(value_diff), 2),
                "current_weight": round(current_weight, 3),
                "target_weight": round(target_weight, 3)
            })
    
    return changes


@mcp.tool()
async def process_investment_review(
    review_type: str = "periodic",
    use_mcp_calls: bool = False
) -> Dict[str, Any]:
    """
    Process a complete investment review cycle.
    
    Flow:
    1. Gather portfolio analytics
    2. Analyze fundamentals
    3. Assess macro environment
    4. Determine target allocation
    5. Build rebalance proposal
    6. Validate with risk server
    7. Execute if approved
    8. Log everything to compliance
    
    Args:
        review_type: Type of review (periodic, triggered, manual)
        use_mcp_calls: If True, make actual MCP calls (requires Archestra)
    """
    review_id = f"REV_{uuid.uuid4().hex[:8]}"
    
    # Log review start
    await log_compliance_event(
        "system",
        "investing-supervisor",
        "process_investment_review",
        {
            "review_id": review_id,
            "review_type": review_type
        }
    )
    
    try:
        print(f"\n{'='*60}")
        print(f"[Investing Supervisor] Investment Review: {review_id}")
        print(f"Review Type: {review_type}")
        print(f"{'='*60}\n")
        
        # Step 1: Get current portfolio state
        print("[1/6] Fetching portfolio state...")
        if use_mcp_calls:
            portfolio_state = await call_mcp_tool(
                "execution",
                "get_portfolio_state",
                {}
            )
        else:
            # Mock portfolio
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
        
        print(f"   Total Value: ${portfolio_state.get('total_value', 0):,.2f}")
        print(f"   Positions: {len(portfolio_state.get('positions', {}))}")
        print(f"   Cash: ${portfolio_state.get('cash', 0):,.2f}")
        
        # Step 2: Analyze portfolio
        print("\n[2/6] Analyzing portfolio health...")
        if use_mcp_calls:
            portfolio_analysis = await call_mcp_tool(
                "portfolio_analytics",
                "evaluate_portfolio",
                {"portfolio_state": portfolio_state}
            )
        else:
            portfolio_analysis = {
                "portfolio_health": "GOOD",
                "health_score": 0.72,
                "rebalancing_needed": True,
                "insights": ["Portfolio allocation acceptable but could be optimized"]
            }
        
        print(f"   Health: {portfolio_analysis.get('portfolio_health')} (score: {portfolio_analysis.get('health_score', 0):.2f})")
        print(f"   Rebalancing Needed: {portfolio_analysis.get('rebalancing_needed')}")
        
        # Step 3: Analyze macro environment
        print("\n[3/6] Assessing macro environment...")
        if use_mcp_calls:
            macro_analysis = await call_mcp_tool("macro", "analyze_macro", {})
        else:
            macro_analysis = {
                "market_regime": "BULL",
                "risk_environment": "FAVORABLE",
                "investment_stance": "BALANCED",
                "confidence": 0.75,
                "insights": ["Market conditions favorable for moderate exposure"]
            }
        
        print(f"   Market Regime: {macro_analysis.get('market_regime')}")
        print(f"   Risk Environment: {macro_analysis.get('risk_environment')}")
        print(f"   Investment Stance: {macro_analysis.get('investment_stance')}")
        print(f"   Confidence: {macro_analysis.get('confidence', 0):.2%}")
        
        # Step 4: Analyze fundamentals for key positions
        print("\n[4/6] Analyzing fundamentals...")
        fundamental_analyses = {}
        
        for symbol in portfolio_state.get("positions", {}).keys():
            if use_mcp_calls:
                fund_analysis = await call_mcp_tool(
                    "fundamental",
                    "analyze_fundamentals",
                    {"symbol": symbol}
                )
            else:
                fund_analysis = {
                    "symbol": symbol,
                    "recommendation": "HOLD",
                    "confidence": 0.68,
                    "scores": {"overall": 0.68}
                }
            
            fundamental_analyses[symbol] = fund_analysis
            print(f"   {symbol}: {fund_analysis.get('recommendation')} (confidence: {fund_analysis.get('confidence', 0):.2%})")
        
        # Step 5: Build rebalancing proposal
        print("\n[5/6] Building rebalancing proposal...")
        
        # Calculate target allocation
        target_allocation = calculate_target_allocation(
            fundamental_analyses,
            macro_analysis,
            portfolio_state
        )
        
        print(f"   Target allocation calculated for {len(target_allocation)} positions")
        
        # Build changes
        changes = build_rebalance_changes(portfolio_state, target_allocation)
        
        if not changes:
            print("   No significant changes needed - portfolio aligned with targets")
            
            result = {
                "success": True,
                "review_id": review_id,
                "action_taken": "NO_REBALANCE",
                "reason": "Portfolio allocation within tolerance",
                "portfolio_analysis": portfolio_analysis,
                "macro_analysis": macro_analysis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await log_compliance_event(
                "system",
                "investing-supervisor",
                "review_complete_no_action",
                result
            )
            
            return result
        
        print(f"   Changes needed: {len(changes)}")
        for change in changes:
            print(f"     - {change['action']} {change['quantity']} {change['symbol']}")
        
        # Calculate total turnover
        total_turnover = sum(c["value"] for c in changes)
        turnover_pct = total_turnover / portfolio_state.get("total_value", 100000)
        
        rebalance_proposal = {
            "review_id": review_id,
            "proposal_type": "rebalance",
            "changes": changes,
            "total_turnover": round(total_turnover, 2),
            "turnover_pct": round(turnover_pct, 3),
            "target_allocation": target_allocation,
            "rationale": {
                "macro_stance": macro_analysis.get("investment_stance"),
                "portfolio_health": portfolio_analysis.get("portfolio_health"),
                "fundamentals": {
                    symbol: analysis.get("recommendation")
                    for symbol, analysis in fundamental_analyses.items()
                }
            }
        }
        
        # Log proposal
        await log_compliance_event(
            "proposal",
            "investing-supervisor",
            "rebalance_proposal_created",
            rebalance_proposal
        )
        
        # Step 6: Risk validation
        print(f"\n{'='*60}")
        print("[Risk Validation] Submitting to risk server...")
        print(f"{'='*60}")
        
        max_turnover_pct = 0.30  # 30% max turnover
        
        if use_mcp_calls:
            risk_validation = await call_mcp_tool(
                "risk",
                "validate_rebalance",
                {
                    "changes": changes,
                    "total_value": portfolio_state.get("total_value", 100000),
                    "max_turnover_pct": max_turnover_pct
                }
            )
        else:
            # Mock risk validation
            risk_validation = {
                "approved": True,
                "risk_score": 0.25,
                "violations": [],
                "reason": "Approved - rebalance within limits",
                "turnover_pct": turnover_pct
            }
        
        approved = risk_validation.get("approved", False)
        print(f"   Status: {'✓ APPROVED' if approved else '✗ REJECTED'}")
        print(f"   Risk Score: {risk_validation.get('risk_score', 0):.2f}")
        print(f"   Turnover: {risk_validation.get('turnover_pct', 0):.2%}")
        print(f"   Reason: {risk_validation.get('reason', 'N/A')}")
        
        if risk_validation.get("violations"):
            print(f"   Violations:")
            for violation in risk_validation["violations"]:
                print(f"     - {violation}")
        
        # Log risk decision
        await log_compliance_event(
            "risk_decision",
            "risk-server",
            "validate_rebalance",
            {
                "review_id": review_id,
                "approved": approved,
                **risk_validation
            }
        )
        
        # Step 7: Execute if approved
        execution_result = None
        
        if approved:
            print(f"\n{'='*60}")
            print("[Execution] Applying rebalance...")
            print(f"{'='*60}")
            
            if use_mcp_calls:
                execution_result = await call_mcp_tool(
                    "execution",
                    "apply_rebalance",
                    {
                        "rebalance_id": review_id,
                        "changes": changes,
                        "approved": True,
                        "risk_validation": risk_validation
                    }
                )
            else:
                execution_result = {
                    "success": True,
                    "rebalance_id": review_id,
                    "changes_applied": len(changes),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            success = execution_result.get("success", False)
            print(f"   Status: {'✓ SUCCESS' if success else '✗ FAILED'}")
            print(f"   Changes Applied: {execution_result.get('changes_applied', 0)}")
            
            # Log execution
            await log_compliance_event(
                "execution",
                "execution-server",
                "apply_rebalance",
                {
                    "review_id": review_id,
                    "success": success,
                    **execution_result
                }
            )
        else:
            print("\n[Execution] Rebalance rejected - not executed")
        
        # Final result
        print(f"\n{'='*60}")
        print(f"[Investing Supervisor] Review {review_id} complete")
        print(f"{'='*60}\n")
        
        return {
            "success": approved and (execution_result.get("success", False) if execution_result else False),
            "review_id": review_id,
            "action_taken": "REBALANCED" if approved else "REJECTED",
            "portfolio_analysis": portfolio_analysis,
            "macro_analysis": macro_analysis,
            "fundamental_analyses": fundamental_analyses,
            "rebalance_proposal": rebalance_proposal,
            "risk_validation": risk_validation,
            "execution": execution_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        error_msg = f"Error processing investment review: {str(e)}"
        print(f"\n[ERROR] {error_msg}")
        
        await log_compliance_event(
            "error",
            "investing-supervisor",
            "process_investment_review",
            {
                "review_id": review_id,
                "error": error_msg
            },
            "critical"
        )
        
        return {
            "success": False,
            "review_id": review_id,
            "error": error_msg,
            "timestamp": datetime.utcnow().isoformat()
        }


async def log_compliance_event(
    event_type: str,
    agent_name: str,
    action: str,
    details: Dict[str, Any],
    severity: str = "info"
):
    """Helper to log events to compliance server"""
    print(f"[Compliance Log] {event_type} - {agent_name}.{action}")


if __name__ == "__main__":
    mcp.run()
