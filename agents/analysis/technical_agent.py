"""
Technical Analysis Agent - Generates trading signals from technical indicators.

Read-only agent that computes:
- Simple Moving Averages (SMA)
- Relative Strength Index (RSI)
- Deterministic BUY/SELL/HOLD signals
"""

from typing import Dict, Any, List
from agents.analysis.market_data_agent import get_candles


def _calculate_sma(prices: List[float], period: int) -> float:
    """
    Calculate Simple Moving Average.
    
    Args:
        prices: List of prices (most recent last)
        period: Number of periods for SMA
    
    Returns:
        SMA value
    """
    if len(prices) < period:
        raise ValueError(f"Insufficient data for SMA({period}): need {period}, got {len(prices)}")
    
    return sum(prices[-period:]) / period


def _calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index.
    
    Args:
        prices: List of prices (most recent last)
        period: RSI period (default 14)
    
    Returns:
        RSI value (0-100)
    """
    if len(prices) < period + 1:
        raise ValueError(f"Insufficient data for RSI({period}): need {period + 1}, got {len(prices)}")
    
    changes = []
    for i in range(1, len(prices)):
        changes.append(prices[i] - prices[i-1])
    
    gains = [change if change > 0 else 0 for change in changes[-period:]]
    losses = [-change if change < 0 else 0 for change in changes[-period:]]
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def _generate_signal_logic(sma_fast: float, sma_slow: float, rsi: float) -> tuple[str, float]:
    """
    Generate deterministic trading signal from indicators.
    
    Args:
        sma_fast: Fast SMA value (20-period)
        sma_slow: Slow SMA value (50-period)
        rsi: RSI value (0-100)
    
    Returns:
        Tuple of (signal, confidence)
        signal: "BUY", "SELL", or "HOLD"
        confidence: 0.0 to 1.0
    """
    bullish_trend = sma_fast > sma_slow
    oversold = rsi < 30
    overbought = rsi > 70
    
    if bullish_trend and oversold:
        return "BUY", 0.85
    elif bullish_trend and rsi < 50:
        return "BUY", 0.65
    elif not bullish_trend and overbought:
        return "SELL", 0.85
    elif not bullish_trend and rsi > 50:
        return "SELL", 0.65
    elif oversold:
        return "BUY", 0.55
    elif overbought:
        return "SELL", 0.55
    else:
        return "HOLD", 0.50


def generate_signal(symbol: str) -> Dict[str, Any]:
    """
    Generate trading signal based on technical analysis.
    
    Computes SMA(20), SMA(50), and RSI(14) to produce a deterministic
    BUY/SELL/HOLD signal with confidence score.
    
    Args:
        symbol: Asset symbol (e.g., 'BTCUSDT', 'AAPL')
    
    Returns:
        Dictionary containing:
        {
            "symbol": str,
            "signal": str ("BUY", "SELL", "HOLD"),
            "confidence": float (0.0 to 1.0),
            "indicators": {
                "sma_fast": float (20-period SMA),
                "sma_slow": float (50-period SMA),
                "rsi": float (14-period RSI, 0-100)
            }
        }
    
    Raises:
        ValueError: If insufficient data or calculation error
    """
    try:
        candle_data = get_candles(symbol, interval="1h", limit=100)
        candles = candle_data["candles"]
        
        if len(candles) < 50:
            raise ValueError(f"Insufficient data for technical analysis: need 50, got {len(candles)}")
        
        close_prices = [candle["close"] for candle in candles]
        
        sma_fast = _calculate_sma(close_prices, period=20)
        sma_slow = _calculate_sma(close_prices, period=50)
        rsi = _calculate_rsi(close_prices, period=14)
        
        signal, confidence = _generate_signal_logic(sma_fast, sma_slow, rsi)
        
        return {
            "symbol": symbol,
            "signal": signal,
            "confidence": round(confidence, 2),
            "indicators": {
                "sma_fast": round(sma_fast, 2),
                "sma_slow": round(sma_slow, 2),
                "rsi": rsi
            }
        }
    
    except Exception as e:
        raise ValueError(f"Error generating signal for {symbol}: {str(e)}")
