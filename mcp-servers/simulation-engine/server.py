"""
AutoFinance Simulation Engine Server

Real backtesting and "what-if" analysis using Yahoo Finance historical data.
- Trade simulation with real price history
- Strategy backtesting (momentum, mean reversion, buy & hold)
- Position sizing calculator
- Portfolio rebalance simulation

Tools:
- simulate_trade: Simulate trade with real historical scenarios
- simulate_strategy: Backtest a strategy with real data
- simulate_portfolio_rebalance: Simulate rebalancing
- calculate_position_size: Risk-based position sizing
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import math

try:
    import yfinance as yf
    import numpy as np
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance", "numpy"])
    import yfinance as yf
    import numpy as np


# Initialize MCP Server
mcp = FastMCP("auto-finance-simulation-engine")


def _get_ticker_symbol(symbol: str) -> str:
    """Convert symbol to Yahoo Finance format."""
    s = symbol.upper()
    
    # Map common crypto symbols to Yahoo format
    crypto_map = {
        "BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "BNB": "BNB-USD",
        "XRP": "XRP-USD", "DOGE": "DOGE-USD", "ADA": "ADA-USD", "AVAX": "AVAX-USD",
        "DOT": "DOT-USD", "MATIC": "MATIC-USD", "LINK": "LINK-USD", "UNI": "UNI-USD",
        "LTC": "LTC-USD", "BCH": "BCH-USD", "ALGO": "ALGO-USD", "XLM": "XLM-USD",
        "NEAR": "NEAR-USD", "ATOM": "ATOM-USD", "ICP": "ICP-USD", "FIL": "FIL-USD"
    }
    
    # 1. Check exact match
    if s in crypto_map:
        return crypto_map[s]
        
    # 2. Check USDT pair (e.g. BTCUSDT, TSLAUSDT)
    if s.endswith("USDT"):
        base = s.replace("USDT", "")
        # If the base is a known crypto (e.g. LINK from LINKUSDT), use the crypto format
        if base in crypto_map:
            return crypto_map[base]
        # Otherwise assume it's a stock (e.g. TSLA from TSLAUSDT)
        return base
        
    # 3. Check -USD format
    if s.endswith("-USD"):
        return s
        
    # 4. Default to generic (usually stock)
    return s


def _fetch_historical(symbol: str, period: str = "6mo") -> list:
    """Fetch real historical closing prices."""
    yf_symbol = _get_ticker_symbol(symbol)
    ticker = yf.Ticker(yf_symbol)
    hist = ticker.history(period=period, interval="1d")

    if hist.empty:
        return []

    return [
        {"date": idx.strftime("%Y-%m-%d"), "close": round(float(row["Close"]), 2),
         "high": round(float(row["High"]), 2), "low": round(float(row["Low"]), 2),
         "volume": int(row["Volume"])}
        for idx, row in hist.iterrows()
    ]


@mcp.tool()
def simulate_trade(
    symbol: str,
    quantity: int,
    action: str,
    entry_price: float,
    current_portfolio_value: float = 100000.0
) -> Dict[str, Any]:
    """
    Simulate a trade using real historical volatility for scenario analysis.

    Args:
        symbol: Trading symbol (e.g., 'AAPL', 'BTCUSDT')
        quantity: Number of shares/units
        action: 'buy' or 'sell'
        entry_price: Entry price for the trade
        current_portfolio_value: Current portfolio value

    Returns:
        Simulation results with bull/base/bear scenarios based on real data
    """
    prices = _fetch_historical(symbol, "6mo")

    if len(prices) < 20:
        return {"error": f"Insufficient historical data for {symbol}", "symbol": symbol}

    closes = [p["close"] for p in prices]
    returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]

    # Real statistics
    avg_daily_return = sum(returns) / len(returns)
    std_daily = (sum((r - avg_daily_return)**2 for r in returns) / len(returns)) ** 0.5
    annualized_vol = std_daily * math.sqrt(252)
    max_drawdown = 0
    peak = closes[0]
    for p in closes:
        if p > peak:
            peak = p
        dd = (peak - p) / peak
        if dd > max_drawdown:
            max_drawdown = dd

    # Scenarios based on real volatility (30-day projections)
    trade_value = entry_price * quantity
    days = 30

    # Bull: +1.5 std devs over 30 days
    bull_return = (avg_daily_return + 1.5 * std_daily) * days
    bull_price = round(entry_price * (1 + bull_return), 2)
    bull_pnl = round((bull_price - entry_price) * quantity * (1 if action.lower() == "buy" else -1), 2)

    # Base: average return over 30 days
    base_return = avg_daily_return * days
    base_price = round(entry_price * (1 + base_return), 2)
    base_pnl = round((base_price - entry_price) * quantity * (1 if action.lower() == "buy" else -1), 2)

    # Bear: -1.5 std devs over 30 days
    bear_return = (avg_daily_return - 1.5 * std_daily) * days
    bear_price = round(entry_price * (1 + bear_return), 2)
    bear_pnl = round((bear_price - entry_price) * quantity * (1 if action.lower() == "buy" else -1), 2)

    # Risk metrics
    position_pct = (trade_value / current_portfolio_value) * 100
    max_loss = round(trade_value * max_drawdown, 2)

    return {
        "symbol": symbol,
        "action": action,
        "quantity": quantity,
        "entry_price": entry_price,
        "trade_value": round(trade_value, 2),
        "position_pct": round(position_pct, 2),
        "scenarios": {
            "bull": {
                "price": bull_price,
                "return_pct": round(bull_return * 100, 2),
                "pnl": bull_pnl
            },
            "base": {
                "price": base_price,
                "return_pct": round(base_return * 100, 2),
                "pnl": base_pnl
            },
            "bear": {
                "price": bear_price,
                "return_pct": round(bear_return * 100, 2),
                "pnl": bear_pnl
            }
        },
        "risk_metrics": {
            "annualized_volatility": round(annualized_vol * 100, 2),
            "max_historical_drawdown": round(max_drawdown * 100, 2),
            "max_potential_loss": max_loss,
            "data_points": len(closes)
        },
        "recommendation": "PROCEED" if position_pct < 10 and annualized_vol < 0.6 else "CAUTION",
        "timestamp": datetime.now().isoformat(),
        "source": "Yahoo Finance"
    }


@mcp.tool()
def simulate_strategy(
    strategy_type: str,
    symbol: str,
    initial_capital: float = 10000.0,
    timeframe_days: int = 90
) -> Dict[str, Any]:
    """
    Backtest a trading strategy with REAL historical data.

    Args:
        strategy_type: 'momentum', 'mean_reversion', or 'buy_and_hold'
        symbol: Trading symbol
        initial_capital: Starting capital
        timeframe_days: Backtest period in days

    Returns:
        Strategy performance metrics from real data
    """
    # Fetch enough data
    # Fetch enough data - ensure generous buffer for trading days vs calendar days
    if timeframe_days > 365:
        period = "5y"
    elif timeframe_days > 100:
        period = "2y"  # 1y might be tight for 180 trading days + indicators
    else:
        period = "1y"  # Always get plenty for lookbacks (SMA200 etc)
        
    prices = _fetch_historical(symbol, period)

    if len(prices) < timeframe_days:
        return {"error": f"Only {len(prices)} days of data available for {symbol}", "symbol": symbol}

    # Use the last N days
    prices = prices[-timeframe_days:]
    closes = [p["close"] for p in prices]

    capital = initial_capital
    position = 0
    trades = []
    portfolio_values = [initial_capital]

    # Detect if this is a high-price asset (crypto, BRK.A, etc.) → use fractional shares
    use_fractional = closes[0] > 500  # BTC ~$97k, ETH ~$3k, etc.

    def calc_shares(cap, price):
        """Calculate shares — fractional for expensive assets."""
        raw = (cap * 0.95) / price
        return round(raw, 6) if use_fractional else int(raw)

    if strategy_type == "buy_and_hold":
        # Buy on day 1, hold
        shares = calc_shares(capital, closes[0])
        if shares <= 0:
            return {"error": f"Insufficient capital (${initial_capital}) to buy {symbol} at ${closes[0]}", "symbol": symbol}
        cost = shares * closes[0]
        capital -= cost
        position = shares
        trades.append({"day": 0, "action": "BUY", "price": closes[0], "shares": round(shares, 6)})

        for price in closes[1:]:
            portfolio_values.append(capital + position * price)

        final_value = capital + position * closes[-1]
        trades.append({"day": len(closes)-1, "action": "HOLD", "price": closes[-1], "shares": round(position, 6)})

    elif strategy_type == "momentum":
        # 20-day momentum: buy when price > 20-day SMA, sell when below
        lookback = 20
        for i in range(lookback, len(closes)):
            sma = sum(closes[i-lookback:i]) / lookback
            price = closes[i]

            if price > sma and position == 0:
                # Buy signal
                shares = calc_shares(capital, price)
                if shares > 0:
                    capital -= shares * price
                    position = shares
                    trades.append({"day": i, "action": "BUY", "price": price, "shares": round(shares, 6)})

            elif price < sma and position > 0:
                # Sell signal
                capital += position * price
                trades.append({"day": i, "action": "SELL", "price": price, "shares": round(position, 6)})
                position = 0

            portfolio_values.append(capital + position * price)

        final_value = capital + position * closes[-1]

    elif strategy_type == "mean_reversion":
        # Adaptive mean reversion — threshold scales with asset volatility
        lookback = 20

        # Calculate asset volatility to set adaptive threshold
        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        avg_ret = sum(returns) / len(returns) if returns else 0
        std_ret = (sum((r - avg_ret)**2 for r in returns) / len(returns)) ** 0.5 if returns else 0.02
        # Threshold = 1 std dev of daily returns, clamped between 1% and 10%
        threshold = max(0.01, min(0.10, std_ret * math.sqrt(lookback) * 0.5))

        for i in range(lookback, len(closes)):
            sma = sum(closes[i-lookback:i]) / lookback
            deviation = (closes[i] - sma) / sma
            price = closes[i]

            if deviation < -threshold and position == 0:
                # Oversold - buy
                shares = calc_shares(capital, price)
                if shares > 0:
                    capital -= shares * price
                    position = shares
                    trades.append({"day": i, "action": "BUY", "price": price, "shares": round(shares, 6), "deviation": round(deviation*100, 2)})

            elif deviation > threshold and position > 0:
                # Overbought - sell
                capital += position * price
                trades.append({"day": i, "action": "SELL", "price": price, "shares": round(position, 6), "deviation": round(deviation*100, 2)})
                position = 0

            portfolio_values.append(capital + position * price)

        final_value = capital + position * closes[-1]
    else:
        return {"error": f"Unknown strategy: {strategy_type}. Use: momentum, mean_reversion, buy_and_hold"}

    # Calculate metrics
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    buy_hold_return = ((closes[-1] - closes[0]) / closes[0]) * 100

    # Max drawdown
    peak_val = portfolio_values[0]
    max_dd = 0
    for v in portfolio_values:
        if v > peak_val:
            peak_val = v
        dd = (peak_val - v) / peak_val
        if dd > max_dd:
            max_dd = dd

    # Daily returns for Sharpe
    daily_returns = []
    for i in range(1, len(portfolio_values)):
        daily_returns.append((portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1])

    avg_daily = sum(daily_returns) / len(daily_returns) if daily_returns else 0
    std_daily = (sum((r - avg_daily)**2 for r in daily_returns) / len(daily_returns)) ** 0.5 if daily_returns else 1
    sharpe = (avg_daily / std_daily) * math.sqrt(252) if std_daily > 0 else 0

    return {
        "symbol": symbol,
        "strategy": strategy_type,
        "timeframe_days": timeframe_days,
        "initial_capital": initial_capital,
        "final_value": round(final_value, 2),
        "total_return_pct": round(total_return, 2),
        "buy_hold_return_pct": round(buy_hold_return, 2),
        "alpha": round(total_return - buy_hold_return, 2),
        "total_trades": len(trades),
        "sharpe_ratio": round(sharpe, 3),
        "max_drawdown_pct": round(max_dd * 100, 2),
        "trades": trades[-10:],  # Last 10 trades
        "verdict": "OUTPERFORMED" if total_return > buy_hold_return else "UNDERPERFORMED",
        "timestamp": datetime.now().isoformat(),
        "source": "Yahoo Finance"
    }


@mcp.tool()
def simulate_portfolio_rebalance(
    current_positions: List[Dict[str, Any]],
    target_allocation: Dict[str, float]
) -> Dict[str, Any]:
    """
    Simulate portfolio rebalancing with real current prices.

    Args:
        current_positions: List of {symbol, quantity, avg_price}
        target_allocation: Target weights {symbol: weight} (must sum to 1.0)

    Returns:
        Rebalancing plan with required trades and cost estimates
    """
    # Fetch current prices
    total_value = 0
    positions = []

    for pos in current_positions:
        prices = _fetch_historical(pos["symbol"], "5d")
        if prices:
            current_price = prices[-1]["close"]
        else:
            current_price = pos.get("avg_price", 0)

        value = pos["quantity"] * current_price
        total_value += value
        positions.append({
            "symbol": pos["symbol"],
            "quantity": pos["quantity"],
            "avg_price": pos.get("avg_price", current_price),
            "current_price": current_price,
            "current_value": round(value, 2),
            "pnl": round((current_price - pos.get("avg_price", current_price)) * pos["quantity"], 2)
        })

    if total_value == 0:
        return {"error": "Portfolio has zero value"}

    # Calculate current vs target weights
    trades_needed = []
    for pos in positions:
        current_weight = pos["current_value"] / total_value
        target_weight = target_allocation.get(pos["symbol"], 0)
        diff_weight = target_weight - current_weight
        diff_value = diff_weight * total_value
        diff_shares = int(diff_value / pos["current_price"]) if pos["current_price"] > 0 else 0

        trades_needed.append({
            "symbol": pos["symbol"],
            "current_weight": round(current_weight * 100, 2),
            "target_weight": round(target_weight * 100, 2),
            "action": "BUY" if diff_shares > 0 else "SELL" if diff_shares < 0 else "HOLD",
            "shares": abs(diff_shares),
            "estimated_value": round(abs(diff_value), 2),
            "current_price": pos["current_price"]
        })

    return {
        "portfolio_value": round(total_value, 2),
        "positions": positions,
        "rebalance_trades": trades_needed,
        "trades_required": sum(1 for t in trades_needed if t["action"] != "HOLD"),
        "timestamp": datetime.now().isoformat(),
        "source": "Yahoo Finance"
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
    risk_amount = account_value * (risk_per_trade_pct / 100)
    price_risk = abs(entry_price - stop_loss_price)

    if price_risk <= 0:
        return {"error": "Stop loss must differ from entry price"}

    shares = int(risk_amount / price_risk)
    position_value = shares * entry_price
    position_pct = (position_value / account_value) * 100
    actual_risk = shares * price_risk

    # Risk/reward for common targets
    reward_1r = entry_price + price_risk if entry_price > stop_loss_price else entry_price - price_risk
    reward_2r = entry_price + 2 * price_risk if entry_price > stop_loss_price else entry_price - 2 * price_risk
    reward_3r = entry_price + 3 * price_risk if entry_price > stop_loss_price else entry_price - 3 * price_risk

    return {
        "recommended_shares": shares,
        "position_value": round(position_value, 2),
        "position_pct": round(position_pct, 2),
        "risk_amount": round(actual_risk, 2),
        "risk_pct": round((actual_risk / account_value) * 100, 2),
        "entry_price": entry_price,
        "stop_loss": stop_loss_price,
        "risk_per_share": round(price_risk, 2),
        "targets": {
            "1R": round(reward_1r, 2),
            "2R": round(reward_2r, 2),
            "3R": round(reward_3r, 2)
        },
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    mcp.run()
