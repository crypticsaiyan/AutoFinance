"""
AutoFinance Trading Demo

Demonstrates the trading domain flow:
1. Trading supervisor receives trade request
2. Aggregates intelligence from analytical agents
3. Builds trade proposal
4. Risk validation
5. Execution (if approved)
6. Compliance logging

This demo shows both APPROVED and REJECTED scenarios.
"""

import asyncio
from datetime import datetime


class MockMCPClient:
    """Mock MCP client for demo purposes"""
    
    async def call_tool(self, server: str, tool: str, args: dict):
        """Simulate MCP tool calls"""
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Route to appropriate mock handler
        if server == "market":
            return await self._mock_market(tool, args)
        elif server == "technical":
            return await self._mock_technical(tool, args)
        elif server == "volatility":
            return await self._mock_volatility(tool, args)
        elif server == "news":
            return await self._mock_news(tool, args)
        elif server == "risk":
            return await self._mock_risk(tool, args)
        elif server == "execution":
            return await self._mock_execution(tool, args)
        elif server == "compliance":
            return await self._mock_compliance(tool, args)
    
    async def _mock_market(self, tool, args):
        if tool == "get_live_price":
            return {
                "symbol": args["symbol"],
                "price": 48000.0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _mock_technical(self, tool, args):
        if tool == "generate_signal":
            return {
                "signal": "BUY",
                "confidence": 0.72,
                "indicators": {"sma_20": 47500, "sma_50": 46000, "rsi": 58},
                "reason": "Bullish technical setup - price above SMAs"
            }
    
    async def _mock_volatility(self, tool, args):
        if tool == "get_volatility_score":
            return {
                "volatility": 0.35,
                "risk_level": "MEDIUM",
                "risk_score": 0.45
            }
    
    async def _mock_news(self, tool, args):
        if tool == "analyze_sentiment":
            return {
                "sentiment": "POSITIVE",
                "score": 0.68,
                "confidence": 0.65,
                "news_count": 5
            }
    
    async def _mock_risk(self, tool, args):
        if tool == "validate_trade":
            # Check if this is the high-risk scenario
            if args.get("volatility", 0) > 0.6:
                return {
                    "approved": False,
                    "risk_score": 0.82,
                    "violations": ["Volatility 0.75 exceeds maximum 0.50"],
                    "reason": "Rejected - 1 violations"
                }
            else:
                return {
                    "approved": True,
                    "risk_score": 0.32,
                    "violations": [],
                    "reason": "Approved - within policy bounds"
                }
    
    async def _mock_execution(self, tool, args):
        if tool == "execute_trade" and args.get("approved"):
            return {
                "success": True,
                "trade_id": args["trade_id"],
                "symbol": args["symbol"],
                "action": args["action"],
                "quantity": args["quantity"],
                "price": args["price"],
                "value": args["quantity"] * args["price"],
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "reason": "Trade not approved"
            }
    
    async def _mock_compliance(self, tool, args):
        if tool == "log_event":
            return {
                "success": True,
                "event_id": f"EVT_{datetime.utcnow().strftime('%H%M%S')}",
                "logged_at": datetime.utcnow().isoformat()
            }


async def run_trading_demo():
    """Run complete trading demo"""
    
    print("="*80)
    print("🚀 AutoFinance Trading Demo")
    print("="*80)
    print()
    
    client = MockMCPClient()
    
    # Scenario 1: APPROVED TRADE
    print("📊 SCENARIO 1: Approved Trade")
    print("-"*80)
    
    await run_trade_scenario(
        client,
        symbol="BTCUSDT",
        quantity=0.5,
        scenario="approved"
    )
    
    print("\n" + "="*80 + "\n")
    
    # Scenario 2: REJECTED TRADE (High Volatility)
    print("🚫 SCENARIO 2: Rejected Trade (Policy Violation)")
    print("-"*80)
    
    await run_trade_scenario(
        client,
        symbol="VOLATILE_COIN",
        quantity=0.5,
        scenario="rejected"
    )
    
    print("\n" + "="*80)
    print("✅ Trading Demo Complete")
    print("="*80)


async def run_trade_scenario(client, symbol, quantity, scenario):
    """Run a single trade scenario"""
    
    trade_id = f"TRD_{datetime.utcnow().strftime('%H%M%S')}"
    
    print(f"\n🔹 Trade Request: {trade_id}")
    print(f"   Symbol: {symbol}")
    print(f"   Quantity: {quantity}")
    print()
    
    # Step 1: Market Intelligence
    print("[1/5] 📈 Gathering Market Intelligence...")
    
    market_data = await client.call_tool("market", "get_live_price", {"symbol": symbol})
    print(f"   ✓ Price: ${market_data['price']:,.2f}")
    
    technical_data = await client.call_tool(
        "technical",
        "generate_signal",
        {"symbol": symbol, "current_price": market_data["price"]}
    )
    print(f"   ✓ Technical: {technical_data['signal']} (confidence: {technical_data['confidence']:.2%})")
    
    volatility_data = await client.call_tool(
        "volatility",
        "get_volatility_score",
        {"symbol": symbol, "current_price": market_data["price"]}
    )
    # Override for rejected scenario
    if scenario == "rejected":
        volatility_data["volatility"] = 0.75
        volatility_data["risk_level"] = "HIGH"
    
    print(f"   ✓ Volatility: {volatility_data['volatility']:.2%} ({volatility_data['risk_level']})")
    
    sentiment_data = await client.call_tool("news", "analyze_sentiment", {"symbol": symbol})
    print(f"   ✓ Sentiment: {sentiment_data['sentiment']} (score: {sentiment_data['score']:.2f})")
    
    # Step 2: Build Proposal
    print("\n[2/5] 📋 Building Trade Proposal...")
    
    trade_value = quantity * market_data["price"]
    portfolio_value = 100000
    position_size_pct = trade_value / portfolio_value
    
    # Aggregate confidence
    aggregate_confidence = (
        technical_data["confidence"] * 0.4 +
        sentiment_data["confidence"] * 0.3 +
        (1.0 - volatility_data["risk_score"]) * 0.3
    )
    
    print(f"   ✓ Action: BUY")
    print(f"   ✓ Trade Value: ${trade_value:,.2f}")
    print(f"   ✓ Position Size: {position_size_pct:.2%}")
    print(f"   ✓ Aggregate Confidence: {aggregate_confidence:.2%}")
    
    # Log proposal
    await client.call_tool("compliance", "log_event", {
        "event_type": "proposal",
        "agent_name": "trading-supervisor",
        "action": "trade_proposal_created",
        "details": {"trade_id": trade_id, "symbol": symbol}
    })
    
    # Step 3: Risk Validation
    print("\n[3/5] 🛡️  Risk Validation...")
    
    risk_validation = await client.call_tool(
        "risk",
        "validate_trade",
        {
            "symbol": symbol,
            "action": "BUY",
            "quantity": quantity,
            "price": market_data["price"],
            "confidence": aggregate_confidence,
            "volatility": volatility_data["volatility"],
            "position_size_pct": position_size_pct,
            "trade_value": trade_value
        }
    )
    
    approved = risk_validation["approved"]
    
    if approved:
        print(f"   ✅ APPROVED")
        print(f"   ✓ Risk Score: {risk_validation['risk_score']:.2f}")
        print(f"   ✓ Reason: {risk_validation['reason']}")
    else:
        print(f"   ❌ REJECTED")
        print(f"   ✗ Risk Score: {risk_validation['risk_score']:.2f}")
        print(f"   ✗ Reason: {risk_validation['reason']}")
        if risk_validation["violations"]:
            print(f"   ✗ Violations:")
            for violation in risk_validation["violations"]:
                print(f"      - {violation}")
    
    # Log risk decision
    await client.call_tool("compliance", "log_event", {
        "event_type": "risk_decision",
        "agent_name": "risk-server",
        "action": "validate_trade",
        "details": {"trade_id": trade_id, "approved": approved}
    })
    
    # Step 4: Execution
    print(f"\n[4/5] ⚡ Execution...")
    
    if approved:
        execution_result = await client.call_tool(
            "execution",
            "execute_trade",
            {
                "trade_id": trade_id,
                "symbol": symbol,
                "action": "BUY",
                "quantity": quantity,
                "price": market_data["price"],
                "approved": True,
                "risk_validation": risk_validation
            }
        )
        
        if execution_result["success"]:
            print(f"   ✅ EXECUTED")
            print(f"   ✓ {execution_result['action']} {execution_result['quantity']} {execution_result['symbol']}")
            print(f"   ✓ Price: ${execution_result['price']:,.2f}")
            print(f"   ✓ Total: ${execution_result['value']:,.2f}")
        else:
            print(f"   ❌ EXECUTION FAILED")
            print(f"   ✗ {execution_result['reason']}")
    else:
        print(f"   ⏸️  NOT EXECUTED (rejected by risk)")
    
    # Step 5: Summary
    print(f"\n[5/5] 📊 Summary")
    
    if approved:
        print(f"   ✅ Trade {trade_id} completed successfully")
        print(f"   📝 All events logged to compliance")
    else:
        print(f"   ❌ Trade {trade_id} rejected")
        print(f"   📝 Rejection logged to compliance")


if __name__ == "__main__":
    asyncio.run(run_trading_demo())
