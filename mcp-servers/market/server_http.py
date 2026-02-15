"""
AutoFinance Market Server - HTTP/SSE Transport
Accessible via URL for remote MCP connections
"""

from mcp.server.fastmcp import FastMCP
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create MCP server instance
mcp = FastMCP("AutoFinance Market Server (Real Data)")

@mcp.tool()
def get_live_price(symbol: str) -> dict:
    """
    Get live price data for a stock or cryptocurrency.
    
    Args:
        symbol: Stock ticker (e.g., 'AAPL', 'TSLA') or crypto (e.g., 'BTC-USD')
    
    Returns:
        Current price, change, volume, and market data
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        
        # Get previous close for change calculation
        previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
        
        if current_price and previous_close:
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
        else:
            change = 0
            change_percent = 0
        
        return {
            "symbol": symbol,
            "current_price": round(current_price, 2) if current_price else 0,
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": info.get('volume', 0),
            "market_cap": info.get('marketCap', 0),
            "currency": info.get('currency', 'USD'),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": f"Failed to fetch price for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def get_candles(symbol: str, period: str = "1mo", interval: str = "1d") -> dict:
    """
    Get historical OHLCV (candles) data.
    
    Args:
        symbol: Stock ticker or crypto symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
        interval: Data interval (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)
    
    Returns:
        Historical OHLCV data
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return {"error": f"No data available for {symbol}", "symbol": symbol}
        
        # Convert to list of dicts for JSON serialization
        candles = []
        for idx, row in hist.iterrows():
            candles.append({
                "timestamp": idx.isoformat(),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume'])
            })
        
        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "candles": candles,
            "count": len(candles)
        }
    except Exception as e:
        return {
            "error": f"Failed to fetch candles for {symbol}: {str(e)}",
            "symbol": symbol
        }

@mcp.tool()
def calculate_volatility(symbol: str, period: str = "1mo") -> dict:
    """
    Calculate price volatility (standard deviation of returns).
    
    Args:
        symbol: Stock ticker or crypto symbol
        period: Time period for calculation
    
    Returns:
        Volatility metrics
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty or len(hist) < 2:
            return {"error": f"Insufficient data for {symbol}", "symbol": symbol}
        
        # Calculate daily returns
        returns = hist['Close'].pct_change().dropna()
        
        # Calculate volatility (annualized)
        daily_vol = returns.std()
        annual_vol = daily_vol * np.sqrt(252)  # 252 trading days
        
        return {
            "symbol": symbol,
            "period": period,
            "daily_volatility": round(daily_vol * 100, 2),
            "annual_volatility": round(annual_vol * 100, 2),
            "data_points": len(returns),
            "interpretation": "HIGH" if annual_vol > 0.5 else "MEDIUM" if annual_vol > 0.25 else "LOW"
        }
    except Exception as e:
        return {
            "error": f"Failed to calculate volatility for {symbol}: {str(e)}",
            "symbol": symbol
        }

@mcp.tool()
def get_market_overview(symbols: list[str]) -> dict:
    """
    Get overview of multiple symbols at once.
    
    Args:
        symbols: List of ticker symbols (e.g., ['AAPL', 'GOOGL', 'MSFT'])
    
    Returns:
        Price data for all symbols
    """
    overview = []
    
    for symbol in symbols:
        result = get_live_price(symbol)
        overview.append(result)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "count": len(symbols),
        "symbols": overview
    }

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    # For HTTP access, we'll use a simple HTTP wrapper
    # This runs the server and makes it accessible
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await mcp.run(
                read_stream,
                write_stream,
                mcp.create_initialization_options()
            )
    
    print("🚀 Market Server starting (stdio mode)...")
    print("   For HTTP access, use ngrok or similar tunnel")
    asyncio.run(main())
