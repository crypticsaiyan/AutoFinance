"""
AutoFinance Market Server

Real-time market data provider.
- Live price data
- Historical candles
- Volatility calculations

Tools:
- get_live_price: Get current market price
- get_candles: Get historical OHLCV data
- calculate_volatility: Calculate price volatility
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import math
import random


# Initialize MCP Server
mcp = FastMCP("auto-finance-market")


# Simulation mode for deterministic demo
SIMULATION_MODE = {
    "enabled": False,
    "prices": {
        "BTCUSDT": 48000.0,
        "ETHUSDT": 2800.0,
        "SOLUSDT": 110.0
    },
    "volatility_multiplier": 1.0
}


def generate_mock_price(symbol: str, base_price: float, volatility: float = 0.02) -> float:
    """Generate realistic mock price with volatility"""
    if SIMULATION_MODE["enabled"]:
        return SIMULATION_MODE["prices"].get(symbol, base_price)
    
    # Random walk with drift
    change = random.gauss(0, volatility)
    return base_price * (1 + change)


def generate_mock_candles(symbol: str, base_price: float, periods: int) -> List[Dict]:
    """Generate realistic OHLCV candle data"""
    candles = []
    current_price = base_price
    
    now = datetime.utcnow()
    
    for i in range(periods):
        timestamp = now - timedelta(hours=periods - i)
        
        # Generate OHLC with realistic movements
        open_price = current_price
        high_price = open_price * random.uniform(1.0, 1.02)
        low_price = open_price * random.uniform(0.98, 1.0)
        close_price = random.uniform(low_price, high_price)
        volume = random.uniform(1000, 10000)
        
        candles.append({
            "timestamp": timestamp.isoformat(),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": round(volume, 2)
        })
        
        current_price = close_price
    
    return candles


@mcp.tool()
def get_live_price(symbol: str) -> Dict[str, Any]:
    """
    Get current live price for a symbol.
    
    In production, this would call Binance API.
    For demo, uses deterministic simulation.
    """
    # Base prices for common symbols
    base_prices = {
        "BTCUSDT": 48000.0,
        "ETHUSDT": 2800.0,
        "SOLUSDT": 110.0,
        "BNBUSDT": 580.0,
        "ADAUSDT": 0.58
    }
    
    base_price = base_prices.get(symbol, 100.0)
    
    if SIMULATION_MODE["enabled"]:
        current_price = SIMULATION_MODE["prices"].get(symbol, base_price)
    else:
        # Simulate slight price movement
        current_price = generate_mock_price(symbol, base_price, volatility=0.005)
    
    return {
        "symbol": symbol,
        "price": round(current_price, 2),
        "timestamp": datetime.utcnow().isoformat(),
        "source": "simulation" if SIMULATION_MODE["enabled"] else "live_mock"
    }


@mcp.tool()
def get_candles(
    symbol: str,
    interval: str = "1h",
    limit: int = 24
) -> Dict[str, Any]:
    """
    Get historical OHLCV candle data.
    
    Args:
        symbol: Trading pair symbol
        interval: Candle interval (1h, 4h, 1d)
        limit: Number of candles to return
    """
    base_prices = {
        "BTCUSDT": 48000.0,
        "ETHUSDT": 2800.0,
        "SOLUSDT": 110.0,
        "BNBUSDT": 580.0,
        "ADAUSDT": 0.58
    }
    
    base_price = base_prices.get(symbol, 100.0)
    candles = generate_mock_candles(symbol, base_price, limit)
    
    return {
        "symbol": symbol,
        "interval": interval,
        "candles": candles,
        "count": len(candles),
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def calculate_volatility(symbol: str, period: int = 24) -> Dict[str, Any]:
    """
    Calculate price volatility over a period.
    
    Returns annualized volatility as a percentage.
    """
    # Get historical data
    candles_data = get_candles(symbol, limit=period)
    candles = candles_data["candles"]
    
    if len(candles) < 2:
        return {
            "symbol": symbol,
            "volatility": 0.0,
            "error": "Insufficient data"
        }
    
    # Calculate returns
    returns = []
    for i in range(1, len(candles)):
        prev_close = candles[i-1]["close"]
        curr_close = candles[i]["close"]
        ret = (curr_close - prev_close) / prev_close
        returns.append(ret)
    
    # Calculate standard deviation of returns
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    std_dev = math.sqrt(variance)
    
    # Annualize (assuming hourly data -> 24 * 365 periods per year)
    annualized_volatility = std_dev * math.sqrt(24 * 365)
    
    # Apply simulation multiplier if in special mode
    if SIMULATION_MODE["enabled"]:
        annualized_volatility *= SIMULATION_MODE["volatility_multiplier"]
    
    return {
        "symbol": symbol,
        "volatility": round(annualized_volatility, 4),
        "period": period,
        "risk_level": "HIGH" if annualized_volatility > 0.5 else "MEDIUM" if annualized_volatility > 0.3 else "LOW",
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def get_market_overview(symbols: List[str]) -> Dict[str, Any]:
    """
    Get market overview for multiple symbols.
    """
    overview = []
    
    for symbol in symbols:
        price_data = get_live_price(symbol)
        vol_data = calculate_volatility(symbol)
        
        overview.append({
            "symbol": symbol,
            "price": price_data["price"],
            "volatility": vol_data["volatility"],
            "risk_level": vol_data["risk_level"]
        })
    
    return {
        "markets": overview,
        "count": len(overview),
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def set_simulation_mode(
    enabled: bool,
    prices: Optional[Dict[str, float]] = None,
    volatility_multiplier: float = 1.0
) -> Dict[str, Any]:
    """
    Configure simulation mode (for deterministic demos).
    
    Args:
        enabled: Enable/disable simulation mode
        prices: Fixed prices for symbols
        volatility_multiplier: Multiply volatility calculations
    """
    SIMULATION_MODE["enabled"] = enabled
    
    if prices:
        SIMULATION_MODE["prices"].update(prices)
    
    SIMULATION_MODE["volatility_multiplier"] = volatility_multiplier
    
    return {
        "success": True,
        "simulation_mode": SIMULATION_MODE,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    mcp.run()
