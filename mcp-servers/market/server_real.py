"""
AutoFinance Market Server - REAL DATA VERSION

Real-time market data provider using Yahoo Finance.
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
import yfinance as yf
import pandas as pd
import numpy as np
from functools import lru_cache
import time

# Initialize MCP Server
mcp = FastMCP("auto-finance-market")

# Price cache to avoid rate limiting
_price_cache = {}
_CACHE_TTL = 60  # seconds


def _get_ticker_symbol(symbol: str) -> str:
    """Convert symbol to Yahoo Finance format."""
    # Crypto symbols need conversion
    crypto_map = {
        "BTCUSDT": "BTC-USD",
        "ETHUSDT": "ETH-USD",
        "SOLUSDT": "SOL-USD",
        "BNBUSDT": "BNB-USD",
    }
    return crypto_map.get(symbol, symbol)


@mcp.tool()
def get_live_price(symbol: str) -> Dict[str, Any]:
    """
    Get real-time market price for a symbol.
    
    Args:
        symbol: Trading symbol (e.g., 'AAPL', 'BTCUSDT', 'TSLA')
    
    Returns:
        Dictionary with symbol, price, timestamp, and additional market data
    """
    # Check cache first
    cache_key = f"{symbol}:{int(time.time() // _CACHE_TTL)}"
    if cache_key in _price_cache:
        return _price_cache[cache_key]
    
    try:
        yf_symbol = _get_ticker_symbol(symbol)
        ticker = yf.Ticker(yf_symbol)
        
        # Get current data
        info = ticker.info
        hist = ticker.history(period="1d", interval="1m")
        
        if hist.empty:
            return {
                "error": f"No data available for {symbol}",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }
        
        current_price = hist['Close'].iloc[-1]
        
        result = {
            "symbol": symbol,
            "price": round(float(current_price), 2),
            "timestamp": datetime.now().isoformat(),
            "market_cap": info.get("marketCap"),
            "volume_24h": int(hist['Volume'].sum()) if len(hist) > 0 else None,
            "change_24h": round(float(hist['Close'].iloc[-1] - hist['Open'].iloc[0]), 2) if len(hist) > 1 else 0,
            "change_24h_pct": round(((hist['Close'].iloc[-1] / hist['Open'].iloc[0]) - 1) * 100, 2) if len(hist) > 1 else 0,
            "high_24h": round(float(hist['High'].max()), 2),
            "low_24h": round(float(hist['Low'].min()), 2),
            "source": "Yahoo Finance"
        }
        
        # Cache the result
        _price_cache[cache_key] = result
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
def get_candles(
    symbol: str,
    timeframe: str = "1h",
    periods: int = 24
) -> Dict[str, Any]:
    """
    Get historical OHLCV candlestick data.
    
    Args:
        symbol: Trading symbol
        timeframe: Candle timeframe (1m, 5m, 15m, 1h, 1d)
        periods: Number of candles to retrieve
    
    Returns:
        Dictionary with symbol, timeframe, and list of OHLCV candles
    """
    try:
        yf_symbol = _get_ticker_symbol(symbol)
        ticker = yf.Ticker(yf_symbol)
        
        # Map timeframe to yfinance parameters
        interval_map = {
            "1m": ("1d", "1m"),
            "5m": ("5d", "5m"),
            "15m": ("5d", "15m"),
            "1h": ("1mo", "1h"),
            "1d": ("1y", "1d"),
        }
        
        period, interval = interval_map.get(timeframe, ("1mo", "1h"))
        
        # Fetch data
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return {
                "error": f"No data available for {symbol}",
                "symbol": symbol,
                "timeframe": timeframe
            }
        
        # Take last N periods
        hist = hist.tail(periods)
        
        # Convert to candle format
        candles = []
        for idx, row in hist.iterrows():
            candles.append({
                "timestamp": idx.isoformat(),
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2),
                "volume": int(row['Volume'])
            })
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "periods": len(candles),
            "candles": candles,
            "source": "Yahoo Finance"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "symbol": symbol,
            "timeframe": timeframe
        }


@mcp.tool()
def calculate_volatility(
    symbol: str,
    periods: int = 30
) -> Dict[str, Any]:
    """
    Calculate historical volatility (standard deviation of returns).
    
    Args:
        symbol: Trading symbol
        periods: Number of periods for calculation (default 30 days)
    
    Returns:
        Dictionary with volatility metrics
    """
    try:
        yf_symbol = _get_ticker_symbol(symbol)
        ticker = yf.Ticker(yf_symbol)
        
        # Get daily data
        hist = ticker.history(period=f"{periods + 5}d", interval="1d")
        
        if len(hist) < 10:
            return {
                "error": "Insufficient data for volatility calculation",
                "symbol": symbol
            }
        
        # Calculate daily returns
        returns = hist['Close'].pct_change().dropna()
        
        # Calculate volatility (annualized)
        daily_volatility = returns.std()
        annualized_volatility = daily_volatility * np.sqrt(252)  # 252 trading days
        
        # Calculate additional metrics
        avg_return = returns.mean() * 252  # Annualized
        max_drawdown = ((hist['Close'] / hist['Close'].cummax()) - 1).min()
        
        return {
            "symbol": symbol,
            "volatility": round(float(annualized_volatility), 4),
            "volatility_pct": round(float(annualized_volatility * 100), 2),
            "avg_return_annualized": round(float(avg_return * 100), 2),
            "max_drawdown": round(float(max_drawdown * 100), 2),
            "periods_analyzed": len(returns),
            "risk_level": "LOW" if annualized_volatility < 0.2 else "MEDIUM" if annualized_volatility < 0.5 else "HIGH",
            "timestamp": datetime.now().isoformat(),
            "source": "Yahoo Finance"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "symbol": symbol
        }


@mcp.tool()
def get_market_overview() -> Dict[str, Any]:
    """
    Get overview of major market indices.
    
    Returns:
        Dictionary with major market index data
    """
    indices = {
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI",
        "NASDAQ": "^IXIC",
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD"
    }
    
    overview = {}
    
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d", interval="1d")
            
            if not hist.empty and len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2]
                change_pct = ((current / previous) - 1) * 100
                
                overview[name] = {
                    "price": round(float(current), 2),
                    "change_pct": round(float(change_pct), 2),
                    "trend": "UP" if change_pct > 0 else "DOWN"
                }
        except:
            overview[name] = {"error": "Data unavailable"}
    
    return {
        "timestamp": datetime.now().isoformat(),
        "indices": overview,
        "source": "Yahoo Finance"
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
