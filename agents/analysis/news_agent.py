"""
News & Sentiment Agent - Level 1 deterministic keyword-based sentiment analysis.

Read-only agent that analyzes news headlines using keyword matching.
No ML, no LLM, no external sentiment APIs.
"""

from typing import Dict, Any, List
import re


POSITIVE_KEYWORDS = {
    "surge": 0.4,
    "growth": 0.3,
    "record": 0.5,
    "approval": 0.3,
    "profit": 0.4,
    "rally": 0.3,
    "bullish": 0.4,
    "gains": 0.3,
    "rise": 0.2,
    "soar": 0.4,
    "boom": 0.4,
    "positive": 0.3,
    "upgrade": 0.3,
    "strong": 0.2,
    "beat": 0.3,
    "optimistic": 0.3,
    "breakthrough": 0.4,
    "success": 0.3,
    "outperform": 0.4
}

NEGATIVE_KEYWORDS = {
    "crash": -0.5,
    "selloff": -0.4,
    "lawsuit": -0.3,
    "regulation": -0.2,
    "decline": -0.4,
    "loss": -0.3,
    "bearish": -0.4,
    "fall": -0.3,
    "plunge": -0.4,
    "drop": -0.3,
    "concern": -0.2,
    "fear": -0.3,
    "risk": -0.2,
    "weak": -0.2,
    "miss": -0.3,
    "downgrade": -0.3,
    "pessimistic": -0.3,
    "failure": -0.4,
    "underperform": -0.4
}


def _fetch_headlines_simulated(symbol: str) -> List[str]:
    """
    Fetch simulated headlines for testing.
    
    Args:
        symbol: Asset symbol
    
    Returns:
        List of headline strings
    """
    from state.simulation_mode import SIMULATION_MODE, get_simulated_value
    
    if SIMULATION_MODE:
        headlines = get_simulated_value(symbol, "headlines")
        if headlines is None:
            return []
        return headlines
    
    return []


def _score_headline(headline: str) -> float:
    """
    Score a single headline using keyword matching.
    
    Args:
        headline: News headline text
    
    Returns:
        Sentiment score between -1.0 and 1.0
    """
    headline_lower = headline.lower()
    
    words = re.findall(r'\b\w+\b', headline_lower)
    
    total_score = 0.0
    
    for word in words:
        if word in POSITIVE_KEYWORDS:
            total_score += POSITIVE_KEYWORDS[word]
        elif word in NEGATIVE_KEYWORDS:
            total_score += NEGATIVE_KEYWORDS[word]
    
    normalized_score = max(-1.0, min(1.0, total_score))
    
    return normalized_score


def _classify_sentiment(score: float) -> str:
    """
    Classify sentiment score into label.
    
    Args:
        score: Sentiment score (-1.0 to 1.0)
    
    Returns:
        Sentiment label: "POSITIVE", "NEUTRAL", or "NEGATIVE"
    """
    if score > 0.3:
        return "POSITIVE"
    elif score < -0.3:
        return "NEGATIVE"
    else:
        return "NEUTRAL"


def analyze_sentiment(symbol: str) -> Dict[str, Any]:
    """
    Analyze news sentiment using deterministic keyword matching.
    
    Fetches recent headlines and computes sentiment score using predefined
    keyword dictionaries. Scores are normalized between -1.0 and 1.0.
    
    Classification thresholds:
    - POSITIVE: score > 0.3
    - NEUTRAL: -0.3 <= score <= 0.3
    - NEGATIVE: score < -0.3
    
    Args:
        symbol: Asset symbol (e.g., 'BTCUSDT', 'AAPL')
    
    Returns:
        Dictionary containing:
        {
            "symbol": str,
            "sentiment_score": float (-1.0 to 1.0),
            "sentiment_label": str ("POSITIVE", "NEUTRAL", "NEGATIVE"),
            "headline_count": int
        }
    
    Raises:
        ValueError: If analysis error
    """
    try:
        headlines = _fetch_headlines_simulated(symbol)
        
        if not headlines:
            return {
                "symbol": symbol,
                "sentiment_score": 0.0,
                "sentiment_label": "NEUTRAL",
                "headline_count": 0
            }
        
        scores = [_score_headline(headline) for headline in headlines]
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        avg_score = round(avg_score, 2)
        
        sentiment_label = _classify_sentiment(avg_score)
        
        return {
            "symbol": symbol,
            "sentiment_score": avg_score,
            "sentiment_label": sentiment_label,
            "headline_count": len(headlines)
        }
    
    except Exception as e:
        raise ValueError(f"Error analyzing sentiment for {symbol}: {str(e)}")
