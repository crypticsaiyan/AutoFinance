---
name: technical-analysis-implementation
description: Implement technical analysis indicators and strategies for the AutoFinance platform. Use when adding new indicators or trading strategies.
license: MIT
---

# Technical Analysis Implementation Skill

This skill guides the implementation of technical analysis indicators and trading strategies.

## Implementation Guidelines

### 1. Indicator Structure

Every technical indicator should follow this structure:

```python
from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class IndicatorResult:
    """Standard result format for technical indicators."""
    values: np.ndarray
    signal: str  # 'buy', 'sell', 'hold'
    metadata: dict

def calculate_indicator(
    prices: np.ndarray,
    period: int = 14,
    **kwargs
) -> IndicatorResult:
    """
    Calculate technical indicator.
    
    Args:
        prices: Array of price data
        period: Lookback period for calculation
        **kwargs: Additional parameters
        
    Returns:
        IndicatorResult with calculated values
    """
    # Input validation
    if len(prices) < period:
        raise ValueError(f"Not enough data: need {period}, got {len(prices)}")
    
    # Calculation (vectorized)
    values = np.convolve(prices, np.ones(period)/period, mode='valid')
    
    # Generate signal
    signal = 'hold'
    if values[-1] > values[-2]:
        signal = 'buy'
    elif values[-1] < values[-2]:
        signal = 'sell'
    
    return IndicatorResult(
        values=values,
        signal=signal,
        metadata={'period': period}
    )
```

### 2. Common Indicators

#### Moving Averages
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)
- Weighted Moving Average (WMA)

#### Momentum Indicators
- Relative Strength Index (RSI)
- Stochastic Oscillator
- MACD (Moving Average Convergence Divergence)

#### Volatility Indicators
- Bollinger Bands
- Average True Range (ATR)
- Standard Deviation

#### Volume Indicators
- On-Balance Volume (OBV)
- Volume-Weighted Average Price (VWAP)
- Money Flow Index (MFI)

### 3. Performance Optimization

Always vectorize calculations using NumPy:

```python
# BAD: Using loops
def sma_slow(prices, period):
    result = []
    for i in range(len(prices) - period + 1):
        result.append(sum(prices[i:i+period]) / period)
    return result

# GOOD: Vectorized
def sma_fast(prices, period):
    return np.convolve(prices, np.ones(period)/period, mode='valid')
```

### 4. Testing Indicators

Always include tests with known values:

```python
def test_sma():
    """Test SMA with known values."""
    prices = np.array([1, 2, 3, 4, 5])
    result = calculate_sma(prices, period=3)
    expected = np.array([2.0, 3.0, 4.0])  # (1+2+3)/3, (2+3+4)/3, (3+4+5)/3
    np.testing.assert_array_almost_equal(result, expected)
```

### 5. Signal Generation

Implement clear signal logic:

```python
def generate_signals(indicator_values: np.ndarray, threshold: float = 70):
    """
    Generate buy/sell signals from indicator values.
    
    Args:
        indicator_values: Array of indicator values
        threshold: Overbought/oversold threshold
        
    Returns:
        List of signals ('buy', 'sell', 'hold')
    """
    signals = []
    for i in range(1, len(indicator_values)):
        if indicator_values[i] < (100 - threshold) and indicator_values[i-1] >= (100 - threshold):
            signals.append('buy')  # Cross below oversold
        elif indicator_values[i] > threshold and indicator_values[i-1] <= threshold:
            signals.append('sell')  # Cross above overbought
        else:
            signals.append('hold')
    return signals
```

### 6. Integration with MCP Server

Add indicators as tools in the technical analysis server:

```python
@server.tool()
async def calculate_rsi(
    symbol: str,
    period: int = 14,
    timeframe: str = "1d"
) -> dict:
    """
    Calculate Relative Strength Index for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        period: RSI period (default 14)
        timeframe: Time frame (1d, 1h, 5m, etc.)
        
    Returns:
        Dictionary with RSI values and signals
    """
    # Fetch price data
    prices = await fetch_price_data(symbol, timeframe)
    
    # Calculate RSI
    result = calculate_rsi_indicator(prices, period)
    
    return {
        'symbol': symbol,
        'rsi': float(result.values[-1]),
        'signal': result.signal,
        'timestamp': datetime.now().isoformat(),
        'metadata': result.metadata
    }
```

## Best Practices

1. **Validate Inputs**: Always check for sufficient data and valid parameters
2. **Handle Edge Cases**: Account for NaN values, empty arrays, etc.
3. **Document Formulas**: Include the mathematical formula in docstrings
4. **Use NumPy**: Vectorize all calculations for performance
5. **Return Metadata**: Include calculation parameters in results
6. **Test Thoroughly**: Test with real and synthetic data
7. **Cache Results**: Cache expensive calculations when possible
8. **Time Complexity**: Aim for O(n) or better complexity

## Example: RSI Implementation

```python
def calculate_rsi(prices: np.ndarray, period: int = 14) -> IndicatorResult:
    """
    Calculate Relative Strength Index.
    
    Formula:
    RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss
    
    Args:
        prices: Array of closing prices
        period: RSI period (default 14)
        
    Returns:
        IndicatorResult with RSI values
    """
    # Calculate price changes
    deltas = np.diff(prices)
    
    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate average gains and losses
    avg_gains = np.convolve(gains, np.ones(period)/period, mode='valid')
    avg_losses = np.convolve(losses, np.ones(period)/period, mode='valid')
    
    # Calculate RS and RSI
    rs = avg_gains / (avg_losses + 1e-10)  # Avoid division by zero
    rsi = 100 - (100 / (1 + rs))
    
    # Generate signal
    signal = 'hold'
    if rsi[-1] < 30:
        signal = 'buy'  # Oversold
    elif rsi[-1] > 70:
        signal = 'sell'  # Overbought
    
    return IndicatorResult(
        values=rsi,
        signal=signal,
        metadata={'period': period, 'overbought': 70, 'oversold': 30}
    )
```
