"""
AutoFinance Trading Supervisor Server

Orchestrates trading domain analytical agents.
- Aggregates intelligence from market, technical, volatility, news servers
- Builds structured trade proposals
- Enforces risk validation
- Coordinates execution
- Logs all decisions

Tools:
- process_trade_request: Orchestrate full trading decision flow
"""

from mcp.server.fastmcp import FastMCP
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from datetime import datetime
from typing import Dict, Any
import uuid
import asyncio


# Initialize MCP Server
mcp = FastMCP("auto-finance-trading-supervisor")


# MCP Server endpoints (configured for Archestra orchestration)
MCP_SERVERS = {
    "market": "auto-finance-market",
    "technical": "auto-finance-technical",
    "volatility": "auto-finance-volatility",
    "news": "auto-finance-news",
    "risk": "auto-finance-risk",
    "execution": "auto-finance-execution",
    "compliance": "auto-finance-compliance"
}


async def call_mcp_tool(server_name: str, tool_name: str, arguments: Dict) -> Any:
    """
    Call an MCP tool on another server.
    
    In production with Archestra, this would use proper MCP client connections.
    For this demo, we'll simulate the calls with proper structure.
    """
    # This is a placeholder for actual MCP client calls
    # In real deployment with Archestra, this would establish proper MCP connections
    
    # For demo purposes, return structured mock responses
    # In production: Use mcp.client.stdio or appropriate transport
    
    print(f"[MCP Call] {server_name}.{tool_name}({arguments})")
    
    # Simulate MCP call delay
    await asyncio.sleep(0.1)
    
    # Mock responses for demonstration
    # In production, these would be actual MCP tool invocations
    return {"simulated": True, "server": server_name, "tool": tool_name}


def calculate_aggregate_confidence(signals: Dict[str, Any]) -> float:
    """
    Aggregate confidence from multiple signals.
    
    Weighted combination of technical, sentiment, and volatility signals.
    """
    weights = {
        "technical": 0.4,
        "sentiment": 0.3,
        "volatility": 0.3
    }
    
    technical_conf = signals.get("technical", {}).get("confidence", 0.5)
    sentiment_conf = signals.get("sentiment", {}).get("confidence", 0.5)
    
    # Volatility is inverse - high volatility reduces confidence
    volatility_score = signals.get("volatility", {}).get("risk_score", 0.5)
    volatility_conf = 1.0 - volatility_score
    
    aggregate = (
        technical_conf * weights["technical"] +
        sentiment_conf * weights["sentiment"] +
        volatility_conf * weights["volatility"]
    )
    
    return round(aggregate, 3)


def determine_trade_action(signals: Dict[str, Any]) -> str:
    """
    Determine trade action from aggregated signals.
    """
    technical_signal = signals.get("technical", {}).get("signal", "HOLD")
    sentiment = signals.get("sentiment", {}).get("sentiment", "NEUTRAL")
    
    # Simple majority voting
    buy_votes = 0
    sell_votes = 0
    
    if technical_signal == "BUY":
        buy_votes += 1
    elif technical_signal == "SELL":
        sell_votes += 1
    
    if sentiment == "POSITIVE":
        buy_votes += 1
    elif sentiment == "NEGATIVE":
        sell_votes += 1
    
    if buy_votes > sell_votes:
        return "BUY"
    elif sell_votes > buy_votes:
        return "SELL"
    else:
        return "HOLD"


@mcp.tool()
async def process_trade_request(
    symbol: str,
    quantity: float,
    use_mcp_calls: bool = False
) -> Dict[str, Any]:
    """
    Process a complete trade request through the trading swarm.
    
    Flow:
    1. Gather intelligence from analytical agents
    2. Build trade proposal
    3. Validate with risk server
    4. Execute if approved
    5. Log everything to compliance
    
    Args:
        symbol: Trading pair (e.g., "BTCUSDT")
        quantity: Trade quantity
        use_mcp_calls: If True, make actual MCP calls (requires Archestra)
    """
    trade_id = f"TRD_{uuid.uuid4().hex[:8]}"
    
    # Log trade request
    await log_compliance_event(
        "proposal",
        "trading-supervisor",
        "process_trade_request",
        {
            "trade_id": trade_id,
            "symbol": symbol,
            "quantity": quantity
        }
    )
    
    try:
        # Step 1: Gather market intelligence
        print(f"\n{'='*60}")
        print(f"[Trading Supervisor] Processing trade request: {trade_id}")
        print(f"Symbol: {symbol}, Quantity: {quantity}")
        print(f"{'='*60}\n")
        
        # Get market data
        print("[1/5] Fetching market data...")
        if use_mcp_calls:
            market_data = await call_mcp_tool("market", "get_live_price", {"symbol": symbol})
        else:
            # Mock for demo
            market_data = {
                "symbol": symbol,
                "price": 48000.0,
                "timestamp": datetime.utcnow().isoformat()
            }
        current_price = market_data.get("price", 48000.0)
        print(f"   Current price: ${current_price:,.2f}")
        
        # Get technical analysis
        print("[2/5] Generating technical signals...")
        if use_mcp_calls:
            technical_data = await call_mcp_tool(
                "technical",
                "generate_signal",
                {"symbol": symbol, "current_price": current_price}
            )
        else:
            technical_data = {
                "signal": "BUY",
                "confidence": 0.72,
                "reason": "Bullish technical setup"
            }
        print(f"   Signal: {technical_data.get('signal')} (confidence: {technical_data.get('confidence', 0):.2%})")
        
        # Get volatility analysis
        print("[3/5] Analyzing volatility...")
        if use_mcp_calls:
            volatility_data = await call_mcp_tool(
                "volatility",
                "get_volatility_score",
                {"symbol": symbol, "current_price": current_price}
            )
        else:
            volatility_data = {
                "volatility": 0.35,
                "risk_level": "MEDIUM",
                "risk_score": 0.45
            }
        print(f"   Volatility: {volatility_data.get('volatility', 0):.2%} ({volatility_data.get('risk_level')})")
        
        # Get sentiment analysis
        print("[4/5] Analyzing news sentiment...")
        if use_mcp_calls:
            sentiment_data = await call_mcp_tool("news", "analyze_sentiment", {"symbol": symbol})
        else:
            sentiment_data = {
                "sentiment": "POSITIVE",
                "score": 0.68,
                "confidence": 0.65
            }
        print(f"   Sentiment: {sentiment_data.get('sentiment')} (score: {sentiment_data.get('score', 0):.2f})")
        
        # Step 2: Aggregate signals and build proposal
        print("\n[5/5] Building trade proposal...")
        
        signals = {
            "technical": technical_data,
            "volatility": volatility_data,
            "sentiment": sentiment_data
        }
        
        action = determine_trade_action(signals)
        aggregate_confidence = calculate_aggregate_confidence(signals)
        trade_value = quantity * current_price
        
        # Get portfolio state to calculate position size
        if use_mcp_calls:
            portfolio_state = await call_mcp_tool("execution", "get_portfolio_state", {})
        else:
            portfolio_state = {
                "total_value": 100000.0,
                "cash": 80000.0
            }
        
        portfolio_value = portfolio_state.get("total_value", 100000.0)
        position_size_pct = trade_value / portfolio_value
        
        trade_proposal = {
            "trade_id": trade_id,
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": current_price,
            "trade_value": trade_value,
            "confidence": aggregate_confidence,
            "volatility": volatility_data.get("volatility", 0.35),
            "position_size_pct": position_size_pct,
            "signals": {
                "technical": technical_data.get("signal"),
                "sentiment": sentiment_data.get("sentiment"),
                "risk_level": volatility_data.get("risk_level")
            }
        }
        
        print(f"   Action: {action}")
        print(f"   Aggregate Confidence: {aggregate_confidence:.2%}")
        print(f"   Position Size: {position_size_pct:.2%} of portfolio")
        
        # Log proposal
        await log_compliance_event(
            "proposal",
            "trading-supervisor",
            "trade_proposal_created",
            trade_proposal
        )
        
        # Step 3: Risk validation
        print(f"\n{'='*60}")
        print("[Risk Validation] Submitting to risk server...")
        print(f"{'='*60}")
        
        if use_mcp_calls:
            risk_validation = await call_mcp_tool(
                "risk",
                "validate_trade",
                {
                    "symbol": symbol,
                    "action": action,
                    "quantity": quantity,
                    "price": current_price,
                    "confidence": aggregate_confidence,
                    "volatility": volatility_data.get("volatility", 0.35),
                    "position_size_pct": position_size_pct,
                    "trade_value": trade_value
                }
            )
        else:
            # Mock risk validation
            risk_validation = {
                "approved": True,
                "risk_score": 0.32,
                "violations": [],
                "reason": "Approved - within policy bounds"
            }
        
        approved = risk_validation.get("approved", False)
        print(f"   Status: {'✓ APPROVED' if approved else '✗ REJECTED'}")
        print(f"   Risk Score: {risk_validation.get('risk_score', 0):.2f}")
        print(f"   Reason: {risk_validation.get('reason', 'N/A')}")
        
        if risk_validation.get("violations"):
            print(f"   Violations:")
            for violation in risk_validation["violations"]:
                print(f"     - {violation}")
        
        # Log risk decision
        await log_compliance_event(
            "risk_decision",
            "risk-server",
            "validate_trade",
            {
                "trade_id": trade_id,
                "approved": approved,
                **risk_validation
            }
        )
        
        # Step 4: Execute if approved
        execution_result = None
        
        if approved:
            print(f"\n{'='*60}")
            print("[Execution] Sending to execution server...")
            print(f"{'='*60}")
            
            if use_mcp_calls:
                execution_result = await call_mcp_tool(
                    "execution",
                    "execute_trade",
                    {
                        "trade_id": trade_id,
                        "symbol": symbol,
                        "action": action,
                        "quantity": quantity,
                        "price": current_price,
                        "approved": True,
                        "risk_validation": risk_validation
                    }
                )
            else:
                execution_result = {
                    "success": True,
                    "trade_id": trade_id,
                    "symbol": symbol,
                    "action": action,
                    "quantity": quantity,
                    "price": current_price,
                    "value": trade_value,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            success = execution_result.get("success", False)
            print(f"   Status: {'✓ SUCCESS' if success else '✗ FAILED'}")
            
            if success:
                print(f"   Executed: {action} {quantity} {symbol} @ ${current_price:,.2f}")
                print(f"   Total Value: ${trade_value:,.2f}")
            else:
                print(f"   Error: {execution_result.get('reason', 'Unknown error')}")
            
            # Log execution
            await log_compliance_event(
                "execution",
                "execution-server",
                "execute_trade",
                {
                    "trade_id": trade_id,
                    "success": success,
                    **execution_result
                }
            )
        else:
            print("\n[Execution] Trade rejected - not executed")
        
        # Final result
        print(f"\n{'='*60}")
        print(f"[Trading Supervisor] Trade {trade_id} complete")
        print(f"{'='*60}\n")
        
        return {
            "success": approved and (execution_result.get("success", False) if execution_result else False),
            "trade_id": trade_id,
            "proposal": trade_proposal,
            "risk_validation": risk_validation,
            "execution": execution_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        error_msg = f"Error processing trade: {str(e)}"
        print(f"\n[ERROR] {error_msg}")
        
        await log_compliance_event(
            "error",
            "trading-supervisor",
            "process_trade_request",
            {
                "trade_id": trade_id,
                "error": error_msg
            },
            "critical"
        )
        
        return {
            "success": False,
            "trade_id": trade_id,
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
    # In production with Archestra, this would make an actual MCP call
    print(f"[Compliance Log] {event_type} - {agent_name}.{action}")


if __name__ == "__main__":
    mcp.run()
