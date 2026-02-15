"""
AutoFinance Execution Server

The ONLY authority that modifies portfolio state.
- Executes approved trades
- Applies approved rebalances
- Maintains portfolio state
- Does NOT validate risk
- Does NOT make decisions

Tools:
- execute_trade: Execute an approved trade
- apply_rebalance: Apply an approved rebalance
- get_portfolio_state: Read current portfolio (read-only)
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, Literal
import copy


# Initialize MCP Server
mcp = FastMCP("auto-finance-execution")


# Portfolio State (ONLY place state exists)
PORTFOLIO_STATE = {
    "cash": 100000.0,
    "positions": {},  # {symbol: {quantity, avg_price, current_value}}
    "transaction_history": [],
    "last_updated": datetime.utcnow().isoformat()
}


def calculate_portfolio_value(state: Dict) -> float:
    """Calculate total portfolio value (cash + positions)"""
    cash = state.get("cash", 0)
    positions_value = sum(
        pos.get("current_value", 0) 
        for pos in state.get("positions", {}).values()
    )
    return cash + positions_value


def update_position_value(symbol: str, current_price: float):
    """Update current value of a position"""
    if symbol in PORTFOLIO_STATE["positions"]:
        quantity = PORTFOLIO_STATE["positions"][symbol]["quantity"]
        PORTFOLIO_STATE["positions"][symbol]["current_value"] = quantity * current_price
        PORTFOLIO_STATE["positions"][symbol]["current_price"] = current_price


@mcp.tool()
def execute_trade(
    trade_id: str,
    symbol: str,
    action: Literal["BUY", "SELL"],
    quantity: float,
    price: float,
    approved: bool,
    risk_validation: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute an approved trade.
    
    CRITICAL: Only executes if approved=True in risk validation.
    """
    # Verify approval
    if not approved:
        return {
            "success": False,
            "trade_id": trade_id,
            "reason": "Trade not approved by risk server",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    trade_value = quantity * price
    
    try:
        if action == "BUY":
            # Check sufficient cash
            if PORTFOLIO_STATE["cash"] < trade_value:
                return {
                    "success": False,
                    "trade_id": trade_id,
                    "reason": f"Insufficient cash: ${PORTFOLIO_STATE['cash']:,.2f} < ${trade_value:,.2f}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Execute buy
            PORTFOLIO_STATE["cash"] -= trade_value
            
            if symbol in PORTFOLIO_STATE["positions"]:
                # Update existing position
                pos = PORTFOLIO_STATE["positions"][symbol]
                total_quantity = pos["quantity"] + quantity
                total_cost = (pos["avg_price"] * pos["quantity"]) + trade_value
                pos["avg_price"] = total_cost / total_quantity
                pos["quantity"] = total_quantity
                pos["current_value"] = total_quantity * price
                pos["current_price"] = price
            else:
                # Create new position
                PORTFOLIO_STATE["positions"][symbol] = {
                    "quantity": quantity,
                    "avg_price": price,
                    "current_value": trade_value,
                    "current_price": price
                }
        
        elif action == "SELL":
            # Check position exists and sufficient quantity
            if symbol not in PORTFOLIO_STATE["positions"]:
                return {
                    "success": False,
                    "trade_id": trade_id,
                    "reason": f"No position in {symbol}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            pos = PORTFOLIO_STATE["positions"][symbol]
            if pos["quantity"] < quantity:
                return {
                    "success": False,
                    "trade_id": trade_id,
                    "reason": f"Insufficient quantity: {pos['quantity']} < {quantity}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Execute sell
            PORTFOLIO_STATE["cash"] += trade_value
            pos["quantity"] -= quantity
            pos["current_value"] = pos["quantity"] * price
            pos["current_price"] = price
            
            # Remove position if fully sold
            if pos["quantity"] == 0:
                del PORTFOLIO_STATE["positions"][symbol]
        
        # Record transaction
        transaction = {
            "trade_id": trade_id,
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price,
            "value": trade_value,
            "risk_score": risk_validation.get("risk_score", 0)
        }
        PORTFOLIO_STATE["transaction_history"].append(transaction)
        PORTFOLIO_STATE["last_updated"] = datetime.utcnow().isoformat()
        
        return {
            "success": True,
            "trade_id": trade_id,
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price,
            "value": trade_value,
            "new_cash": PORTFOLIO_STATE["cash"],
            "new_position": PORTFOLIO_STATE["positions"].get(symbol),
            "timestamp": transaction["timestamp"]
        }
    
    except Exception as e:
        return {
            "success": False,
            "trade_id": trade_id,
            "reason": f"Execution error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


@mcp.tool()
def apply_rebalance(
    rebalance_id: str,
    changes: list,
    approved: bool,
    risk_validation: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply an approved portfolio rebalance.
    
    Args:
        changes: List of {symbol, action, quantity, price, value}
    """
    if not approved:
        return {
            "success": False,
            "rebalance_id": rebalance_id,
            "reason": "Rebalance not approved by risk server",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    applied_changes = []
    
    try:
        for change in changes:
            result = execute_trade(
                trade_id=f"{rebalance_id}_{change['symbol']}",
                symbol=change["symbol"],
                action=change["action"],
                quantity=change["quantity"],
                price=change["price"],
                approved=True,
                risk_validation=risk_validation
            )
            applied_changes.append(result)
        
        return {
            "success": True,
            "rebalance_id": rebalance_id,
            "changes_applied": len(applied_changes),
            "changes": applied_changes,
            "new_portfolio_value": calculate_portfolio_value(PORTFOLIO_STATE),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "rebalance_id": rebalance_id,
            "reason": f"Rebalance error: {str(e)}",
            "partial_changes": applied_changes,
            "timestamp": datetime.utcnow().isoformat()
        }


@mcp.tool()
def get_portfolio_state() -> Dict[str, Any]:
    """
    Get current portfolio state (read-only).
    
    Returns cash, positions, and portfolio metrics.
    """
    total_value = calculate_portfolio_value(PORTFOLIO_STATE)
    
    return {
        "cash": PORTFOLIO_STATE["cash"],
        "positions": copy.deepcopy(PORTFOLIO_STATE["positions"]),
        "total_value": total_value,
        "num_positions": len(PORTFOLIO_STATE["positions"]),
        "cash_pct": PORTFOLIO_STATE["cash"] / total_value if total_value > 0 else 1.0,
        "invested_pct": (total_value - PORTFOLIO_STATE["cash"]) / total_value if total_value > 0 else 0.0,
        "last_updated": PORTFOLIO_STATE["last_updated"],
        "transaction_count": len(PORTFOLIO_STATE["transaction_history"])
    }


@mcp.tool()
def update_position_prices(price_updates: Dict[str, float]) -> Dict[str, Any]:
    """
    Update current prices for positions (mark-to-market).
    
    Args:
        price_updates: {symbol: current_price}
    """
    updated = []
    
    for symbol, current_price in price_updates.items():
        if symbol in PORTFOLIO_STATE["positions"]:
            update_position_value(symbol, current_price)
            updated.append(symbol)
    
    PORTFOLIO_STATE["last_updated"] = datetime.utcnow().isoformat()
    
    return {
        "updated_symbols": updated,
        "new_portfolio_value": calculate_portfolio_value(PORTFOLIO_STATE),
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def reset_portfolio(initial_cash: float = 100000.0) -> Dict[str, Any]:
    """
    Reset portfolio to initial state (for testing/demo).
    """
    global PORTFOLIO_STATE
    
    PORTFOLIO_STATE = {
        "cash": initial_cash,
        "positions": {},
        "transaction_history": [],
        "last_updated": datetime.utcnow().isoformat()
    }
    
    return {
        "success": True,
        "message": "Portfolio reset to initial state",
        "initial_cash": initial_cash,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    mcp.run()
