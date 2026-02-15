"""
AutoFinance Investing Demo

Demonstrates the investing domain flow:
1. Investing supervisor runs periodic review
2. Analyzes portfolio, fundamentals, and macro
3. Builds rebalancing proposal
4. Risk validation
5. Execution (if approved)
6. Compliance logging
"""

import asyncio
from datetime import datetime


class MockMCPClient:
    """Mock MCP client for demo purposes"""
    
    async def call_tool(self, server: str, tool: str, args: dict):
        """Simulate MCP tool calls"""
        await asyncio.sleep(0.1)
        
        if server == "execution":
            return await self._mock_execution(tool, args)
        elif server == "portfolio_analytics":
            return await self._mock_portfolio_analytics(tool, args)
        elif server == "fundamental":
            return await self._mock_fundamental(tool, args)
        elif server == "macro":
            return await self._mock_macro(tool, args)
        elif server == "risk":
            return await self._mock_risk(tool, args)
        elif server == "compliance":
            return await self._mock_compliance(tool, args)
    
    async def _mock_execution(self, tool, args):
        if tool == "get_portfolio_state":
            return {
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
        elif tool == "apply_rebalance" and args.get("approved"):
            return {
                "success": True,
                "rebalance_id": args["rebalance_id"],
                "changes_applied": len(args["changes"]),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _mock_portfolio_analytics(self, tool, args):
        if tool == "evaluate_portfolio":
            return {
                "portfolio_health": "GOOD",
                "health_score": 0.72,
                "metrics": {
                    "concentration_risk": 0.35,
                    "diversification_score": 0.65,
                    "cash_allocation": 0.30,
                    "num_positions": 2
                },
                "rebalancing_needed": True,
                "insights": ["Portfolio concentrated in BTC", "Consider adding diversification"]
            }
    
    async def _mock_fundamental(self, tool, args):
        if tool == "analyze_fundamentals":
            recommendations = {
                "BTCUSDT": ("HOLD", 0.75),
                "ETHUSDT": ("BUY", 0.80)
            }
            rec, conf = recommendations.get(args["symbol"], ("HOLD", 0.65))
            
            return {
                "symbol": args["symbol"],
                "recommendation": rec,
                "confidence": conf,
                "scores": {
                    "valuation": 0.70,
                    "quality": 0.85,
                    "growth": 0.75,
                    "overall": 0.77
                }
            }
    
    async def _mock_macro(self, tool, args):
        if tool == "analyze_macro":
            return {
                "market_regime": "BULL",
                "risk_environment": "FAVORABLE",
                "investment_stance": "BALANCED",
                "confidence": 0.75,
                "indicators": {
                    "risk_appetite": 0.72,
                    "liquidity_score": 0.68
                },
                "insights": ["Market conditions favorable", "Moderate positioning recommended"]
            }
    
    async def _mock_risk(self, tool, args):
        if tool == "validate_rebalance":
            return {
                "approved": True,
                "risk_score": 0.28,
                "violations": [],
                "reason": "Approved - rebalance within limits",
                "turnover_pct": args.get("max_turnover_pct", 0.2) * 0.7
            }
    
    async def _mock_compliance(self, tool, args):
        if tool == "log_event":
            return {
                "success": True,
                "event_id": f"EVT_{datetime.utcnow().strftime('%H%M%S')}",
                "logged_at": datetime.utcnow().isoformat()
            }


async def run_investing_demo():
    """Run complete investing demo"""
    
    print("="*80)
    print("💼 AutoFinance Investing Demo")
    print("="*80)
    print()
    
    client = MockMCPClient()
    
    print("🔄 SCENARIO: Periodic Portfolio Review & Rebalancing")
    print("-"*80)
    
    await run_investment_review(client)
    
    print("\n" + "="*80)
    print("✅ Investing Demo Complete")
    print("="*80)


async def run_investment_review(client):
    """Run investment review scenario"""
    
    review_id = f"REV_{datetime.utcnow().strftime('%H%M%S')}"
    
    print(f"\n🔹 Investment Review: {review_id}")
    print(f"   Type: Periodic Review")
    print()
    
    # Step 1: Portfolio State
    print("[1/6] 💰 Fetching Portfolio State...")
    
    portfolio_state = await client.call_tool("execution", "get_portfolio_state", {})
    
    print(f"   ✓ Total Value: ${portfolio_state['total_value']:,.2f}")
    print(f"   ✓ Cash: ${portfolio_state['cash']:,.2f}")
    print(f"   ✓ Positions: {len(portfolio_state['positions'])}")
    
    for symbol, pos in portfolio_state["positions"].items():
        weight = pos["current_value"] / portfolio_state["total_value"]
        print(f"      - {symbol}: {weight:.1%} (${pos['current_value']:,.2f})")
    
    # Log review start
    await client.call_tool("compliance", "log_event", {
        "event_type": "system",
        "agent_name": "investing-supervisor",
        "action": "investment_review_started",
        "details": {"review_id": review_id}
    })
    
    # Step 2: Portfolio Analysis
    print("\n[2/6] 📊 Analyzing Portfolio Health...")
    
    portfolio_analysis = await client.call_tool(
        "portfolio_analytics",
        "evaluate_portfolio",
        {"portfolio_state": portfolio_state}
    )
    
    print(f"   ✓ Health: {portfolio_analysis['portfolio_health']}")
    print(f"   ✓ Score: {portfolio_analysis['health_score']:.2f}")
    print(f"   ✓ Rebalancing Needed: {portfolio_analysis['rebalancing_needed']}")
    print(f"   ✓ Insights:")
    for insight in portfolio_analysis["insights"]:
        print(f"      - {insight}")
    
    # Step 3: Macro Analysis
    print("\n[3/6] 🌍 Assessing Macro Environment...")
    
    macro_analysis = await client.call_tool("macro", "analyze_macro", {})
    
    print(f"   ✓ Market Regime: {macro_analysis['market_regime']}")
    print(f"   ✓ Risk Environment: {macro_analysis['risk_environment']}")
    print(f"   ✓ Investment Stance: {macro_analysis['investment_stance']}")
    print(f"   ✓ Confidence: {macro_analysis['confidence']:.2%}")
    print(f"   ✓ Insights:")
    for insight in macro_analysis["insights"]:
        print(f"      - {insight}")
    
    # Step 4: Fundamental Analysis
    print("\n[4/6] 🔬 Analyzing Fundamentals...")
    
    fundamental_analyses = {}
    
    for symbol in portfolio_state["positions"].keys():
        fund_analysis = await client.call_tool(
            "fundamental",
            "analyze_fundamentals",
            {"symbol": symbol}
        )
        fundamental_analyses[symbol] = fund_analysis
        
        print(f"   ✓ {symbol}:")
        print(f"      Recommendation: {fund_analysis['recommendation']}")
        print(f"      Confidence: {fund_analysis['confidence']:.2%}")
        print(f"      Overall Score: {fund_analysis['scores']['overall']:.2f}")
    
    # Step 5: Build Rebalancing Proposal
    print("\n[5/6] 📋 Building Rebalancing Proposal...")
    
    # Determine target allocation based on analysis
    target_invested = 0.70  # 70% based on BALANCED stance
    num_positions = len(portfolio_state["positions"])
    weight_per_position = target_invested / num_positions if num_positions > 0 else 0
    
    # For ETHUSDT with BUY recommendation, increase slightly
    target_allocation = {
        "BTCUSDT": 0.30,  # Reduce from current 48%
        "ETHUSDT": 0.40   # Increase from current 22% (BUY recommendation)
    }
    
    # Calculate changes
    changes = []
    total_value = portfolio_state["total_value"]
    
    for symbol, target_weight in target_allocation.items():
        current_pos = portfolio_state["positions"][symbol]
        current_value = current_pos["current_value"]
        current_weight = current_value / total_value
        
        target_value = target_weight * total_value
        value_diff = target_value - current_value
        
        if abs(value_diff) > total_value * 0.01:
            quantity_diff = abs(value_diff) / current_pos["current_price"]
            
            changes.append({
                "symbol": symbol,
                "action": "BUY" if value_diff > 0 else "SELL",
                "quantity": round(quantity_diff, 4),
                "price": current_pos["current_price"],
                "value": round(abs(value_diff), 2),
                "current_weight": round(current_weight, 3),
                "target_weight": round(target_weight, 3)
            })
    
    print(f"   ✓ Changes Required: {len(changes)}")
    
    for change in changes:
        symbol = change['symbol']
        action = change['action']
        qty = change['quantity']
        value = change['value']
        print(f"      - {action} {qty} {symbol} (${value:,.2f})")
        print(f"        Current: {change['current_weight']:.1%} → Target: {change['target_weight']:.1%}")
    
    total_turnover = sum(c["value"] for c in changes)
    turnover_pct = total_turnover / total_value
    
    print(f"   ✓ Total Turnover: ${total_turnover:,.2f} ({turnover_pct:.1%})")
    
    # Log proposal
    await client.call_tool("compliance", "log_event", {
        "event_type": "proposal",
        "agent_name": "investing-supervisor",
        "action": "rebalance_proposal_created",
        "details": {"review_id": review_id, "changes": len(changes)}
    })
    
    # Step 6: Risk Validation
    print("\n[6/6] 🛡️  Risk Validation...")
    
    risk_validation = await client.call_tool(
        "risk",
        "validate_rebalance",
        {
            "changes": changes,
            "total_value": total_value,
            "max_turnover_pct": 0.30
        }
    )
    
    approved = risk_validation["approved"]
    
    if approved:
        print(f"   ✅ APPROVED")
        print(f"   ✓ Risk Score: {risk_validation['risk_score']:.2f}")
        print(f"   ✓ Turnover: {risk_validation['turnover_pct']:.1%}")
        print(f"   ✓ Reason: {risk_validation['reason']}")
    else:
        print(f"   ❌ REJECTED")
        print(f"   ✗ Reason: {risk_validation['reason']}")
        if risk_validation["violations"]:
            print(f"   ✗ Violations:")
            for violation in risk_validation["violations"]:
                print(f"      - {violation}")
    
    # Log risk decision
    await client.call_tool("compliance", "log_event", {
        "event_type": "risk_decision",
        "agent_name": "risk-server",
        "action": "validate_rebalance",
        "details": {"review_id": review_id, "approved": approved}
    })
    
    # Execution
    print(f"\n⚡ Execution...")
    
    if approved:
        execution_result = await client.call_tool(
            "execution",
            "apply_rebalance",
            {
                "rebalance_id": review_id,
                "changes": changes,
                "approved": True,
                "risk_validation": risk_validation
            }
        )
        
        if execution_result["success"]:
            print(f"   ✅ REBALANCE APPLIED")
            print(f"   ✓ Changes Applied: {execution_result['changes_applied']}")
            print(f"   ✓ Portfolio rebalanced successfully")
        else:
            print(f"   ❌ EXECUTION FAILED")
    else:
        print(f"   ⏸️  NOT EXECUTED (rejected by risk)")
    
    # Summary
    print(f"\n📊 Summary")
    
    if approved:
        print(f"   ✅ Investment review {review_id} completed successfully")
        print(f"   ✓ Portfolio rebalanced according to analysis")
        print(f"   ✓ Aligned with {macro_analysis['investment_stance']} macro stance")
        print(f"   📝 All events logged to compliance")
    else:
        print(f"   ❌ Rebalancing rejected")
        print(f"   📝 Rejection logged to compliance")


if __name__ == "__main__":
    asyncio.run(run_investing_demo())
