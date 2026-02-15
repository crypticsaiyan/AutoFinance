"""
AutoFinance Fundamental Analysis Server

Long-term fundamental analysis using REAL market data from Yahoo Finance.
- Valuation metrics (P/E, P/B, PEG)
- Growth analysis (revenue, earnings)
- Quality scoring (margins, ROE)
- Company information

Tools:
- analyze_fundamentals: Comprehensive fundamental analysis
- get_company_overview: Company details and key metrics
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any, List
import yfinance as yf


# Initialize MCP Server
mcp = FastMCP("auto-finance-fundamental")


def _get_ticker_symbol(symbol: str) -> str:
    """Convert symbol to Yahoo Finance format."""
    crypto_map = {
        "BTCUSDT": "BTC-USD",
        "ETHUSDT": "ETH-USD",
        "SOLUSDT": "SOL-USD",
        "BNBUSDT": "BNB-USD",
    }
    return crypto_map.get(symbol, symbol)


def get_real_fundamentals(symbol: str) -> Dict[str, Any]:
    """
    Fetch real fundamental data from Yahoo Finance.
    
    Args:
        symbol: Trading symbol
    
    Returns:
        Dictionary of fundamental metrics
    """
    try:
        yf_symbol = _get_ticker_symbol(symbol)
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info
        
        if not info:
            return {}
        
        # Extract key fundamentals
        return {
            "company_name": info.get("longName", info.get("shortName", symbol)),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "enterprise_value": info.get("enterpriseValue", 0),
            "pe_ratio": info.get("trailingPE", info.get("forwardPE", 0)),
            "pb_ratio": info.get("priceToBook", 0),
            "peg_ratio": info.get("pegRatio", 0),
            "price_to_sales": info.get("priceToSalesTrailing12Months", 0),
            "revenue": info.get("totalRevenue", 0),
            "revenue_growth": info.get("revenueGrowth", 0),
            "earnings_growth": info.get("earningsGrowth", 0),
            "profit_margin": info.get("profitMargins", 0),
            "operating_margin": info.get("operatingMargins", 0),
            "roe": info.get("returnOnEquity", 0),
            "roa": info.get("returnOnAssets", 0),
            "debt_to_equity": info.get("debtToEquity", 0),
            "current_ratio": info.get("currentRatio", 0),
            "dividend_yield": info.get("dividendYield", 0),
            "beta": info.get("beta", 1.0),
            "52_week_high": info.get("fiftyTwoWeekHigh", 0),
            "52_week_low": info.get("fiftyTwoWeekLow", 0),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
            "target_price": info.get("targetMeanPrice", 0),
            "analyst_recommendation": info.get("recommendationKey", "hold"),
        }
    except Exception as e:
        print(f"Error fetching fundamentals for {symbol}: {e}")
        return {}


def calculate_valuation_score(fundamentals: Dict) -> float:
    """
    Calculate valuation score (0-1, higher is better value).
    Based on P/E, P/B, PEG ratios compared to market averages.
    """
    pe = fundamentals.get("pe_ratio", 0)
    pb = fundamentals.get("pb_ratio", 0)
    peg = fundamentals.get("peg_ratio", 0)
    
    score = 0.5  # Start neutral
    
    # P/E analysis (average S&P 500 P/E is ~20)
    if pe > 0:
        if pe < 15:
            score += 0.15  # Undervalued
        elif pe > 30:
            score -= 0.15  # Overvalued
    
    # P/B analysis (average is ~3)
    if pb > 0:
        if pb < 2:
            score += 0.1  # Good value
        elif pb > 5:
            score -= 0.1  # Expensive
    
    # PEG analysis (< 1 is good, > 2 is expensive)
    if peg > 0:
        if peg < 1:
            score += 0.2  # Excellent value
        elif peg > 2:
            score -= 0.2  # Overvalued
    
    return max(0.0, min(1.0, score))


def calculate_quality_score(fundamentals: Dict) -> float:
    """
    Calculate quality score based on profitability and financial health.
    """
    profit_margin = fundamentals.get("profit_margin", 0)
    roe = fundamentals.get("roe", 0)
    debt_to_equity = fundamentals.get("debt_to_equity", 0)
    
    score = 0.5  # Start neutral
    
    # Profit margin (good companies have >15%)
    if profit_margin > 0.15:
        score += 0.2
    elif profit_margin < 0.05:
        score -= 0.2
    
    # ROE (good is >15%)
    if roe > 0.15:
        score += 0.2
    elif roe < 0.05:
        score -= 0.2
    
    # Debt to equity (lower is better, <0.5 is good)
    if debt_to_equity > 0 and debt_to_equity < 0.5:
        score += 0.1
    elif debt_to_equity > 2:
        score -= 0.1
    
    return max(0.0, min(1.0, score))


@mcp.tool()
def analyze_fundamentals(symbol: str) -> Dict[str, Any]:
    """
    Perform comprehensive fundamental analysis using REAL data from Yahoo Finance.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
    
    Returns:
        valuation_score: 0-1, investment value opportunity
        quality_score: 0-1, company quality
        growth_score: 0-1, growth potential
        recommendation: BUY, HOLD, SELL based on analyst consensus
    """
    # Get real fundamental data
    fundamentals = get_real_fundamentals(symbol)
    
    if not fundamentals:
        return {
            "symbol": symbol,
            "error": "Unable to fetch fundamental data",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Calculate scores
    valuation_score = calculate_valuation_score(fundamentals)
    quality_score = calculate_quality_score(fundamentals)
    
    # Growth score from revenue and earnings growth
    revenue_growth = fundamentals.get("revenue_growth", 0)
    earnings_growth = fundamentals.get("earnings_growth", 0)
    avg_growth = (revenue_growth + earnings_growth) / 2 if (revenue_growth and earnings_growth) else 0
    
    # Normalize growth to 0-1 (20% growth = 1.0)
    growth_score = min(abs(avg_growth) / 0.20, 1.0) if avg_growth else 0.5
    
    # Overall fundamental score
    overall_score = (valuation_score * 0.3 + quality_score * 0.4 + growth_score * 0.3)
    
    # Use analyst recommendation or calculate from score
    analyst_rec = fundamentals.get("analyst_recommendation", "hold").lower()
    if "buy" in analyst_rec or "strong_buy" in analyst_rec:
        recommendation = "BUY"
        confidence = 0.75
    elif "sell" in analyst_rec:
        recommendation = "SELL"
        confidence = 0.70
    else:
        recommendation = "HOLD"
        confidence = 0.60
    
    # Adjust confidence based on our scores
    confidence = (confidence + overall_score) / 2
    
    # Format market cap
    market_cap = fundamentals.get("market_cap", 0)
    if market_cap > 1_000_000_000_000:
        cap_str = f"${market_cap/1_000_000_000_000:.2f}T"
    elif market_cap > 1_000_000_000:
        cap_str = f"${market_cap/1_000_000_000:.2f}B"
    else:
        cap_str = f"${market_cap/1_000_000:.2f}M"
    
    return {
        "symbol": symbol,
        "company_name": fundamentals.get("company_name", symbol),
        "recommendation": recommendation,
        "confidence": round(confidence, 3),
        "sector": fundamentals.get("sector", "N/A"),
        "industry": fundamentals.get("industry", "N/A"),
        "fundamentals": {
            "market_cap": market_cap,
            "market_cap_str": cap_str,
            "pe_ratio": round(fundamentals.get("pe_ratio", 0), 2),
            "pb_ratio": round(fundamentals.get("pb_ratio", 0), 2),
            "peg_ratio": round(fundamentals.get("peg_ratio", 0), 2),
            "profit_margin": round(fundamentals.get("profit_margin", 0) * 100, 2),
            "roe": round(fundamentals.get("roe", 0) * 100, 2),
            "revenue_growth": round(fundamentals.get("revenue_growth", 0) * 100, 2),
            "earnings_growth": round(fundamentals.get("earnings_growth", 0) * 100, 2),
            "debt_to_equity": round(fundamentals.get("debt_to_equity", 0), 2),
            "dividend_yield": round(fundamentals.get("dividend_yield", 0) * 100, 2),
            "current_price": round(fundamentals.get("current_price", 0), 2),
            "target_price": round(fundamentals.get("target_price", 0), 2)
        },
        "scores": {
            "valuation": round(valuation_score, 3),
            "quality": round(quality_score, 3),
            "growth": round(growth_score, 3),
            "overall": round(overall_score, 3)
        },
        "timestamp": datetime.utcnow().isoformat(),
        "source": "yahoo_finance"
    }


@mcp.tool()
def get_company_overview(symbol: str) -> Dict[str, Any]:
    """
    Get detailed company overview from REAL data.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Comprehensive company information
    """
    fundamentals = get_real_fundamentals(symbol)
    
    if not fundamentals:
        return {
            "symbol": symbol,
            "error": "Unable to fetch company data",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Calculate upside potential
    current = fundamentals.get("current_price", 0)
    target = fundamentals.get("target_price", 0)
    upside = ((target - current) / current * 100) if current > 0 and target > 0 else 0
    
    return {
        "symbol": symbol,
        "company_name": fundamentals.get("company_name", symbol),
        "sector": fundamentals.get("sector", "N/A"),
        "industry": fundamentals.get("industry", "N/A"),
        "valuation": {
            "current_price": fundamentals.get("current_price", 0),
            "target_price": fundamentals.get("target_price", 0),
            "upside_potential": round(upside, 2),
            "pe_ratio": fundamentals.get("pe_ratio", 0),
            "pb_ratio": fundamentals.get("pb_ratio", 0),
            "peg_ratio": fundamentals.get("peg_ratio", 0),
            "price_to_sales": fundamentals.get("price_to_sales", 0)
        },
        "profitability": {
            "profit_margin": round(fundamentals.get("profit_margin", 0) * 100, 2),
            "operating_margin": round(fundamentals.get("operating_margin", 0) * 100, 2),
            "roe": round(fundamentals.get("roe", 0) * 100, 2),
            "roa": round(fundamentals.get("roa", 0) * 100, 2)
        },
        "growth": {
            "revenue_growth": round(fundamentals.get("revenue_growth", 0) * 100, 2),
            "earnings_growth": round(fundamentals.get("earnings_growth", 0) * 100, 2)
        },
        "balance_sheet": {
            "debt_to_equity": fundamentals.get("debt_to_equity", 0),
            "current_ratio": fundamentals.get("current_ratio", 0)
        },
        "market_data": {
            "market_cap": fundamentals.get("market_cap", 0),
            "beta": fundamentals.get("beta", 1.0),
            "52_week_high": fundamentals.get("52_week_high", 0),
            "52_week_low": fundamentals.get("52_week_low", 0),
            "dividend_yield": round(fundamentals.get("dividend_yield", 0) * 100, 2)
        },
        "analyst_recommendation": fundamentals.get("analyst_recommendation", "hold"),
        "timestamp": datetime.utcnow().isoformat(),
        "source": "yahoo_finance"
    }


@mcp.tool()
def compare_fundamentals(symbols: List[str]) -> Dict[str, Any]:
    """
    Compare fundamental metrics across multiple stocks using REAL data.
    
    Args:
        symbols: List of stock symbols to compare
    
    Returns:
        Comparison data with rankings
    """
    comparison = []
    
    for symbol in symbols:
        analysis = analyze_fundamentals(symbol)
        
        if "error" not in analysis:
            comparison.append({
                "symbol": symbol,
                "company_name": analysis.get("company_name", symbol),
                "recommendation": analysis["recommendation"],
                "overall_score": analysis["scores"]["overall"],
                "quality": analysis["scores"]["quality"],
                "growth": analysis["scores"]["growth"],
                "valuation": analysis["scores"]["valuation"],
                "pe_ratio": analysis["fundamentals"].get("pe_ratio", 0),
                "roe": analysis["fundamentals"].get("roe", 0)
            })
    
    # Sort by overall score
    comparison.sort(key=lambda x: x["overall_score"], reverse=True)
    
    return {
        "comparison": comparison,
        "top_pick": comparison[0] if comparison else None,
        "count": len(comparison),
        "timestamp": datetime.utcnow().isoformat(),
        "source": "yahoo_finance"
    }


@mcp.tool()
def get_investment_thesis(symbol: str) -> Dict[str, Any]:
    """
    Generate investment thesis from REAL fundamental data.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Investment thesis with strengths, weaknesses, and outlook
    """
    analysis = analyze_fundamentals(symbol)
    
    if "error" in analysis:
        return analysis
    
    # Build thesis narrative
    fundamentals = analysis["fundamentals"]
    scores = analysis["scores"]
    
    strengths = []
    weaknesses = []
    
    # Quality analysis
    if scores["quality"] > 0.7:
        strengths.append(f"Strong profitability (Profit Margin: {fundamentals['profit_margin']}%, ROE: {fundamentals['roe']}%)")
    elif scores["quality"] < 0.4:
        weaknesses.append("Below-average profitability metrics")
    
    # Growth analysis
    if scores["growth"] > 0.6:
        strengths.append(f"Solid growth trajectory (Revenue: {fundamentals['revenue_growth']}%, Earnings: {fundamentals['earnings_growth']}%)")
    elif scores["growth"] < 0.4:
        weaknesses.append("Limited growth momentum")
    
    # Valuation analysis
    if scores["valuation"] > 0.6:
        strengths.append(f"Attractive valuation (P/E: {fundamentals['pe_ratio']}, PEG: {fundamentals['peg_ratio']})")
    elif scores["valuation"] < 0.4:
        weaknesses.append("Premium valuation may limit upside")
    
    # Target price analysis
    if fundamentals.get("target_price", 0) > fundamentals.get("current_price", 0):
        upside = ((fundamentals['target_price'] - fundamentals['current_price']) / fundamentals['current_price']) * 100
        strengths.append(f"Analyst target implies {upside:.1f}% upside")
    
    # Debt analysis
    if fundamentals.get("debt_to_equity", 0) < 0.5:
        strengths.append("Strong balance sheet with low debt")
    elif fundamentals.get("debt_to_equity", 0) > 2:
        weaknesses.append("High debt levels increase risk")
    
    thesis = {
        "symbol": symbol,
        "company_name": analysis.get("company_name", symbol),
        "sector": analysis.get("sector", "N/A"),
        "investment_case": analysis["recommendation"],
        "confidence": analysis["confidence"],
        "strengths": strengths if strengths else ["Balanced fundamental profile"],
        "weaknesses": weaknesses if weaknesses else ["No major concerns identified"],
        "horizon": "Long-term (6-12 months)",
        "overall_score": scores["overall"],
        "timestamp": datetime.utcnow().isoformat(),
        "source": "yahoo_finance"
    }
    
    return thesis


if __name__ == "__main__":
    mcp.run()
