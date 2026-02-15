"""
AutoFinance Macro Analysis Server

Real macroeconomic data from FRED API (Federal Reserve Economic Data).
Falls back to reasonable estimates if FRED_API_KEY is not set.

Tools:
- analyze_macro: Comprehensive macro environment analysis
- get_macro_indicators: Get key economic indicators
- get_sector_outlook: Sector-specific macro outlook
- assess_portfolio_timing: Timing recommendation for rebalancing
- get_correlation_analysis: Crypto-equity correlation analysis
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, Any
import os
import sys

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# Initialize MCP Server
mcp = FastMCP("auto-finance-macro")

FRED_API_KEY = os.getenv("FRED_API_KEY", "")
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# FRED series IDs
FRED_SERIES = {
    "gdp_growth": "A191RL1Q225SBEA",       # Real GDP growth rate (quarterly, annualized)
    "inflation_rate": "CPIAUCSL",            # CPI (monthly, used to calculate YoY inflation)
    "core_inflation": "CPILFESL",            # Core CPI (excluding food & energy)
    "unemployment_rate": "UNRATE",           # Unemployment rate (monthly)
    "fed_funds_rate": "DFF",                 # Effective federal funds rate (daily)
    "treasury_10y": "DGS10",                 # 10-Year Treasury yield (daily)
    "treasury_2y": "DGS2",                   # 2-Year Treasury yield (daily)
    "sp500": "SP500",                        # S&P 500 index (daily)
    "vix": "VIXCLS",                         # VIX volatility index (daily)
    "consumer_sentiment": "UMCSENT",         # U of Michigan Consumer Sentiment (monthly)
    "initial_claims": "ICSA",                # Initial jobless claims (weekly)
    "industrial_production": "INDPRO",       # Industrial production index (monthly)
}

# Cache to avoid hammering FRED
_fred_cache = {}
_CACHE_TTL = 3600  # 1 hour


def fetch_fred_series(series_id: str, limit: int = 5) -> list:
    """Fetch latest observations from FRED API"""
    if not FRED_API_KEY:
        return []

    cache_key = f"{series_id}:{limit}"
    import time
    now = time.time()
    if cache_key in _fred_cache and (now - _fred_cache[cache_key]["time"]) < _CACHE_TTL:
        return _fred_cache[cache_key]["data"]

    try:
        response = requests.get(
            FRED_BASE_URL,
            params={
                "series_id": series_id,
                "api_key": FRED_API_KEY,
                "file_type": "json",
                "sort_order": "desc",
                "limit": limit
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        observations = data.get("observations", [])

        # Filter out missing values
        valid = []
        for obs in observations:
            if obs.get("value") and obs["value"] != ".":
                valid.append({
                    "date": obs["date"],
                    "value": float(obs["value"])
                })

        _fred_cache[cache_key] = {"data": valid, "time": now}
        return valid

    except Exception as e:
        print(f"⚠️  FRED API error for {series_id}: {e}")
        return []


def get_latest_value(series_id: str) -> float | None:
    """Get latest value for a FRED series"""
    data = fetch_fred_series(series_id, limit=1)
    return data[0]["value"] if data else None


def calculate_yoy_change(series_id: str) -> float | None:
    """Calculate year-over-year percentage change"""
    data = fetch_fred_series(series_id, limit=14)  # ~14 months of monthly data
    if len(data) < 12:
        return None
    current = data[0]["value"]
    year_ago = data[-1]["value"]
    if year_ago == 0:
        return None
    return ((current - year_ago) / year_ago) * 100


def get_real_macro_indicators() -> Dict[str, Any]:
    """Fetch real macro indicators from FRED"""

    gdp = get_latest_value(FRED_SERIES["gdp_growth"])
    unemployment = get_latest_value(FRED_SERIES["unemployment_rate"])
    fed_rate = get_latest_value(FRED_SERIES["fed_funds_rate"])
    treasury_10y = get_latest_value(FRED_SERIES["treasury_10y"])
    treasury_2y = get_latest_value(FRED_SERIES["treasury_2y"])
    vix = get_latest_value(FRED_SERIES["vix"])
    consumer_sentiment = get_latest_value(FRED_SERIES["consumer_sentiment"])
    inflation_yoy = calculate_yoy_change(FRED_SERIES["inflation_rate"])

    # Determine yield curve status
    yield_spread = None
    if treasury_10y is not None and treasury_2y is not None:
        yield_spread = round(treasury_10y - treasury_2y, 2)

    # Determine volatility regime from VIX
    if vix is not None:
        if vix < 15:
            vol_regime = "LOW"
        elif vix < 25:
            vol_regime = "NORMAL"
        else:
            vol_regime = "HIGH"
    else:
        vol_regime = "UNKNOWN"

    # Determine market regime
    regime = "UNKNOWN"
    if gdp is not None and inflation_yoy is not None:
        if gdp > 2.5 and (inflation_yoy is None or inflation_yoy < 3.5):
            regime = "BULL"
        elif gdp < 0:
            regime = "BEAR"
        elif gdp > 0:
            regime = "CONSOLIDATION"

    # Risk appetite based on VIX and consumer sentiment
    risk_appetite = 0.5
    if vix is not None:
        risk_appetite = max(0.1, min(0.9, 1.0 - (vix / 50)))
    if consumer_sentiment is not None:
        risk_appetite = (risk_appetite + (consumer_sentiment / 120)) / 2

    # Liquidity score based on fed rate and yield curve
    liquidity = 0.5
    if fed_rate is not None:
        liquidity = max(0.2, min(0.9, 1.0 - (fed_rate / 10)))

    return {
        "gdp_growth": round(gdp, 2) if gdp is not None else None,
        "inflation_rate": round(inflation_yoy, 2) if inflation_yoy is not None else None,
        "unemployment_rate": round(unemployment, 2) if unemployment is not None else None,
        "interest_rate": round(fed_rate, 2) if fed_rate is not None else None,
        "treasury_10y": round(treasury_10y, 2) if treasury_10y is not None else None,
        "treasury_2y": round(treasury_2y, 2) if treasury_2y is not None else None,
        "yield_spread": yield_spread,
        "vix": round(vix, 2) if vix is not None else None,
        "consumer_sentiment": round(consumer_sentiment, 1) if consumer_sentiment is not None else None,
        "market_regime": regime,
        "volatility_regime": vol_regime,
        "risk_appetite": round(risk_appetite, 3),
        "liquidity_score": round(liquidity, 3),
        "source": "fred_api"
    }


def get_macro_data() -> Dict[str, Any]:
    """Get macro data from FRED if key available, otherwise return error"""
    if FRED_API_KEY:
        return get_real_macro_indicators()

    return {
        "gdp_growth": None,
        "inflation_rate": None,
        "unemployment_rate": None,
        "interest_rate": None,
        "treasury_10y": None,
        "treasury_2y": None,
        "yield_spread": None,
        "vix": None,
        "consumer_sentiment": None,
        "market_regime": "UNKNOWN",
        "volatility_regime": "UNKNOWN",
        "risk_appetite": 0.5,
        "liquidity_score": 0.5,
        "source": "unavailable",
        "error": "No FRED API key configured. Get one free at https://fred.stlouisfed.org/docs/api/"
    }


@mcp.tool()
def analyze_macro() -> Dict[str, Any]:
    """
    Analyze macroeconomic environment using real FRED data.

    Returns:
        market_regime, risk_environment, investment_stance, indicators, and insights
    """
    indicators = get_macro_data()

    regime = indicators["market_regime"]
    risk_appetite = indicators["risk_appetite"]
    liquidity = indicators["liquidity_score"]
    volatility = indicators["volatility_regime"]

    # Determine risk environment
    if risk_appetite > 0.7 and liquidity > 0.7:
        risk_environment = "FAVORABLE"
        risk_score = 0.3
    elif risk_appetite < 0.5 or liquidity < 0.5:
        risk_environment = "CHALLENGING"
        risk_score = 0.7
    else:
        risk_environment = "NEUTRAL"
        risk_score = 0.5

    # Determine investment stance
    if regime == "BULL" and risk_environment == "FAVORABLE":
        stance = "AGGRESSIVE"
        confidence = 0.8
    elif regime == "BEAR" or risk_environment == "CHALLENGING":
        stance = "DEFENSIVE"
        confidence = 0.75
    else:
        stance = "BALANCED"
        confidence = 0.65

    # Generate insights from real data
    insights = []

    if indicators.get("gdp_growth") is not None:
        gdp = indicators["gdp_growth"]
        if gdp > 3:
            insights.append(f"Strong GDP growth at {gdp}%")
        elif gdp > 1:
            insights.append(f"Moderate GDP growth at {gdp}%")
        elif gdp > 0:
            insights.append(f"Weak GDP growth at {gdp}%")
        else:
            insights.append(f"GDP contracting at {gdp}%")

    if indicators.get("inflation_rate") is not None:
        inf = indicators["inflation_rate"]
        if inf > 4:
            insights.append(f"High inflation at {inf}% - hawkish Fed likely")
        elif inf > 2.5:
            insights.append(f"Elevated inflation at {inf}% - watching Fed closely")
        else:
            insights.append(f"Inflation cooling at {inf}% - near target")

    if indicators.get("yield_spread") is not None:
        spread = indicators["yield_spread"]
        if spread < 0:
            insights.append(f"Yield curve inverted ({spread}%) - recession signal")
        elif spread < 0.5:
            insights.append(f"Flat yield curve ({spread}%) - caution warranted")
        else:
            insights.append(f"Normal yield curve ({spread}%) - healthy signal")

    if volatility == "HIGH":
        insights.append("Elevated market volatility - proceed cautiously")
        confidence -= 0.1
    elif volatility == "LOW":
        insights.append("Low volatility - favorable for positioning")
        confidence += 0.05

    if indicators.get("vix") is not None:
        insights.append(f"VIX at {indicators['vix']} ({volatility})")

    confidence = max(0.5, min(0.95, confidence))

    result = {
        "market_regime": regime,
        "risk_environment": risk_environment,
        "investment_stance": stance,
        "confidence": round(confidence, 3),
        "indicators": {
            "gdp_growth": indicators.get("gdp_growth"),
            "inflation_rate": indicators.get("inflation_rate"),
            "unemployment_rate": indicators.get("unemployment_rate"),
            "interest_rate": indicators.get("interest_rate"),
            "treasury_10y": indicators.get("treasury_10y"),
            "treasury_2y": indicators.get("treasury_2y"),
            "yield_spread": indicators.get("yield_spread"),
            "vix": indicators.get("vix"),
            "consumer_sentiment": indicators.get("consumer_sentiment"),
            "risk_appetite": indicators["risk_appetite"],
            "liquidity_score": indicators["liquidity_score"],
            "volatility_regime": volatility,
        },
        "risk_score": round(risk_score, 3),
        "insights": insights,
        "timestamp": datetime.utcnow().isoformat(),
        "source": indicators["source"]
    }

    if indicators.get("error"):
        result["error"] = indicators["error"]

    return result


@mcp.tool()
def get_macro_indicators() -> Dict[str, Any]:
    """
    Get current macroeconomic indicators from FRED.

    Returns key economic metrics for investment analysis.
    """
    indicators = get_macro_data()

    result = {
        "gdp_growth": indicators.get("gdp_growth"),
        "inflation_rate": indicators.get("inflation_rate"),
        "unemployment_rate": indicators.get("unemployment_rate"),
        "interest_rate": indicators.get("interest_rate"),
        "treasury_10y": indicators.get("treasury_10y"),
        "treasury_2y": indicators.get("treasury_2y"),
        "yield_spread": indicators.get("yield_spread"),
        "vix": indicators.get("vix"),
        "consumer_sentiment": indicators.get("consumer_sentiment"),
        "market_regime": indicators["market_regime"],
        "risk_appetite": indicators["risk_appetite"],
        "liquidity_score": indicators["liquidity_score"],
        "timestamp": datetime.utcnow().isoformat(),
        "source": indicators["source"]
    }

    if indicators.get("error"):
        result["error"] = indicators["error"]

    return result


@mcp.tool()
def get_sector_outlook(sector: str) -> Dict[str, Any]:
    """
    Get macro outlook for specific sector.

    Args:
        sector: Sector name (e.g., "technology", "healthcare", "energy", "finance")
    """
    macro_analysis = analyze_macro()

    # Sector sensitivity to macro factors
    sector_multipliers = {
        "technology": 1.2,
        "healthcare": 0.8,
        "energy": 1.1,
        "finance": 1.3,
        "consumer": 1.0,
        "industrials": 1.1,
        "utilities": 0.7,
        "real_estate": 1.4,
        "DeFi": 1.3,
        "Layer1": 1.0,
        "NFT": 0.8,
    }

    multiplier = sector_multipliers.get(sector.lower(), 1.0)
    base_confidence = macro_analysis["confidence"]
    adjusted_confidence = base_confidence * multiplier

    return {
        "sector": sector,
        "macro_regime": macro_analysis["market_regime"],
        "sector_outlook": "POSITIVE" if adjusted_confidence > 0.65 else "NEGATIVE" if adjusted_confidence < 0.45 else "NEUTRAL",
        "confidence": round(adjusted_confidence, 3),
        "macro_context": macro_analysis["risk_environment"],
        "key_indicators": {
            "gdp": macro_analysis["indicators"].get("gdp_growth"),
            "inflation": macro_analysis["indicators"].get("inflation_rate"),
            "vix": macro_analysis["indicators"].get("vix"),
        },
        "timestamp": datetime.utcnow().isoformat(),
        "source": macro_analysis["source"]
    }


@mcp.tool()
def assess_portfolio_timing() -> Dict[str, Any]:
    """
    Assess whether current macro conditions favor portfolio changes.
    """
    macro_analysis = analyze_macro()

    regime = macro_analysis["market_regime"]
    risk_env = macro_analysis["risk_environment"]
    stance = macro_analysis["investment_stance"]

    if risk_env == "FAVORABLE" and regime in ["BULL", "CONSOLIDATION"]:
        timing = "FAVORABLE"
        action = "Consider increasing exposure"
        timing_score = 0.8
    elif risk_env == "CHALLENGING":
        timing = "UNFAVORABLE"
        action = "Consider defensive positioning"
        timing_score = 0.3
    else:
        timing = "NEUTRAL"
        action = "Maintain current allocation"
        timing_score = 0.5

    return {
        "timing_recommendation": timing,
        "suggested_action": action,
        "timing_score": round(timing_score, 3),
        "investment_stance": stance,
        "market_regime": regime,
        "risk_environment": risk_env,
        "confidence": macro_analysis["confidence"],
        "timestamp": datetime.utcnow().isoformat(),
        "source": macro_analysis["source"]
    }


@mcp.tool()
def get_correlation_analysis() -> Dict[str, Any]:
    """
    Analyze correlations between crypto and traditional markets.
    """
    macro_analysis = analyze_macro()

    risk_appetite = macro_analysis["indicators"]["risk_appetite"]
    # Higher risk appetite = higher crypto-equity correlation
    correlation = min(0.9, risk_appetite * 0.8 + 0.15)

    if correlation > 0.6:
        correlation_level = "HIGH"
        implication = "Crypto moving with equities - diversification limited"
    elif correlation < 0.4:
        correlation_level = "LOW"
        implication = "Crypto showing independence - good diversification"
    else:
        correlation_level = "MODERATE"
        implication = "Mixed correlation - typical relationship"

    return {
        "correlation_to_equities": round(correlation, 3),
        "correlation_level": correlation_level,
        "implication": implication,
        "diversification_benefit": round(1.0 - correlation, 3),
        "timestamp": datetime.utcnow().isoformat(),
        "source": macro_analysis["source"]
    }


if __name__ == "__main__":
    mcp.run()
