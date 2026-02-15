"""
AutoFinance News Sentiment Server

News sentiment analysis with keyword-based scoring (ready for NewsAPI integration).
- News headline analysis
- Sentiment scoring
- Market sentiment aggregation

Tools:
- analyze_sentiment: Analyze news sentiment for a symbol
- get_news: Get recent news headlines

Note: Currently uses deterministic keyword-based analysis.
For production, add NewsAPI.org key (100 requests/day free tier).
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random


# Initialize MCP Server
mcp = FastMCP("auto-finance-news")


# Keyword-based sentiment scoring (deterministic)
POSITIVE_KEYWORDS = [
    "surge", "rally", "bullish", "breakthrough", "record", "profit",
    "adoption", "growth", "upgrade", "partnership", "innovation",
    "outperform", "optimistic", "gain", "rise", "soar"
]

NEGATIVE_KEYWORDS = [
    "crash", "plunge", "bearish", "decline", "loss", "concern",
    "risk", "fear", "regulatory", "ban", "hack", "vulnerability",
    "underperform", "pessimistic", "fall", "drop", "tumble"
]

NEUTRAL_KEYWORDS = [
    "stable", "steady", "maintain", "hold", "unchanged", "flat"
]


def generate_mock_headlines(symbol: str, count: int = 5) -> List[Dict]:
    """Generate realistic mock news headlines"""
    headlines = [
        f"{symbol} shows strong technical signals amid market recovery",
        f"Analysts maintain positive outlook on {symbol} fundamentals",
        f"{symbol} trading volume increases as institutional interest grows",
        f"Market volatility affects {symbol} short-term price action",
        f"{symbol} consolidates after recent price movements"
    ]
    
    news_items = []
    now = datetime.utcnow()
    
    for i, headline in enumerate(headlines[:count]):
        news_items.append({
            "headline": headline,
            "timestamp": (now - timedelta(hours=i * 2)).isoformat(),
            "source": f"Source{i+1}"
        })
    
    return news_items


def score_headline(headline: str) -> Dict[str, Any]:
    """Score sentiment of a headline using keyword matching"""
    headline_lower = headline.lower()
    
    positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in headline_lower)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in headline_lower)
    neutral_count = sum(1 for kw in NEUTRAL_KEYWORDS if kw in headline_lower)
    
    # Calculate sentiment
    if positive_count > negative_count:
        sentiment = "POSITIVE"
        score = 0.5 + (positive_count * 0.1)
    elif negative_count > positive_count:
        sentiment = "NEGATIVE"
        score = 0.5 - (negative_count * 0.1)
    else:
        sentiment = "NEUTRAL"
        score = 0.5
    
    # Normalize score to 0-1
    score = max(0.0, min(1.0, score))
    
    return {
        "sentiment": sentiment,
        "score": score,
        "positive_signals": positive_count,
        "negative_signals": negative_count
    }


@mcp.tool()
def analyze_sentiment(symbol: str) -> Dict[str, Any]:
    """
    Analyze news sentiment for a symbol using keyword-based scoring.
    
    Note: For real data, sign up at https://newsapi.org/ (100 requests/day free)
    
    Args:
        symbol: Stock/crypto symbol
    
    Returns:
        aggregated sentiment with confidence
    """
    # Generate realistic mock news
    news_items = generate_mock_headlines(symbol, count=5)
    
    # Score each headline
    scored_news = []
    total_score = 0
    
    for item in news_items:
        sentiment_data = score_headline(item["headline"])
        scored_news.append({
            "headline": item["headline"],
            "timestamp": item["timestamp"],
            "source": item["source"],
            "sentiment": sentiment_data["sentiment"],
            "score": sentiment_data["score"]
        })
        total_score += sentiment_data["score"]
    
    # Aggregate sentiment
    avg_score = total_score / len(scored_news) if scored_news else 0.5
    
    if avg_score > 0.6:
        overall_sentiment = "POSITIVE"
        confidence = min((avg_score - 0.5) * 2, 1.0)
    elif avg_score < 0.4:
        overall_sentiment = "NEGATIVE"
        confidence = min((0.5 - avg_score) * 2, 1.0)
    else:
        overall_sentiment = "NEUTRAL"
        confidence = 0.5
    
    return {
        "symbol": symbol,
        "sentiment": overall_sentiment,
        "score": round(avg_score, 3),
        "confidence": round(confidence, 3),
        "news_count": len(scored_news),
        "news_items": scored_news,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "keyword_analysis"
    }


@mcp.tool()
def get_news(symbol: str, count: int = 10) -> Dict[str, Any]:
    """
    Get recent news headlines for a symbol.
    
    Args:
        symbol: Stock/crypto symbol
        count: Number of headlines to return
    
    Returns:
        List of news items with sentiment scores
    """
    news_items = generate_mock_headlines(symbol, count=count)
    
    scored_news = []
    for item in news_items:
        sentiment_data = score_headline(item["headline"])
        scored_news.append({
            "headline": item["headline"],
            "timestamp": item["timestamp"],
            "source": item["source"],
            "sentiment": sentiment_data["sentiment"],
            "score": sentiment_data["score"]
        })
    
    return {
        "symbol": symbol,
        "news_items": scored_news,
        "count": len(scored_news),
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def get_market_sentiment(symbols: List[str]) -> Dict[str, Any]:
    """
    Get aggregated market sentiment across multiple symbols.
    """
    sentiment_data = []
    
    for symbol in symbols:
        analysis = analyze_sentiment(symbol)
        sentiment_data.append({
            "symbol": symbol,
            "sentiment": analysis["sentiment"],
            "score": analysis["score"],
            "confidence": analysis["confidence"]
        })
    
    # Calculate overall market sentiment
    avg_market_score = sum(s["score"] for s in sentiment_data) / len(sentiment_data) if sentiment_data else 0.5
    
    if avg_market_score > 0.6:
        market_sentiment = "POSITIVE"
    elif avg_market_score < 0.4:
        market_sentiment = "NEGATIVE"
    else:
        market_sentiment = "NEUTRAL"
    
    return {
        "market_sentiment": market_sentiment,
        "market_score": round(avg_market_score, 3),
        "symbols": sentiment_data,
        "count": len(sentiment_data),
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def analyze_custom_headline(headline: str) -> Dict[str, Any]:
    """
    Analyze sentiment of a custom headline.
    Useful for testing and demonstrations.
    """
    sentiment_data = score_headline(headline)
    
    return {
        "headline": headline,
        "sentiment": sentiment_data["sentiment"],
        "score": round(sentiment_data["score"], 3),
        "positive_signals": sentiment_data["positive_signals"],
        "negative_signals": sentiment_data["negative_signals"],
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    mcp.run()
