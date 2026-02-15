"""
AutoFinance Simulation Engine Server

Provides "what-if" analysis and strategy backtesting.
Users can simulate trades before execution.
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random
import math

# Initialize MCP Server
mcp = FastMCP("auto-finance-simulation-engine")


@mcp.tool()
def simulate_trade(
    symbol: str,
    quantity: int,
    action: str,
    entry_price: float,
    current_portfolio_value: float = 100000.0
) -> Dict[str, Any]:
    """
    Simulate a trade with bull/base/bear scenarios.
    
    Args:
        symbol: Trading symbol
        quantity: Number of shares/units
        action: 'buy' or 'sell'
        entry_price: Entry price for the trade
        current_portfolio_value: Current total portfolio value
    
    Returns:
        Simulation results with multiple scenarios
    """
    trade_value = quantity * entry_price
    position_size_pct = (trade_value / current_portfolio_value) * 100
    
    # Scenario projections (30-day forward)
    scenarios = {
        "bull_case": {
            "probability": 20,
            "price_change_pct": 15,
            "description": "Strong upward momentum continues"
        },
        "base_case": {
            "probability": 50,
            "price_change_pct": 5,
            "description": "Normal market conditions"
        },
        "bear_case": {
            "probability": 30,
            "price_change_pct": -10,
            "description": "Market correction or negative news"
        }
    }
    
    results = {
        "symbol": symbol,
        "action": action,
        "quantity": quantity,
        "entry_price": entry_price,
        "trade_value": round(trade_value, 2),
        "position_size_pct": round(position_size_pct, 2),
        "current_portfolio_value": current_portfolio_value,
        "scenarios": {},
        "risk_metrics": {},
        "recommendation": ""
    }
    
    # Calculate each scenario
    for scenario_name, scenario in scenarios.items():
        price_change = entry_price * (scenario["price_change_pct"] / 100)
        exit_price = entry_price + price_change
        
        if action == "buy":
            pnl = (exit_price - entry_price) * quantity
        else:  # sell
            pnl = (entry_price - exit_price) * quantity
        
        pnl_pct = (pnl / trade_value) * 100
        
        results["scenarios"][scenario_name] = {
            "probability": scenario["probability"],
            "exit_price": round(exit_price, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "description": scenario["description"],
            "portfolio_impact_pct": round((pnl / current_portfolio_value) * 100, 2)
        }
    
    # Calculate risk metrics
    expected_return = sum(
        (scenario["pnl_pct"] / 100) * (scenarios[name]["probability"] / 100)
        for name, scenario in results["scenarios"].items()
    )
    
    # Calculate max drawdown
    max_loss = results["scenarios"]["bear_case"]["pnl"]
    max_loss_pct = (max_loss / trade_value) * 100
    
    # Risk/reward ratio
    best_gain = results["scenarios"]["bull_case"]["pnl"]
    risk_reward = abs(best_gain / max_loss) if max_loss < 0 else 0
    
    results["risk_metrics"] = {
        "expected_return_pct": round(expected_return * 100, 2),
        "max_potential_loss": round(max_loss, 2),
        "max_potential_loss_pct": round(max_loss_pct, 2),
        "max_potential_gain": round(best_gain, 2),
        "risk_reward_ratio": round(risk_reward, 2),
        "volatility_estimate": "Medium"  # Could calculate from historical data
    }
    
    # Generate recommendation
    if position_size_pct > 20:
        results["recommendation"] = "⚠️ WARNING: Position size > 20% of portfolio. Consider reducing."
    elif risk_reward < 1.5:
        results["recommendation"] = "⚠️ CAUTION: Risk/reward ratio below 1.5. Low upside potential."
    elif expected_return < 0:
        results["recommendation"] = "❌ NOT RECOMMENDED: Negative expected return."
    elif expected_return > 0.05 and risk_reward > 2:
        results["recommendation"] = "✅ FAVORABLE: Good risk/reward profile."
    else:
        results["recommendation"] = "⚖️ NEUTRAL: Moderate risk/reward. Proceed with caution."
    
    results["timestamp"] = datetime.now().isoformat()
    
    return results


@mcp.tool()
def simulate_portfolio_rebalance(
    current_positions: List[Dict[str, Any]],
    target_allocation: Dict[str, float]
) -> Dict[str, Any]:
    """
    Simulate portfolio rebalancing.
    
    Args:
        current_positions: List of current positions with symbol, quantity, price
        target_allocation: Target allocation percentages by symbol
    
    Returns:
        Rebalancing plan with required trades
    """
    # Calculate current portfolio value
    total_value = sum(pos["quantity"] * pos["price"] for pos in current_positions)
    
    # Calculate current allocation
    current_allocation = {}
    for pos in current_positions:
        symbol = pos["symbol"]
        value = pos["quantity"] * pos["price"]
        current_allocation[symbol] = (value / total_value) * 100
    
    # Calculate required trades
    trades = []
    for symbol, target_pct in target_allocation.items():
        current_pct = current_allocation.get(symbol, 0)
        diff_pct = target_pct - current_pct
        diff_value = (diff_pct / 100) * total_value
        
        # Find current position
        current_pos = next((p for p in current_positions if p["symbol"] == symbol), None)
        current_price = current_pos["price"] if current_pos else 100  # Default price
        
        if abs(diff_value) > total_value * 0.01:  # Only if > 1% of portfolio
            quantity_change = int(diff_value / current_price)
            action = "buy" if quantity_change > 0 else "sell"
            
            trades.append({
                "symbol": symbol,
                "action": action,
                "quantity": abs(quantity_change),
                "estimated_price": current_price,
                "estimated_value": abs(diff_value),
                "current_allocation": round(current_pct, 2),
                "target_allocation": round(target_pct, 2)
            })
    
    # Calculate turnover
    total_turnover = sum(trade["estimated_value"] for trade in trades) / 2
    turnover_pct = (total_turnover / total_value) * 100
    
    return {
        "current_portfolio_value": round(total_value, 2),
        "trades_required": len(trades),
        "trades": trades,
        "turnover_value": round(total_turnover, 2),
        "turnover_pct": round(turnover_pct, 2),
        "estimated_cost": round(total_turnover * 0.001, 2),  # 0.1% transaction cost
        "recommendation": "✅ APPROVED" if turnover_pct < 50 else "⚠️ HIGH TURNOVER",
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def simulate_strategy(
    strategy_type: str,
    symbol: str,
    initial_capital: float = 10000.0,
    timeframe_days: int = 30
) -> Dict[str, Any]:
    """
    Backtest a trading strategy.
    
    Args:
        strategy_type: Strategy name ('momentum', 'mean_reversion', 'buy_and_hold')
        symbol: Trading symbol
        initial_capital: Starting capital
        timeframe_days: Backtest period in days
    
    Returns:
        Strategy performance metrics
    """
    # Simplified backtest simulation
    # In production, would use real historical data
    
    trades_count = timeframe_days // 3  # Avg 1 trade every 3 days
    
    # Simulate strategy performance
    if strategy_type == "momentum":
        win_rate = 0.55
        avg_win = 1.8
        avg_loss = 1.0
    elif strategy_type == "mean_reversion":
        win_rate = 0.60
        avg_win = 1.2
        avg_loss = 1.0
    elif strategy_type == "buy_and_hold":
        win_rate = 0.65
        avg_win = 5.0
        avg_loss = 2.0
        trades_count = 1
    else:
        return {"error": f"Unknown strategy type: {strategy_type}"}
    
    # Calculate returns
    wins = int(trades_count * win_rate)
    losses = trades_count - wins
    
    total_return_pct = (wins * avg_win - losses * avg_loss)
    final_capital = initial_capital * (1 + total_return_pct / 100)
    profit = final_capital - initial_capital
    
    # Calculate Sharpe ratio (simplified)
    returns_std = 15  # Assumed 15% volatility
    sharpe = (total_return_pct - 2) / returns_std  # Risk-free rate = 2%
    
    # Max drawdown estimate
    max_drawdown = -avg_loss * 2  # Simplified
    
    return {
        "strategy_type": strategy_type,
        "symbol": symbol,
        "initial_capital": initial_capital,
        "final_capital": round(final_capital, 2),
        "profit": round(profit, 2),
        "return_pct": round(total_return_pct, 2),
        "trades_executed": trades_count,
        "winning_trades": wins,
        "losing_trades": losses,
        "win_rate": round(win_rate * 100, 1),
        "sharpe_ratio": round(sharpe, 2),
        "max_drawdown_pct": round(max_drawdown, 2),
        "timeframe_days": timeframe_days,
        "recommendation": "✅ PROFITABLE" if total_return_pct > 5 else "⚠️ UNDERPERFORMING",
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def calculate_position_size(
    account_value: float,
    risk_per_trade_pct: float,
    entry_price: float,
    stop_loss_price: float
) -> Dict[str, Any]:
    """
    Calculate optimal position size based on risk management.
    
    Args:
        account_value: Total account value
        risk_per_trade_pct: Maximum risk per trade (e.g., 2.0 for 2%)
        entry_price: Planned entry price
        stop_loss_price: Stop loss price
    
    Returns:
        Recommended position size and risk metrics
    """
    # Calculate maximum dollar risk
    max_risk_dollars = account_value * (risk_per_trade_pct / 100)
    
    # Calculate risk per share
    risk_per_share = abs(entry_price - stop_loss_price)
    
    # Calculate position size
    max_shares = int(max_risk_dollars / risk_per_share)
    position_value = max_shares * entry_price
    position_size_pct = (position_value / account_value) * 100
    
    # Calculate risk/reward
    distance_to_stop = abs(entry_price - stop_loss_price)
    # Assume target is 2x stop distance
    target_price = entry_price + (2 * distance_to_stop)
    risk_reward = 2.0
    
    return {
        "recommended_shares": max_shares,
        "position_value": round(position_value, 2),
        "position_size_pct": round(position_size_pct, 2),
        "risk_amount": round(max_risk_dollars, 2),
        "risk_per_share": round(risk_per_share, 2),
        "entry_price": entry_price,
        "stop_loss": stop_loss_price,
        "target_price": round(target_price, 2),
        "risk_reward_ratio": risk_reward,
        "recommendation": "✅ WITHIN LIMITS" if position_size_pct < 25 else "⚠️ POSITION TOO LARGE",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
