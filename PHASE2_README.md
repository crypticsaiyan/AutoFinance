# Phase 2: Analytical Swarm Layer

## Overview

The Analytical Swarm Layer is a deterministic, read-only intelligence layer composed of specialized agents that provide market analysis without any execution, governance, or state mutation capabilities.

## Architecture

```
agents/
├── analysis/
│   ├── __init__.py
│   ├── market_data_agent.py      # Price data & candles from Binance/Yahoo Finance
│   ├── technical_agent.py         # SMA/RSI indicators → BUY/SELL/HOLD signals
│   ├── volatility_agent.py        # Volatility scoring & risk classification
│   └── news_agent.py              # Deterministic keyword-based sentiment analysis

state/
└── simulation_mode.py             # Deterministic testing configuration
```

## Agent Specifications

### 1. Market Data Agent (`market_data_agent.py`)

**Exposed Tools:**
- `get_live_price(symbol)` - Current market price
- `get_candles(symbol, interval, limit)` - Historical candlestick data
- `calculate_volatility(symbol, lookback)` - Price volatility (std dev of returns)

**Data Sources:**
- Crypto symbols (ending in USDT/BTC): Binance REST API
- Stock symbols: Yahoo Finance (yfinance)

**Returns:**
```python
{
    "symbol": "BTCUSDT",
    "price": 48000.00,
    "timestamp": "2026-02-14T12:34:56Z"
}
```

### 2. Technical Analysis Agent (`technical_agent.py`)

**Exposed Tool:**
- `generate_signal(symbol)` - Generate BUY/SELL/HOLD signal

**Internal Indicators:**
- SMA(20) - Fast Simple Moving Average
- SMA(50) - Slow Simple Moving Average
- RSI(14) - Relative Strength Index

**Signal Logic:**
- Bullish trend (SMA20 > SMA50) + oversold (RSI < 30) → BUY (confidence: 0.85)
- Bearish trend + overbought (RSI > 70) → SELL (confidence: 0.85)
- Other combinations → BUY/SELL/HOLD with lower confidence

**Returns:**
```python
{
    "symbol": "BTCUSDT",
    "signal": "BUY",
    "confidence": 0.74,
    "indicators": {
        "sma_fast": 48210.1,
        "sma_slow": 47900.2,
        "rsi": 29.3
    }
}
```

### 3. Volatility Agent (`volatility_agent.py`)

**Exposed Tool:**
- `get_volatility_score(symbol, lookback)` - Volatility score & risk level

**Risk Classification:**
- `LOW`: volatility < 0.02
- `MEDIUM`: 0.02 ≤ volatility < 0.04
- `HIGH`: volatility ≥ 0.04

**Returns:**
```python
{
    "symbol": "BTCUSDT",
    "volatility_score": 0.05,
    "risk_level": "HIGH",
    "lookback_periods": 20
}
```

### 4. News & Sentiment Agent (`news_agent.py`)

**Exposed Tool:**
- `analyze_sentiment(symbol)` - Keyword-based sentiment analysis

**Implementation:**
- Level 1 deterministic engine only
- No ML, no LLM, no external sentiment APIs
- Predefined positive/negative keyword dictionaries
- Score normalization: -1.0 (negative) to +1.0 (positive)

**Sentiment Classification:**
- `POSITIVE`: score > 0.3
- `NEUTRAL`: -0.3 ≤ score ≤ 0.3
- `NEGATIVE`: score < -0.3

**Returns:**
```python
{
    "symbol": "BTCUSDT",
    "sentiment_score": -0.42,
    "sentiment_label": "NEGATIVE",
    "headline_count": 5
}
```

## Simulation Mode

**Purpose:** Deterministic testing and reproducible demos

**Configuration:** `state/simulation_mode.py`

**Usage:**
```python
from state import simulation_mode

# Enable simulation mode
simulation_mode.SIMULATION_MODE = True

# All agents will use simulated data
from agents.analysis import get_live_price
price_data = get_live_price("BTCUSDT")  # Returns simulated data
```

**Simulated Symbols:**
- `BTCUSDT` - Bitcoin (negative sentiment scenario)
- `AAPL` - Apple stock (positive sentiment scenario)
- `ETHUSDT` - Ethereum (neutral sentiment scenario)

## Testing

Run the test suite to validate all agents:

```bash
python3 test_phase2.py
```

**Expected Output:**
```
✓ Market Data Agent: Fetching prices, candles, volatility
✓ Technical Analysis Agent: Generating signals with SMA/RSI
✓ Volatility Agent: Computing risk scores
✓ News & Sentiment Agent: Analyzing sentiment from headlines
```

## Design Principles

### ✅ What This Layer Does
- Fetches real-time market data
- Computes technical indicators
- Assesses volatility and risk
- Analyzes news sentiment
- Returns structured, JSON-serializable dictionaries
- Supports deterministic simulation mode

### ❌ What This Layer Does NOT Do
- No portfolio state mutation
- No trade execution or proposals
- No governance checks or risk validation
- No global state changes
- No print statements or CLI logic
- No external state dependencies

## Integration Example

```python
from agents.analysis import (
    get_live_price,
    generate_signal,
    get_volatility_score,
    analyze_sentiment
)

# Analyze BTC
symbol = "BTCUSDT"

price = get_live_price(symbol)
signal = generate_signal(symbol)
volatility = get_volatility_score(symbol)
sentiment = analyze_sentiment(symbol)

# All return structured dictionaries
print(f"Price: ${price['price']:,.2f}")
print(f"Signal: {signal['signal']} (confidence: {signal['confidence']})")
print(f"Risk: {volatility['risk_level']}")
print(f"Sentiment: {sentiment['sentiment_label']}")
```

## Future Extensions

This read-only analytical layer is designed to be cleanly separable from:
- **Phase 3:** Governance & Risk Layer (portfolio validation, risk checks)
- **Phase 4:** Execution Layer (trade placement, order management)
- **Phase 5:** Orchestration Layer (multi-agent coordination)

Each agent can be independently consumed by higher-level supervisors or orchestrators without tight coupling.

## Dependencies

- `requests` - HTTP client for Binance API
- `yfinance` - Yahoo Finance data fetching
- Standard library: `statistics`, `datetime`, `re`

Install dependencies:
```bash
pip install requests yfinance
```

## Status

✅ **Phase 2 Complete**

All analytical agents implemented, tested, and operational in simulation mode.
