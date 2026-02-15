"""
AutoFinance News Sentiment Server

Real news via NewsAPI.org + LLM-powered sentiment analysis (Ollama/OpenAI).
Falls back to keyword-based analysis if LLM is unavailable.

Tools:
- analyze_sentiment: Analyze news sentiment for a symbol
- get_news: Get recent real news headlines with sentiment
- get_market_sentiment: Aggregate sentiment across symbols
- analyze_custom_headline: Analyze any custom headline
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, List
import json
import os
import sys

# Add parent directory to path for llm_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_client import get_llm_response, check_llm_availability

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))


# Initialize MCP Server
mcp = FastMCP("auto-finance-news")

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_API_URL = "https://newsapi.org/v2/everything"

# Keyword-based sentiment scoring (fallback)
POSITIVE_KEYWORDS = [
    "surge", "rally", "bullish", "breakthrough", "record", "profit",
    "adoption", "growth", "upgrade", "partnership", "innovation",
    "outperform", "optimistic", "gain", "rise", "soar", "beat", "strong"
]

NEGATIVE_KEYWORDS = [
    "crash", "plunge", "bearish", "decline", "loss", "concern",
    "risk", "fear", "regulatory", "ban", "hack", "vulnerability",
    "underperform", "pessimistic", "fall", "drop", "tumble", "miss", "weak"
]


def fetch_real_news(symbol: str, count: int = 5) -> List[Dict]:
    """Fetch real news from NewsAPI.org"""
    if not NEWS_API_KEY:
        return []

    # Map common symbols to search-friendly names
    symbol_names = {
        "AAPL": "Apple stock",
        "MSFT": "Microsoft stock",
        "GOOGL": "Google Alphabet stock",
        "TSLA": "Tesla stock",
        "AMZN": "Amazon stock",
        "NVDA": "Nvidia stock",
        "META": "Meta Facebook stock",
        "BTCUSDT": "Bitcoin BTC crypto",
        "ETHUSDT": "Ethereum ETH crypto",
        "SOLUSDT": "Solana SOL crypto",
    }
    query = symbol_names.get(symbol, f"{symbol} stock")

    try:
        response = requests.get(
            NEWS_API_URL,
            params={
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": count,
                "language": "en",
                "apiKey": NEWS_API_KEY
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            return []

        news_items = []
        for article in data.get("articles", [])[:count]:
            title = article.get("title", "")
            # Skip removed articles
            if title == "[Removed]" or not title:
                continue
            news_items.append({
                "headline": title,
                "description": article.get("description", ""),
                "timestamp": article.get("publishedAt", datetime.utcnow().isoformat()),
                "source": article.get("source", {}).get("name", "Unknown"),
                "url": article.get("url", "")
            })

        return news_items

    except Exception as e:
        print(f"⚠️  NewsAPI error: {e}")
        return []


def score_headline_keywords(headline: str) -> Dict[str, Any]:
    """Score sentiment using keyword matching (fallback)"""
    headline_lower = headline.lower()

    positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in headline_lower)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in headline_lower)

    if positive_count > negative_count:
        sentiment = "POSITIVE"
        score = 0.5 + (positive_count * 0.1)
    elif negative_count > positive_count:
        sentiment = "NEGATIVE"
        score = 0.5 - (negative_count * 0.1)
    else:
        sentiment = "NEUTRAL"
        score = 0.5

    return {
        "sentiment": sentiment,
        "score": max(0.0, min(1.0, score)),
        "reasoning": f"Keyword analysis: {positive_count} positive, {negative_count} negative signals",
        "method": "keyword"
    }


def score_headline_llm(headline: str, symbol: str = "") -> Dict[str, Any]:
    """Score sentiment using LLM (OpenAI or Ollama)"""
    prompt = f"""Analyze the financial sentiment of this news headline{f' about {symbol}' if symbol else ''}.

Headline: "{headline}"

Respond ONLY with valid JSON:
{{"sentiment": "POSITIVE" or "NEGATIVE" or "NEUTRAL", "score": 0.0 to 1.0, "reasoning": "brief explanation"}}"""

    result = get_llm_response(
        prompt=prompt,
        system_prompt="You are a financial sentiment analyst. Always respond with valid JSON only.",
        max_tokens=150,
        temperature=0.2
    )

    if "error" in result:
        fallback = score_headline_keywords(headline)
        fallback["method"] = "keyword_fallback"
        return fallback

    try:
        response_text = result["response"]
        if "{" in response_text and "}" in response_text:
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            analysis = json.loads(response_text[start:end])
        else:
            raise ValueError("No JSON in response")

        sentiment = analysis.get("sentiment", "NEUTRAL").upper()
        if sentiment not in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
            sentiment = "NEUTRAL"

        return {
            "sentiment": sentiment,
            "score": max(0.0, min(1.0, float(analysis.get("score", 0.5)))),
            "reasoning": analysis.get("reasoning", ""),
            "method": "llm",
            "provider": result.get("provider", "unknown"),
            "model": result.get("model", "unknown")
        }
    except (json.JSONDecodeError, ValueError):
        fallback = score_headline_keywords(headline)
        fallback["method"] = "keyword_fallback"
        return fallback


def score_headline(headline: str, symbol: str = "") -> Dict[str, Any]:
    """Score headline using LLM if available, otherwise keywords"""
    status = check_llm_availability()
    if status.get("recommended"):
        return score_headline_llm(headline, symbol)
    return score_headline_keywords(headline)


@mcp.tool()
def analyze_sentiment(symbol: str) -> Dict[str, Any]:
    """
    Analyze news sentiment for a symbol using real news from NewsAPI + LLM analysis.

    Args:
        symbol: Stock/crypto symbol (e.g., AAPL, TSLA, BTCUSDT)

    Returns:
        Aggregated sentiment with confidence, real headlines, and analysis method
    """
    # Try real news first, no fallback headlines if unavailable
    news_items = fetch_real_news(symbol, count=5)
    news_source = "newsapi"

    if not news_items:
        news_source = "unavailable"
        return {
            "symbol": symbol,
            "sentiment": "UNKNOWN",
            "score": 0.5,
            "confidence": 0.0,
            "news_count": 0,
            "news_items": [],
            "analysis_method": "none",
            "news_source": news_source,
            "error": "No news available. Set NEWS_API_KEY in .env for real news.",
            "timestamp": datetime.utcnow().isoformat(),
            "source": "no_data"
        }

    scored_news = []
    total_score = 0

    for item in news_items:
        sentiment_data = score_headline(item["headline"], symbol)
        scored_news.append({
            "headline": item["headline"],
            "description": item.get("description", ""),
            "timestamp": item["timestamp"],
            "source": item["source"],
            "url": item.get("url", ""),
            "sentiment": sentiment_data["sentiment"],
            "score": sentiment_data["score"],
            "reasoning": sentiment_data.get("reasoning", ""),
            "method": sentiment_data.get("method", "unknown")
        })
        total_score += sentiment_data["score"]

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

    methods = set(item.get("method") for item in scored_news)
    analysis_method = "llm" if "llm" in methods else "keyword"

    return {
        "symbol": symbol,
        "sentiment": overall_sentiment,
        "score": round(avg_score, 3),
        "confidence": round(confidence, 3),
        "news_count": len(scored_news),
        "news_items": scored_news,
        "analysis_method": analysis_method,
        "news_source": news_source,
        "timestamp": datetime.utcnow().isoformat(),
        "source": f"newsapi + {analysis_method}"
    }


@mcp.tool()
def get_news(symbol: str, count: int = 10) -> Dict[str, Any]:
    """
    Get recent real news headlines for a symbol with sentiment analysis.

    Args:
        symbol: Stock/crypto symbol
        count: Number of headlines to return

    Returns:
        List of real news items with sentiment scores
    """
    news_items = fetch_real_news(symbol, count=count)
    news_source = "newsapi"

    if not news_items:
        return {
            "symbol": symbol,
            "news_items": [],
            "count": 0,
            "news_source": "unavailable",
            "error": "No news available. Set NEWS_API_KEY in .env for real news.",
            "timestamp": datetime.utcnow().isoformat()
        }

    scored_news = []
    for item in news_items:
        sentiment_data = score_headline(item["headline"], symbol)
        scored_news.append({
            "headline": item["headline"],
            "description": item.get("description", ""),
            "timestamp": item["timestamp"],
            "source": item["source"],
            "url": item.get("url", ""),
            "sentiment": sentiment_data["sentiment"],
            "score": sentiment_data["score"],
            "reasoning": sentiment_data.get("reasoning", ""),
            "method": sentiment_data.get("method", "unknown")
        })

    return {
        "symbol": symbol,
        "news_items": scored_news,
        "count": len(scored_news),
        "news_source": news_source,
        "timestamp": datetime.utcnow().isoformat()
    }


@mcp.tool()
def get_market_sentiment(symbols: List[str]) -> Dict[str, Any]:
    """
    Get aggregated market sentiment across multiple symbols using real news + LLM.
    """
    sentiment_data = []

    for symbol in symbols:
        analysis = analyze_sentiment(symbol)
        sentiment_data.append({
            "symbol": symbol,
            "sentiment": analysis["sentiment"],
            "score": analysis["score"],
            "confidence": analysis["confidence"],
            "method": analysis.get("analysis_method", "unknown"),
            "news_source": analysis.get("news_source", "unknown")
        })

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
    Analyze sentiment of a custom headline using LLM.
    """
    sentiment_data = score_headline(headline)

    return {
        "headline": headline,
        "sentiment": sentiment_data["sentiment"],
        "score": round(sentiment_data["score"], 3),
        "reasoning": sentiment_data.get("reasoning", ""),
        "method": sentiment_data.get("method", "unknown"),
        "provider": sentiment_data.get("provider", ""),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    mcp.run()
