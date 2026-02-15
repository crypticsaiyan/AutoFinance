"""
AutoFinance Volatility Server

Advanced volatility analysis and risk scoring using REAL market data.
- Historical volatility from Yahoo Finance
- Volatility regime detection
- Risk scoring
- VIX-like calculations

Tools:
- calculate_historical_volatility: Calculate actual historical volatility
- detect_volatility_regime: Detect current volatility regime
- get_volatility_score: Get comprehensive volatility assessment
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, List
import math
import yfinance as yf


# Initialize MCP Server
mcp = FastMCP("auto-finance-volatility")


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


def get_real_historical_prices(symbol: str, period: str = "6mo", interval: str = "1d") -> List[float]:
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


def calculate_realized_volatility(prices: list, period: int = None) -> float:
    """
    Calculate historical volatility from price series using log returns.
    
    Args:
        prices: List of prices
        period: Number of periods to use (None = use all)
    
    Returns:
        Annualized volatility
    """
    if len(prices) < 2:
        return 0.0
    
    # Use specified period or all prices
    if period and len(prices) > period:
        prices_to_use = prices[-period:]
    else:
        prices_to_use = prices
    
    # Calculate log returns
    returns = []
    for i in range(1, len(prices_to_use)):
        if prices_to_use[i-1] > 0 and prices_to_use[i] > 0:
            ret = math.log(prices_to_use[i] / prices_to_use[i-1])
            returns.append(ret)
    
    if not returns:
        return 0.0
    
    # Calculate standard deviation
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    std_dev = math.sqrt(variance)
    
    # Annualize (assuming daily data)
    annualized_vol = std_dev * math.sqrt(252)  # 252 trading days per year
    
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
def calculate_historical_volatility(symbol: str, period: str = "6mo") -> Dict[str, Any]:
    """
    Calculate historical volatility from REAL market data.
    
    Args:
        symbol: Trading symbol (e.g., 'AAPL', 'BTCUSDT')
        period: Time period for analysis ('1mo', '3mo', '6mo', '1y')
    
    Returns:
        Annualized volatility and multiple timeframe analysis
    """
    # Fetch real historical prices
    prices = get_real_historical_prices(symbol, period=period, interval="1d")
    
    if not prices or len(prices) < 10:
        return {
            "symbol": symbol,
            "error": "Insufficient historical data",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Calculate volatilities for different windows
    vol_30d = calculate_realized_volatility(prices, period=30) if len(prices) >= 30 else 0.0
    vol_60d = calculate_realized_volatility(prices, period=60) if len(prices) >= 60 else 0.0
    vol_90d = calculate_realized_volatility(prices, period=90) if len(prices) >= 90 else 0.0
    vol_all = calculate_realized_volatility(prices)
    
    # Use 30-day as current volatility
    current_volatility = vol_30d if vol_30d > 0 else vol_all
    
    # Determine regime
    historical_vols = [v for v in [vol_30d, vol_60d, vol_90d] if v > 0]
    regime = calculate_volatility_regime(current_volatility, historical_vols)
    
    return {
        "symbol": symbol,
        "volatility_30d": round(vol_30d * 100, 2),  # As percentage
        "volatility_60d": round(vol_60d * 100, 2),
        "volatility_90d": round(vol_90d * 100, 2),
        "volatility_all_period": round(vol_all * 100, 2),
        "current_volatility": round(current_volatility * 100, 2),
        "regime": regime,
        "data_points": len(prices),
        "timestamp": datetime.utcnow().isoformat(),
        "source": "yahoo_finance"
    }


@mcp.tool()
def detect_volatility_regime(symbol: str) -> Dict[str, Any]:
    """
    Detect current volatility regime (LOW, NORMAL, HIGH) from REAL data.
    
    Args:
        symbol: Trading symbol
    
    Returns:
        Current regime and historical context
    """
    # Fetch 1 year of data for context
    prices = get_real_historical_prices(symbol, period="1y", interval="1d")
    
    if not prices or len(prices) < 60:
        return {
            "symbol": symbol,
            "error": "Insufficient historical data",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Calculate rolling 30-day volatilities
    rolling_vols = []
    for i in range(30, len(prices)):
        window_prices = prices[i-30:i+1]
        vol = calculate_realized_volatility(window_prices, period=30)
        rolling_vols.append(vol)
    
    current_vol = rolling_vols[-1] if rolling_vols else 0.0
    avg_vol = sum(rolling_vols) / len(rolling_vols) if rolling_vols else 0.0
    
    # Determine regime
    regime = calculate_volatility_regime(current_vol, rolling_vols)
    
    # Calculate percentile
    sorted_vols = sorted(rolling_vols)
    percentile = (sorted_vols.index(min(sorted_vols, key=lambda x: abs(x - current_vol))) / len(sorted_vols)) * 100
    
    return {
        "symbol": symbol,
        "regime": regime,
        "current_volatility": round(current_vol * 100, 2),
        "average_volatility": round(avg_vol * 100, 2),
        "percentile": round(percentile, 1),
        "interpretation": f"Current volatility is at {percentile:.0f}th percentile over past year",
        "timestamp": datetime.utcnow().isoformat(),
        "source": "yahoo_finance"
    }


@mcp.tool()
def get_volatility_score(symbol: str) -> Dict[str, Any]:
    """
    Get comprehensive volatility assessment with risk scoring from REAL data.
    
    Args:
        symbol: Trading symbol
    
    Returns:
        volatility: Annualized volatility percentage
        risk_level: LOW, MEDIUM, HIGH
        regime: Current volatility regime
        score: 0-1 risk score
    """
    # Fetch real historical prices (6 months for comprehensive analysis)
    prices = get_real_historical_prices(symbol, period="6mo", interval="1d")
    
    if not prices or len(prices) < 30:
        return {
            "symbol": symbol,
            "error": "Insufficient historical data",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Calculate volatilities for different periods
    vol_30d = calculate_realized_volatility(prices, period=30) if len(prices) >= 30 else 0.0
    vol_60d = calculate_realized_volatility(prices, period=60) if len(prices) >= 60 else 0.0
    vol_90d = calculate_realized_volatility(prices, period=90) if len(prices) >= 90 else 0.0
    
    # Use 30-day as current volatility
    current_volatility = vol_30d
    
    # Determine regime
    historical_vols = [v for v in [vol_30d, vol_60d, vol_90d] if v > 0]
    regime = calculate_volatility_regime(current_volatility, historical_vols)
    
    # Calculate risk score (0-1) and level
    # Thresholds based on typical equity volatility ranges
    # Low: <15%, Medium: 15-30%, High: >30%
    if current_volatility < 0.15:
        risk_level = "LOW"
        risk_score = current_volatility / 0.15 * 0.3  # 0-0.3
    elif current_volatility < 0.30:
        risk_level = "MEDIUM"
        risk_score = 0.3 + (current_volatility - 0.15) / 0.15 * 0.4  # 0.3-0.7
    else:
        risk_level = "HIGH"
        risk_score = 0.7 + min((current_volatility - 0.30) / 0.70 * 0.3, 0.3)  # 0.7-1.0
    
    # Calculate price range for context
    min_price = min(prices)
    max_price = max(prices)
    current_price = prices[-1]
    price_range_pct = ((max_price - min_price) / min_price) * 100
    
    return {
        "symbol": symbol,
        "volatility": round(current_volatility, 4),
        "volatility_pct": round(current_volatility * 100, 2),
        "volatility_30d": round(vol_30d * 100, 2),
        "volatility_60d": round(vol_60d * 100, 2),
        "volatility_90d": round(vol_90d * 100, 2),
        "risk_level": risk_level,
        "regime": regime,
        "risk_score": round(risk_score, 3),
        "price_range_pct": round(price_range_pct, 2),
        "current_price": round(current_price, 2),
        "data_points": len(prices),
        "timestamp": datetime.utcnow().isoformat(),
        "source": "yahoo_finance"
    }


@mcp.tool()
def compare_volatility(symbols: List[str]) -> Dict[str, Any]:
    """
    Compare volatility across multiple symbols using REAL data.
    
    Args:
        symbols: List of trading symbols to compare
    
    Returns:
        Comparison data with rankings
    """
    comparison = []
    
    for symbol in symbols:
        vol_data = get_volatility_score(symbol)
        
        if "error" not in vol_data:
            comparison.append({
                "symbol": symbol,
                "volatility": vol_data["volatility_pct"],
                "risk_level": vol_data["risk_level"],
                "risk_score": vol_data["risk_score"],
                "regime": vol_data["regime"]
            })
    
    # Sort by volatility (highest first)
    comparison.sort(key=lambda x: x["volatility"], reverse=True)
    
    # Calculate statistics
    vols = [c["volatility"] for c in comparison]
    avg_vol = sum(vols) / len(vols) if vols else 0
    
    return {
        "symbols": comparison,
        "count": len(comparison),
        "highest_volatility": comparison[0] if comparison else None,
        "lowest_volatility": comparison[-1] if comparison else None,
        "average_volatility": round(avg_vol, 2),
        "timestamp": datetime.utcnow().isoformat(),
        "source": "yahoo_finance"
    }


@mcp.tool()
def calculate_volatility(symbol: str, periods: int = 30) -> Dict[str, Any]:
    """
    Calculate volatility for a symbol. Alias for calculate_historical_volatility.

    Args:
        symbol: Trading symbol (e.g., 'AAPL', 'BTCUSDT')
        periods: Number of days (maps to period: 30→1mo, 60→3mo, 90→6mo)
    """
    period_map = {30: "1mo", 60: "3mo", 90: "6mo", 180: "1y", 365: "2y"}
    period = period_map.get(periods, "3mo" if periods <= 60 else "6mo" if periods <= 180 else "1y")
    return calculate_historical_volatility(symbol, period)


if __name__ == "__main__":
    mcp.run()
