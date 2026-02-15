#!/usr/bin/env python3
"""
Test script for Technical Analysis MCP Server
Tests all tools with real Yahoo Finance data
"""

import sys
sys.path.append('/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/technical')

from server import (
    generate_signal,
    calculate_support_resistance,
    calculate_rsi_tool,
    calculate_macd_tool,
    calculate_bollinger_bands_tool
)


def print_result(test_name: str, result: dict):
    """Pretty print test results"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    for key, value in result.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        elif isinstance(value, list):
            print(f"{key}: {', '.join(str(v) for v in value)}")
        else:
            print(f"{key}: {value}")
    print()


def test_all():
    """Run all tests"""
    
    print("🧪 Testing Technical Analysis Server with REAL DATA")
    print("=" * 60)
    
    # Test 1: Generate signal for AAPL
    print("\n📊 Test 1: Generate trading signal for AAPL...")
    try:
        result = generate_signal("AAPL", "3mo")
        print_result("Generate Signal - AAPL", result)
        
        # Verify real data
        assert result.get("source") == "yahoo_finance", "Should use Yahoo Finance data"
        assert result.get("data_points", 0) > 0, "Should have historical data points"
        assert "indicators" in result, "Should include technical indicators"
        print("✅ AAPL signal generation PASSED")
    except Exception as e:
        print(f"❌ AAPL signal generation FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Generate signal for BTC
    print("\n📊 Test 2: Generate trading signal for BTCUSDT...")
    try:
        result = generate_signal("BTCUSDT", "3mo")
        print_result("Generate Signal - BTC", result)
        
        assert result.get("source") == "yahoo_finance", "Should use Yahoo Finance data"
        assert result.get("data_points", 0) > 0, "Should have historical data points"
        print("✅ BTC signal generation PASSED")
    except Exception as e:
        print(f"❌ BTC signal generation FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: RSI Calculation
    print("\n📊 Test 3: Calculate RSI for MSFT...")
    try:
        result = calculate_rsi_tool("MSFT", 14)
        print_result("RSI - MSFT", result)
        
        assert "rsi" in result, "Should have RSI value"
        assert 0 <= result.get("rsi", -1) <= 100, "RSI should be between 0 and 100"
        assert "interpretation" in result, "Should have interpretation"
        print("✅ RSI calculation PASSED")
    except Exception as e:
        print(f"❌ RSI calculation FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: MACD Calculation
    print("\n📊 Test 4: Calculate MACD for TSLA...")
    try:
        result = calculate_macd_tool("TSLA")
        print_result("MACD - TSLA", result)
        
        assert "macd" in result, "Should have MACD value"
        assert "signal" in result, "Should have signal line"
        assert "histogram" in result, "Should have histogram"
        assert "trend" in result, "Should have trend direction"
        print("✅ MACD calculation PASSED")
    except Exception as e:
        print(f"❌ MACD calculation FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Bollinger Bands
    print("\n📊 Test 5: Calculate Bollinger Bands for GOOGL...")
    try:
        result = calculate_bollinger_bands_tool("GOOGL", 20)
        print_result("Bollinger Bands - GOOGL", result)
        
        assert "upper_band" in result, "Should have upper band"
        assert "middle_band" in result, "Should have middle band"
        assert "lower_band" in result, "Should have lower band"
        assert "position" in result, "Should have position"
        print("✅ Bollinger Bands calculation PASSED")
    except Exception as e:
        print(f"❌ Bollinger Bands calculation FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 6: Support and Resistance
    print("\n📊 Test 6: Calculate Support/Resistance for NVDA...")
    try:
        result = calculate_support_resistance("NVDA", "6mo")
        print_result("Support/Resistance - NVDA", result)
        
        assert "support_levels" in result, "Should have support levels"
        assert "resistance_levels" in result, "Should have resistance levels"
        assert "current_price" in result, "Should have current price"
        print("✅ Support/Resistance calculation PASSED")
    except Exception as e:
        print(f"❌ Support/Resistance calculation FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
