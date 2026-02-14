"""
Market Data Agent - Fetches real-time price data and candles.

Read-only agent that retrieves market data from:
- Binance REST API for crypto symbols
- Yahoo Finance for stock symbols
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import statistics
import requests


def _is_crypto_symbol(symbol: str) -> bool:
    """
    Determine if symbol is cryptocurrency based on naming convention.
    
    Args:
        symbol: Asset symbol
    
    Returns:
        True if crypto, False if stock
    """
    return symbol.upper().endswith("USDT") or symbol.upper().endswith("BTC")


def get_live_price(symbol: str) -> Dict[str, Any]:
    """
    Fetch current market price for a symbol.
    
    Args:
        symbol: Asset symbol (e.g., 'BTCUSDT', 'AAPL')
    
    Returns:
        Dictionary containing price data:
        {
            "symbol": str,
            "price": float,
            "timestamp": str (ISO 8601)
        }
    
    Raises:
        ValueError: If symbol not found or API error
    """
    from state.simulation_mode import SIMULATION_MODE, get_simulated_value
    
    if SIMULATION_MODE:
        simulated_price = get_simulated_value(symbol, "price")
        if simulated_price is None:
            raise ValueError(f"Symbol {symbol} not found in simulation data")
        
        return {
            "symbol": symbol,
            "price": simulated_price,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    symbol_upper = symbol.upper()
    
    try:
        if _is_crypto_symbol(symbol):
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol_upper}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "symbol": symbol_upper,
                "price": float(data["price"]),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        else:
            import yfinance as yf
            ticker = yf.Ticker(symbol_upper)
            info = ticker.info
            
            if "currentPrice" in info:
                price = info["currentPrice"]
            elif "regularMarketPrice" in info:
                price = info["regularMarketPrice"]
            else:
                raise ValueError(f"Could not fetch price for {symbol_upper}")
            
            return {
                "symbol": symbol_upper,
                "price": float(price),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    
    except requests.RequestException as e:
        raise ValueError(f"API error fetching price for {symbol}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error fetching price for {symbol}: {str(e)}")


def get_candles(symbol: str, interval: str = "1m", limit: int = 100) -> Dict[str, Any]:
    """
    Fetch historical candlestick data.
    
    Args:
        symbol: Asset symbol (e.g., 'BTCUSDT', 'AAPL')
        interval: Time interval ('1m', '5m', '1h', '1d')
        limit: Number of candles to retrieve
    
    Returns:
        Dictionary containing:
        {
            "symbol": str,
            "interval": str,
            "candles": List[Dict] with keys:
                - timestamp: str (ISO 8601)
                - open: float
                - high: float
                - low: float
                - close: float
                - volume: float
        }
    
    Raises:
        ValueError: If symbol not found or API error
    """
    from state.simulation_mode import SIMULATION_MODE, get_simulated_value
    
    if SIMULATION_MODE:
        simulated_candles = get_simulated_value(symbol, "candles")
        if simulated_candles is None:
            raise ValueError(f"Symbol {symbol} not found in simulation data")
        
        return {
            "symbol": symbol,
            "interval": interval,
            "candles": simulated_candles[:limit]
        }
    
    symbol_upper = symbol.upper()
    
    try:
        if _is_crypto_symbol(symbol):
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                "symbol": symbol_upper,
                "interval": interval,
                "limit": limit
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            candles = []
            for candle in data:
                candles.append({
                    "timestamp": datetime.fromtimestamp(candle[0] / 1000).isoformat() + "Z",
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5])
                })
            
            return {
                "symbol": symbol_upper,
                "interval": interval,
                "candles": candles
            }
        else:
            import yfinance as yf
            
            interval_map = {
                "1m": "1m",
                "5m": "5m",
                "1h": "1h",
                "1d": "1d"
            }
            yf_interval = interval_map.get(interval, "1d")
            
            period_map = {
                "1m": "1d",
                "5m": "5d",
                "1h": "1mo",
                "1d": "1y"
            }
            period = period_map.get(interval, "1mo")
            
            ticker = yf.Ticker(symbol_upper)
            hist = ticker.history(period=period, interval=yf_interval)
            
            if hist.empty:
                raise ValueError(f"No data available for {symbol_upper}")
            
            candles = []
            for idx, row in hist.tail(limit).iterrows():
                candles.append({
                    "timestamp": idx.isoformat() + "Z",
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row["Volume"])
                })
            
            return {
                "symbol": symbol_upper,
                "interval": interval,
                "candles": candles
            }
    
    except requests.RequestException as e:
        raise ValueError(f"API error fetching candles for {symbol}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error fetching candles for {symbol}: {str(e)}")


def calculate_volatility(symbol: str, lookback: int = 20) -> Dict[str, Any]:
    """
    Calculate price volatility using standard deviation of recent closes.
    
    Args:
        symbol: Asset symbol (e.g., 'BTCUSDT', 'AAPL')
        lookback: Number of periods for volatility calculation
    
    Returns:
        Dictionary containing:
        {
            "symbol": str,
            "volatility": float (standard deviation of returns),
            "lookback_periods": int
        }
    
    Raises:
        ValueError: If insufficient data or calculation error
    """
    from state.simulation_mode import SIMULATION_MODE, get_simulated_value
    
    if SIMULATION_MODE:
        simulated_vol = get_simulated_value(symbol, "volatility")
        if simulated_vol is None:
            raise ValueError(f"Symbol {symbol} not found in simulation data")
        
        return {
            "symbol": symbol,
            "volatility": simulated_vol,
            "lookback_periods": lookback
        }
    
    try:
        candle_data = get_candles(symbol, interval="1h", limit=lookback + 1)
        candles = candle_data["candles"]
        
        if len(candles) < 2:
            raise ValueError(f"Insufficient data for volatility calculation: {len(candles)} candles")
        
        close_prices = [candle["close"] for candle in candles]
        
        returns = []
        for i in range(1, len(close_prices)):
            ret = (close_prices[i] - close_prices[i-1]) / close_prices[i-1]
            returns.append(ret)
        
        if len(returns) < 2:
            raise ValueError("Insufficient returns for volatility calculation")
        
        volatility = statistics.stdev(returns)
        
        return {
            "symbol": symbol,
            "volatility": round(volatility, 6),
            "lookback_periods": lookback
        }
    
    except Exception as e:
        raise ValueError(f"Error calculating volatility for {symbol}: {str(e)}")
