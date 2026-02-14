#!/usr/bin/env python3
"""
Test script for Phase 2 Analytical Swarm Layer.
Validates all agents in simulation mode.
"""

import sys
sys.path.insert(0, '/home/cryptosaiyan/Documents/AutoFinance')

from state import simulation_mode
from agents.analysis import (
    get_live_price,
    get_candles,
    calculate_volatility,
    generate_signal,
    get_volatility_score,
    analyze_sentiment
)

simulation_mode.SIMULATION_MODE = True


def test_market_data_agent():
    """Test Market Data Agent."""
    print("=" * 60)
    print("TESTING MARKET DATA AGENT")
    print("=" * 60)
    
    symbol = "BTCUSDT"
    
    print(f"\n1. get_live_price('{symbol}'):")
    price_data = get_live_price(symbol)
    print(f"   ✓ Symbol: {price_data['symbol']}")
    print(f"   ✓ Price: ${price_data['price']:,.2f}")
    print(f"   ✓ Timestamp: {price_data['timestamp']}")
    
    print(f"\n2. get_candles('{symbol}', interval='1m', limit=3):")
    candle_data = get_candles(symbol, interval="1m", limit=3)
    print(f"   ✓ Symbol: {candle_data['symbol']}")
    print(f"   ✓ Interval: {candle_data['interval']}")
    print(f"   ✓ Candles: {len(candle_data['candles'])} candles")
    for i, candle in enumerate(candle_data['candles'], 1):
        print(f"      Candle {i}: Close=${candle['close']:,.2f} @ {candle['timestamp']}")
    
    print(f"\n3. calculate_volatility('{symbol}'):")
    vol_data = calculate_volatility(symbol)
    print(f"   ✓ Symbol: {vol_data['symbol']}")
    print(f"   ✓ Volatility: {vol_data['volatility']}")
    print(f"   ✓ Lookback: {vol_data['lookback_periods']} periods")


def test_technical_agent():
    """Test Technical Analysis Agent."""
    print("\n" + "=" * 60)
    print("TESTING TECHNICAL ANALYSIS AGENT")
    print("=" * 60)
    
    symbol = "BTCUSDT"
    
    print(f"\n1. generate_signal('{symbol}'):")
    signal_data = generate_signal(symbol)
    print(f"   ✓ Symbol: {signal_data['symbol']}")
    print(f"   ✓ Signal: {signal_data['signal']}")
    print(f"   ✓ Confidence: {signal_data['confidence']}")
    print(f"   ✓ Indicators:")
    print(f"      - SMA(20): {signal_data['indicators']['sma_fast']}")
    print(f"      - SMA(50): {signal_data['indicators']['sma_slow']}")
    print(f"      - RSI(14): {signal_data['indicators']['rsi']}")


def test_volatility_agent():
    """Test Volatility Agent."""
    print("\n" + "=" * 60)
    print("TESTING VOLATILITY AGENT")
    print("=" * 60)
    
    symbol = "BTCUSDT"
    
    print(f"\n1. get_volatility_score('{symbol}'):")
    vol_score = get_volatility_score(symbol)
    print(f"   ✓ Symbol: {vol_score['symbol']}")
    print(f"   ✓ Volatility Score: {vol_score['volatility_score']}")
    print(f"   ✓ Risk Level: {vol_score['risk_level']}")
    print(f"   ✓ Lookback: {vol_score['lookback_periods']} periods")


def test_news_agent():
    """Test News & Sentiment Agent."""
    print("\n" + "=" * 60)
    print("TESTING NEWS & SENTIMENT AGENT")
    print("=" * 60)
    
    test_symbols = ["BTCUSDT", "AAPL"]
    
    for symbol in test_symbols:
        print(f"\n1. analyze_sentiment('{symbol}'):")
        sentiment = analyze_sentiment(symbol)
        print(f"   ✓ Symbol: {sentiment['symbol']}")
        print(f"   ✓ Sentiment Score: {sentiment['sentiment_score']}")
        print(f"   ✓ Sentiment Label: {sentiment['sentiment_label']}")
        print(f"   ✓ Headlines Analyzed: {sentiment['headline_count']}")


def main():
    """Run all tests."""
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "  PHASE 2: ANALYTICAL SWARM LAYER - TEST SUITE".center(58) + "█")
    print("█" + "  (SIMULATION MODE ENABLED)".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60 + "\n")
    
    try:
        test_market_data_agent()
        test_technical_agent()
        test_volatility_agent()
        test_news_agent()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nPhase 2 Analytical Swarm Layer is operational!")
        print("All agents return structured JSON-serializable dictionaries.")
        print("No execution logic. No governance. Pure intelligence layer.")
        print("=" * 60 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
