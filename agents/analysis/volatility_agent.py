"""
Volatility Agent - Assesses market volatility and risk levels.

Read-only agent that computes volatility scores and risk classifications.
"""

from typing import Dict, Any
from agents.analysis.market_data_agent import calculate_volatility


def _classify_risk_level(volatility_score: float) -> str:
    """
    Classify risk level based on volatility score.
    
    Args:
        volatility_score: Volatility value (standard deviation of returns)
    
    Returns:
        Risk level: "LOW", "MEDIUM", or "HIGH"
    """
    if volatility_score < 0.02:
        return "LOW"
    elif volatility_score < 0.04:
        return "MEDIUM"
    else:
        return "HIGH"


def get_volatility_score(symbol: str, lookback: int = 20) -> Dict[str, Any]:
    """
    Calculate volatility score and risk classification.
    
    Uses Market Data Agent to compute volatility from recent price data,
    then classifies into risk levels:
    - LOW: volatility < 0.02
    - MEDIUM: 0.02 <= volatility < 0.04
    - HIGH: volatility >= 0.04
    
    Args:
        symbol: Asset symbol (e.g., 'BTCUSDT', 'AAPL')
        lookback: Number of periods for volatility calculation (default 20)
    
    Returns:
        Dictionary containing:
        {
            "symbol": str,
            "volatility_score": float,
            "risk_level": str ("LOW", "MEDIUM", "HIGH"),
            "lookback_periods": int
        }
    
    Raises:
        ValueError: If calculation error or insufficient data
    """
    try:
        vol_data = calculate_volatility(symbol, lookback=lookback)
        
        volatility_score = vol_data["volatility"]
        risk_level = _classify_risk_level(volatility_score)
        
        return {
            "symbol": symbol,
            "volatility_score": volatility_score,
            "risk_level": risk_level,
            "lookback_periods": lookback
        }
    
    except Exception as e:
        raise ValueError(f"Error calculating volatility score for {symbol}: {str(e)}")
