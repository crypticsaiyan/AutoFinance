"""
AutoFinance Volatility Server

Advanced volatility analysis and risk scoring.
- Historical volatility
- Volatility regime detection
- Risk scoring

Tools:
- get_volatility_score: Get comprehensive volatility assessment
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any
import math
import random


# Initialize MCP Server
mcp = FastMCP("auto-finance-volatility")


# Simulation mode
SIMULATION_MODE = {
    "enabled": False,
    "volatility_scores": {}  # {symbol: score}
}


def generate_mock_prices(base_price: float, count: int = 100, volatility_factor: float = 1.0) -> list:
    """Generate mock price series with controlled volatility"""
    prices = [base_price]
    
    for _ in range(count - 1):
        change = random.gauss(0, 0.02 * volatility_factor)
        next_price = prices[-1] * (1 + change)
        prices.append(next_price)
    
    return prices


def calculate_historical_volatility(prices: list, period: int = 30) -> float:
    """Calculate historical volatility from price series"""
    if len(prices) < 2:
        return 0.0
    
    returns = []
    for i in range(1, min(len(prices), period + 1)):
        ret = (prices[i] - prices[i-1]) / prices[i-1]
        returns.append(ret)
    
    if not returns:
        return 0.0
    
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    std_dev = math.sqrt(variance)
    
    # Annualize
    annualized_vol = std_dev * math.sqrt(365)
    
    return annualized_vol


def calculate_volatility_regime(current_vol: float, historical_vols: list) -> str:
    """Determine volatility regime"""
    if not historical_vols:
        return "NORMAL"
    
    avg_vol = sum(historical_vols) / len(historical_vols)
    
    if current_vol > avg_vol * 1.5:
        return "HIGH"
    elif current_vol < avg_vol * 0.7:
        return "LOW"
    else:
        return "NORMAL"


@mcp.tool()
def get_volatility_score(symbol: str, current_price: float) -> Dict[str, Any]:
    """
    Get comprehensive volatility assessment for a symbol.
    
    Returns:
        volatility: Annualized volatility percentage
        risk_level: LOW, MEDIUM, HIGH
        regime: Current volatility regime
        score: 0-1 risk score
    """
    # Check simulation mode
    if SIMULATION_MODE["enabled"] and symbol in SIMULATION_MODE["volatility_scores"]:
        return SIMULATION_MODE["volatility_scores"][symbol]
    
    # Generate mock price history
    prices = generate_mock_prices(current_price, count=100)
    
    # Calculate volatilities for different periods
    vol_30d = calculate_historical_volatility(prices, period=30)
    vol_60d = calculate_historical_volatility(prices, period=60)
    vol_90d = calculate_historical_volatility(prices, period=90)
    
    # Use 30-day as current volatility
    current_volatility = vol_30d
    
    # Determine regime
    historical_vols = [vol_30d, vol_60d, vol_90d]
    regime = calculate_volatility_regime(current_volatility, historical_vols)
    
    # Calculate risk score (0-1)
    # Based on volatility thresholds
    if current_volatility < 0.2:
        risk_level = "LOW"
        risk_score = current_volatility / 0.2 * 0.3  # 0-0.3
    elif current_volatility < 0.5:
        risk_level = "MEDIUM"
        risk_score = 0.3 + (current_volatility - 0.2) / 0.3 * 0.4  # 0.3-0.7
    else:
        risk_level = "HIGH"
        risk_score = 0.7 + min((current_volatility - 0.5) / 0.5 * 0.3, 0.3)  # 0.7-1.0
    
    return {
        "symbol": symbol,
        "volatility": round(current_volatility, 4),
        "volatility_30d": round(vol_30d, 4),
        "volatility_60d": round(vol_60d, 4),
        "volatility_90d": round(vol_90d, 4),
        "risk_level": risk_level,
        "regime": regime,
        "risk_score": round(risk_score, 3),
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def compare_volatility(symbols: list) -> Dict[str, Any]:
    """
    Compare volatility across multiple symbols.
    """
    base_prices = {
        "BTCUSDT": 48000.0,
        "ETHUSDT": 2800.0,
        "SOLUSDT": 110.0,
        "BNBUSDT": 580.0
    }
    
    comparison = []
    
    for symbol in symbols:
        price = base_prices.get(symbol, 100.0)
        vol_data = get_volatility_score(symbol, price)
        
        comparison.append({
            "symbol": symbol,
            "volatility": vol_data["volatility"],
            "risk_level": vol_data["risk_level"],
            "risk_score": vol_data["risk_score"]
        })
    
    # Sort by volatility
    comparison.sort(key=lambda x: x["volatility"], reverse=True)
    
    return {
        "symbols": comparison,
        "count": len(comparison),
        "highest_volatility": comparison[0] if comparison else None,
        "lowest_volatility": comparison[-1] if comparison else None,
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def get_volatility_forecast(symbol: str, current_price: float, days_ahead: int = 7) -> Dict[str, Any]:
    """
    Forecast volatility for upcoming period.
    
    Simple forecast based on recent trends.
    """
    vol_data = get_volatility_score(symbol, current_price)
    
    current_vol = vol_data["volatility"]
    vol_30d = vol_data["volatility_30d"]
    vol_60d = vol_data["volatility_60d"]
    
    # Simple trend-based forecast
    trend = (vol_30d - vol_60d) / vol_60d if vol_60d > 0 else 0
    forecast_vol = current_vol * (1 + trend * 0.5)  # Dampen trend
    
    return {
        "symbol": symbol,
        "current_volatility": round(current_vol, 4),
        "forecast_volatility": round(forecast_vol, 4),
        "forecast_days": days_ahead,
        "trend": "INCREASING" if trend > 0.1 else "DECREASING" if trend < -0.1 else "STABLE",
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def set_simulation_volatility(symbol: str, volatility: float, risk_level: str) -> Dict[str, Any]:
    """
    Set deterministic volatility for demo mode.
    """
    SIMULATION_MODE["enabled"] = True
    SIMULATION_MODE["volatility_scores"][symbol] = {
        "symbol": symbol,
        "volatility": volatility,
        "volatility_30d": volatility,
        "volatility_60d": volatility,
        "volatility_90d": volatility,
        "risk_level": risk_level,
        "regime": "SIMULATED",
        "risk_score": volatility,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return {
        "success": True,
        "symbol": symbol,
        "configured_volatility": volatility,
        "risk_level": risk_level,
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def clear_simulation_mode() -> Dict[str, Any]:
    """Clear simulation mode."""
    SIMULATION_MODE["enabled"] = False
    SIMULATION_MODE["volatility_scores"] = {}
    
    return {
        "success": True,
        "message": "Simulation mode cleared",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    mcp.run()
