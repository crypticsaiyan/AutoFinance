"""
AutoFinance Technical Analysis Server

Technical indicator analysis and signal generation using REAL market data.
- SMA (Simple Moving Average)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Signal generation

Tools:
- generate_signal: Generate trading signal with confidence
- calculate_rsi: Calculate RSI indicator
- calculate_macd: Calculate MACD indicator
- calculate_bollinger_bands: Calculate Bollinger Bands
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, Literal, List
import yfinance as yf
import numpy as np


# Initialize MCP Server
mcp = FastMCP("auto-finance-technical")


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
        # If the base is a known crypto, use the crypto format
        if base in crypto_map:
            return crypto_map[base]
        # Otherwise assume it's a stock
        return base
        
    # 3. Check -USD format
    if s.endswith("-USD"):
        return s
        
    # 4. Default to generic (usually stock)
    return s


def get_real_historical_prices(symbol: str, period: str = "3mo", interval: str = "1d") -> List[float]:
    """
    Fetch real historical prices from Yahoo Finance.
    
    Args:
        symbol: Trading symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        List of closing prices
    """
    try:
        yf_symbol = _get_ticker_symbol(symbol)
        ticker = yf.Ticker(yf_symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return []
        
        return hist['Close'].tolist()
    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {e}")
        return []


def calculate_sma(prices: list, period: int = 20) -> float:
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return sum(prices) / len(prices) if prices else 0
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




def calculate_ema(prices: list, period: int = 12) -> List[float]:
    """Calculate Exponential Moving Average"""
    if not prices or len(prices) < period:
        return []
    
    multiplier = 2 / (period + 1)
    ema = [sum(prices[:period]) / period]  # Start with SMA
    
    for price in prices[period:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    
    return ema


def calculate_macd(prices: list) -> Dict[str, float]:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    Returns MACD line, signal line, and histogram.
    """
    if len(prices) < 26:
        return {"macd": 0, "signal": 0, "histogram": 0}
    
    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)
    
    if not ema_12 or not ema_26:
        return {"macd": 0, "signal": 0, "histogram": 0}
    
    # MACD line
    macd_line = [ema_12[i + 14] - ema_26[i] for i in range(len(ema_26))]
    
    # Signal line (9-day EMA of MACD)
    if len(macd_line) < 9:
        return {"macd": macd_line[-1] if macd_line else 0, "signal": 0, "histogram": 0}
    
    signal_line = calculate_ema(macd_line, 9)
    
    macd_val = macd_line[-1]
    signal_val = signal_line[-1] if signal_line else 0
    histogram = macd_val - signal_val
    
    return {
        "macd": round(macd_val, 2),
        "signal": round(signal_val, 2),
        "histogram": round(histogram, 2)
    }


def calculate_bollinger_bands(prices: list, period: int = 20, std_dev: int = 2) -> Dict[str, float]:
    """Calculate Bollinger Bands"""
    if len(prices) < period:
        avg = sum(prices) / len(prices) if prices else 0
        return {"upper": avg, "middle": avg, "lower": avg}
    
    recent_prices = prices[-period:]
    sma = sum(recent_prices) / period
    variance = sum((p - sma) ** 2 for p in recent_prices) / period
    std = variance ** 0.5
    
    return {
        "upper": round(sma + (std_dev * std), 2),
        "middle": round(sma, 2),
        "lower": round(sma - (std_dev * std), 2)
    }


@mcp.tool()
def generate_signal(symbol: str, timeframe: str = "3mo") -> Dict[str, Any]:
    """
    Generate trading signal based on REAL technical analysis from Yahoo Finance.
    
    Uses multiple indicators:
    - SMA (20, 50, 200 day)
    - RSI (14 period)
    - MACD
    - Bollinger Bands
    
    Args:
        symbol: Trading symbol (e.g., 'AAPL', 'BTCUSDT')
        timeframe: Analysis timeframe ('1mo', '3mo', '6mo', '1y')
    
    Returns:
        signal: BUY, SELL, or HOLD
        confidence: 0.0 to 1.0
        indicators: All technical indicator values
        reasons: List of reasons for the signal
    """
    # Fetch REAL historical prices
    prices = get_real_historical_prices(symbol, period=timeframe, interval="1d")
    
    if not prices or len(prices) < 50:
        return {
            "symbol": symbol,
            "signal": "HOLD",
            "confidence": 0.0,
            "error": "Insufficient historical data",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    current_price = prices[-1]
    
    # Calculate ALL indicators
    sma_20 = calculate_sma(prices, period=20)
    sma_50 = calculate_sma(prices, period=50)
    sma_200 = calculate_sma(prices, period=200) if len(prices) >= 200 else sma_50
    rsi = calculate_rsi(prices, period=14)
    macd_data = calculate_macd(prices)
    bb_data = calculate_bollinger_bands(prices, period=20)
    
    # Collect indicator values
    indicators = {
        "current_price": round(current_price, 2),
        "sma_20": round(sma_20, 2),
        "sma_50": round(sma_50, 2),
        "sma_200": round(sma_200, 2),
        "rsi": round(rsi, 2),
        "macd": macd_data["macd"],
        "macd_signal": macd_data["signal"],
        "macd_histogram": macd_data["histogram"],
        "bb_upper": bb_data["upper"],
        "bb_middle": bb_data["middle"],
        "bb_lower": bb_data["lower"]
    }
    
    # Signal logic with multiple factors
    buy_signals = 0
    sell_signals = 0
    reasons = []
    
    # Trend analysis (Moving averages)
    if current_price > sma_20 > sma_50:
        buy_signals += 2
        reasons.append("Strong uptrend (price > SMA20 > SMA50)")
    elif current_price < sma_20 < sma_50:
        sell_signals += 2
        reasons.append("Strong downtrend (price < SMA20 < SMA50)")
    
    # RSI analysis
    if rsi < 30:
        buy_signals += 2
        reasons.append(f"Oversold RSI ({rsi:.1f})")
    elif rsi > 70:
        sell_signals += 2
        reasons.append(f"Overbought RSI ({rsi:.1f})")
    elif 40 <= rsi <= 60:
        reasons.append(f"Neutral RSI ({rsi:.1f})")
    
    # MACD analysis
    if macd_data["histogram"] > 0 and macd_data["macd"] > macd_data["signal"]:
        buy_signals += 1
        reasons.append("Bullish MACD crossover")
    elif macd_data["histogram"] < 0 and macd_data["macd"] < macd_data["signal"]:
        sell_signals += 1
        reasons.append("Bearish MACD crossover")
    
    # Bollinger Bands analysis
    if current_price < bb_data["lower"]:
        buy_signals += 1
        reasons.append("Price below lower Bollinger Band (potential bounce)")
    elif current_price > bb_data["upper"]:
        sell_signals += 1
        reasons.append("Price above upper Bollinger Band (potential reversal)")
    
    # Determine final signal
    total_signals = buy_signals + sell_signals
    
    if buy_signals > sell_signals and buy_signals >= 3:
        signal = "BUY"
        confidence = min(buy_signals / 6.0, 1.0)  # Max 6 possible buy signals
    elif sell_signals > buy_signals and sell_signals >= 3:
        signal = "SELL"
        confidence = min(sell_signals / 6.0, 1.0)
    else:
        signal = "HOLD"
        confidence = 0.3 + (abs(buy_signals - sell_signals) * 0.1)
        reasons.append("Mixed signals - no clear direction")
    
    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": round(confidence, 2),
        "indicators": indicators,
        "reasons": reasons,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "yahoo_finance",
        "data_points": len(prices)
    }


@mcp.tool()
def calculate_support_resistance(symbol: str, period: str = "6mo") -> Dict[str, Any]:
    """
    Calculate support and resistance levels from REAL price data.
    
    Args:
        symbol: Trading symbol
        period: Analysis period
    
    Returns:
        Support and resistance levels with strength indicators
    """
    prices = get_real_historical_prices(symbol, period=period, interval="1d")
    
    if not prices or len(prices) < 20:
        return {
            "error": "Insufficient data",
            "symbol": symbol
        }
    
    # Find local maxima (resistance) and minima (support)
    window = 5
    resistance_levels = []
    support_levels = []
    
    for i in range(window, len(prices) - window):
        # Check if this is a local maximum
        if all(prices[i] >= prices[i-j] for j in range(1, window+1)) and \
           all(prices[i] >= prices[i+j] for j in range(1, window+1)):
            resistance_levels.append(prices[i])
        
        # Check if this is a local minimum
        if all(prices[i] <= prices[i-j] for j in range(1, window+1)) and \
           all(prices[i] <= prices[i+j] for j in range(1, window+1)):
            support_levels.append(prices[i])
    
    # Cluster similar levels
    def cluster_levels(levels, tolerance=0.02):
        if not levels:
            return []
        
        clusters = []
        sorted_levels = sorted(levels)
        current_cluster = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] < tolerance:
                current_cluster.append(level)
            else:
                clusters.append(sum(current_cluster) / len(current_cluster))
                current_cluster = [level]
        
        if current_cluster:
            clusters.append(sum(current_cluster) / len(current_cluster))
        
        return clusters
    
    support = cluster_levels(support_levels)[-3:] if support_levels else []
    resistance = cluster_levels(resistance_levels)[-3:] if resistance_levels else []
    
    current_price = prices[-1]
    
    return {
        "symbol": symbol,
        "current_price": round(current_price, 2),
        "support_levels": [round(s, 2) for s in sorted(support)],
        "resistance_levels": [round(r, 2) for r in sorted(resistance, reverse=True)],
        "nearest_support": round(max([s for s in support if s < current_price], default=0), 2),
        "nearest_resistance": round(min([r for r in resistance if r > current_price], default=0), 2),
        "timestamp": datetime.utcnow().isoformat()
    }


# Keep old tools for calculation
@mcp.tool()
def calculate_rsi_tool(symbol: str, period: int = 14) -> Dict[str, Any]:
    """
    Calculate RSI indicator from REAL market data.
   
    Args:
        symbol: Trading symbol
        period: RSI period (default 14)
    
    Returns:
        RSI value and interpretation
    """
    prices = get_real_historical_prices(symbol, period="3mo", interval="1d")
    
    if not prices or len(prices) < period + 1:
        return {"error": "Insufficient data", "symbol": symbol}
    
    rsi = calculate_rsi(prices, period)
    
    interpretation = "NEUTRAL"
    if rsi < 30:
        interpretation = "OVERSOLD"
    elif rsi > 70:
        interpretation = "OVERBOUGHT"
    
    return {
        "symbol": symbol,
        "rsi": round(rsi, 2),
        "period": period,
        "interpretation": interpretation,
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def calculate_macd_tool(symbol: str) -> Dict[str, Any]:
    """
    Calculate MACD indicator from REAL market data.
    
    Args:
        symbol: Trading symbol
    
    Returns:
        MACD line, signal line, and histogram
    """
    prices = get_real_historical_prices(symbol, period="6mo", interval="1d")
    
    if not prices or len(prices) < 26:
        return {"error": "Insufficient data", "symbol": symbol}
    
    macd_data = calculate_macd(prices)
    
    trend = "BULLISH" if macd_data["histogram"] > 0 else "BEARISH"
    
    return {
        "symbol": symbol,
        "macd": macd_data["macd"],
        "signal": macd_data["signal"],
        "histogram": macd_data["histogram"],
        "trend": trend,
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def calculate_bollinger_bands_tool(symbol: str, period: int = 20) -> Dict[str, Any]:
    """
    Calculate Bollinger Bands from REAL market data.
    
    Args:
        symbol: Trading symbol
        period: Period for bands (default 20)
    
    Returns:
        Upper, middle, and lower bands with price position
    """
    prices = get_real_historical_prices(symbol, period="3mo", interval="1d")
    
    if not prices or len(prices) < period:
        return {"error": "Insufficient data", "symbol": symbol}
    
    bb_data = calculate_bollinger_bands(prices, period)
    current_price = prices[-1]
    
    # Determine position
    band_width = bb_data["upper"] - bb_data["lower"]
    if band_width > 0:
        position_pct = ((current_price - bb_data["lower"]) / band_width) * 100
    else:
        position_pct = 50
    
    position = "MIDDLE"
    if position_pct < 20:
        position = "LOWER_BAND"
    elif position_pct > 80:
        position = "UPPER_BAND"
    
    return {
        "symbol": symbol,
        "current_price": round(current_price, 2),
        "upper_band": bb_data["upper"],
        "middle_band": bb_data["middle"],
        "lower_band": bb_data["lower"],
        "position": position,
        "position_percent": round(position_pct, 1),
        "band_width": round(band_width, 2),
        "timestamp": datetime.utcnow().isoformat()
    }


# Deprecated mock price generator - kept for backward compatibility
def generate_mock_prices(base_price: float, count: int = 50) -> list:
    """DEPRECATED: Use get_real_historical_prices() instead"""
    return [base_price] * count


# --- Convenience Aliases for LLM compatibility ---

@mcp.tool()
def get_support_resistance(symbol: str, period: str = "6mo") -> Dict[str, Any]:
    """Alias for calculate_support_resistance"""
    return calculate_support_resistance(symbol, period)

@mcp.tool()
def analyze_trend(symbol: str) -> Dict[str, Any]:
    """Alias for calculate_macd_tool (trend analysis)"""
    return calculate_macd_tool(symbol)




if __name__ == "__main__":
    mcp.run()

