"""
AutoFinance Technical Analysis Server

Technical indicator analysis and signal generation.
- SMA (Simple Moving Average)
- RSI (Relative Strength Index)
- Signal generation

Tools:
- generate_signal: Generate trading signal with confidence
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, Literal
import random


# Initialize MCP Server
mcp = FastMCP("auto-finance-technical")


# Simulation mode for deterministic signals
SIMULATION_MODE = {
    "enabled": False,
    "signals": {}  # {symbol: {signal, confidence}}
}


def calculate_sma(prices: list, period: int = 20) -> float:
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return sum(prices) / len(prices)
    return sum(prices[-period:]) / period


def calculate_rsi(prices: list, period: int = 14) -> float:
    """Calculate Relative Strength Index"""
    if len(prices) < period + 1:
        return 50.0  # Neutral
    
    # Calculate price changes
    changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    # Separate gains and losses
    gains = [change if change > 0 else 0 for change in changes[-period:]]
    losses = [-change if change < 0 else 0 for change in changes[-period:]]
    
    # Calculate average gain and loss
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def generate_mock_prices(base_price: float, count: int = 50) -> list:
    """Generate mock price series for analysis"""
    prices = [base_price]
    
    for _ in range(count - 1):
        change = random.gauss(0, 0.02)
        next_price = prices[-1] * (1 + change)
        prices.append(next_price)
    
    return prices


@mcp.tool()
def generate_signal(symbol: str, current_price: float) -> Dict[str, Any]:
    """
    Generate trading signal based on technical analysis.
    
    Internally computes SMA, RSI, and other indicators.
    Returns unified signal with confidence score.
    
    Args:
        symbol: Trading pair symbol
        current_price: Current market price
    
    Returns:
        signal: BUY, SELL, or HOLD
        confidence: 0.0 to 1.0
        indicators: Technical indicator values
    """
    # Check simulation mode first
    if SIMULATION_MODE["enabled"] and symbol in SIMULATION_MODE["signals"]:
        sim_data = SIMULATION_MODE["signals"][symbol]
        return {
            "symbol": symbol,
            "signal": sim_data["signal"],
            "confidence": sim_data["confidence"],
            "indicators": sim_data.get("indicators", {}),
            "reason": sim_data.get("reason", "Simulated signal"),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "simulation"
        }
    
    # Generate mock historical prices
    prices = generate_mock_prices(current_price, count=50)
    
    # Calculate indicators
    sma_20 = calculate_sma(prices, period=20)
    sma_50 = calculate_sma(prices, period=50)
    rsi = calculate_rsi(prices, period=14)
    
    # Generate signal based on indicators
    indicators = {
        "sma_20": round(sma_20, 2),
        "sma_50": round(sma_50, 2),
        "rsi": round(rsi, 2),
        "current_price": current_price
    }
    
    # Signal logic
    signal = "HOLD"
    confidence = 0.5
    reasons = []
    
    # RSI signals
    if rsi < 30:
        signal = "BUY"
        reasons.append("RSI oversold")
        confidence += 0.15
    elif rsi > 70:
        signal = "SELL"
        reasons.append("RSI overbought")
        confidence += 0.15
    
    # SMA crossover signals
    if current_price > sma_20 and sma_20 > sma_50:
        if signal == "BUY" or signal == "HOLD":
            signal = "BUY"
            reasons.append("Bullish trend - price above SMAs")
            confidence += 0.10
    elif current_price < sma_20 and sma_20 < sma_50:
        if signal == "SELL" or signal == "HOLD":
            signal = "SELL"
            reasons.append("Bearish trend - price below SMAs")
            confidence += 0.10
    
    # Momentum signal
    if current_price > sma_20:
        reasons.append("Positive momentum")
        if signal == "BUY":
            confidence += 0.05
    else:
        reasons.append("Negative momentum")
        if signal == "SELL":
            confidence += 0.05
    
    # Normalize confidence
    confidence = min(confidence, 0.95)
    confidence = max(confidence, 0.40)
    
    reason = "; ".join(reasons) if reasons else "Neutral technical setup"
    
    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": round(confidence, 3),
        "indicators": indicators,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "technical_analysis"
    }


@mcp.tool()
def analyze_trend(symbol: str, current_price: float, timeframe: str = "short") -> Dict[str, Any]:
    """
    Analyze price trend for a symbol.
    
    Args:
        timeframe: 'short' (20 period) or 'long' (50 period)
    """
    prices = generate_mock_prices(current_price, count=50)
    
    period = 20 if timeframe == "short" else 50
    sma = calculate_sma(prices, period=period)
    
    trend = "BULLISH" if current_price > sma else "BEARISH"
    strength = abs(current_price - sma) / sma
    
    return {
        "symbol": symbol,
        "trend": trend,
        "strength": round(strength, 4),
        "sma": round(sma, 2),
        "current_price": current_price,
        "timeframe": timeframe,
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def get_support_resistance(symbol: str, current_price: float) -> Dict[str, Any]:
    """
    Calculate support and resistance levels.
    """
    prices = generate_mock_prices(current_price, count=50)
    
    # Simple support/resistance based on recent highs/lows
    resistance = max(prices[-20:])
    support = min(prices[-20:])
    
    return {
        "symbol": symbol,
        "support": round(support, 2),
        "resistance": round(resistance, 2),
        "current_price": current_price,
        "distance_to_support": round((current_price - support) / current_price, 4),
        "distance_to_resistance": round((resistance - current_price) / current_price, 4),
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def set_simulation_signal(
    symbol: str,
    signal: Literal["BUY", "SELL", "HOLD"],
    confidence: float,
    reason: str = "Simulated"
) -> Dict[str, Any]:
    """
    Set deterministic signal for demo mode.
    
    Args:
        symbol: Trading pair
        signal: BUY, SELL, or HOLD
        confidence: 0.0 to 1.0
        reason: Explanation
    """
    SIMULATION_MODE["enabled"] = True
    SIMULATION_MODE["signals"][symbol] = {
        "signal": signal,
        "confidence": confidence,
        "reason": reason,
        "indicators": {
            "sma_20": 0,
            "sma_50": 0,
            "rsi": 50
        }
    }
    
    return {
        "success": True,
        "symbol": symbol,
        "configured_signal": signal,
        "confidence": confidence,
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def clear_simulation_mode() -> Dict[str, Any]:
    """
    Clear simulation mode and return to live analysis.
    """
    SIMULATION_MODE["enabled"] = False
    SIMULATION_MODE["signals"] = {}
    
    return {
        "success": True,
        "message": "Simulation mode cleared",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    mcp.run()
