#!/usr/bin/env python3
"""
Test script for Volatility Analysis MCP Server
Tests all tools with real Yahoo Finance data
"""

import sys
sys.path.append('/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/volatility')

from server import (
    calculate_historical_volatility,
    detect_volatility_regime,
    get_volatility_score,
    compare_volatility
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
            print(f"{key}:")
            for item in value:
                if isinstance(item, dict):
                    print(f"  - {item}")
                else:
                    print(f"  - {item}")
        else:
            print(f"{key}: {value}")
    print()


def test_all():
    """Run all tests"""
    
    print("🧪 Testing Volatility Analysis Server with REAL DATA")
    print("=" * 60)
    
    # Test 1: Historical volatility for AAPL
    print("\n📊 Test 1: Calculate historical volatility for AAPL...")
    try:
        result = calculate_historical_volatility("AAPL", "6mo")
        print_result("Historical Volatility - AAPL", result)
        
        assert result.get("source") == "yahoo_finance", "Should use Yahoo Finance data"
        assert result.get("data_points", 0) > 0, "Should have historical data points"
        assert "current_volatility" in result, "Should include current volatility"
        print("✅ AAPL historical volatility PASSED")
    except Exception as e:
        print(f"❌ AAPL historical volatility FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Volatility regime for BTC
    print("\n📊 Test 2: Detect volatility regime for BTCUSDT...")
    try:
        result = detect_volatility_regime("BTCUSDT")
        print_result("Volatility Regime - BTC", result)
        
        assert result.get("source") == "yahoo_finance", "Should use Yahoo Finance data"
        assert "regime" in result, "Should have regime classification"
        assert "percentile" in result, "Should have percentile ranking"
        print("✅ BTC volatility regime PASSED")
    except Exception as e:
        print(f"❌ BTC volatility regime FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Volatility score for TSLA
    print("\n📊 Test 3: Get volatility score for TSLA...")
    try:
        result = get_volatility_score("TSLA")
        print_result("Volatility Score - TSLA", result)
        
        assert "risk_level" in result, "Should have risk level"
        assert "risk_score" in result, "Should have risk score"
        assert result.get("risk_level") in ["LOW", "MEDIUM", "HIGH"], "Risk level should be valid"
        assert 0 <= result.get("risk_score", -1) <= 1, "Risk score should be 0-1"
        print("✅ TSLA volatility score PASSED")
    except Exception as e:
        print(f"❌ TSLA volatility score FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Compare volatility across symbols
    print("\n📊 Test 4: Compare volatility across AAPL, MSFT, TSLA...")
    try:
        result = compare_volatility(["AAPL", "MSFT", "TSLA"])
        print_result("Compare Volatility", result)
        
        assert result.get("count") == 3, "Should compare all 3 symbols"
        assert "highest_volatility" in result, "Should identify highest volatility"
        assert "lowest_volatility" in result, "Should identify lowest volatility"
        assert "average_volatility" in result, "Should calculate average"
        print("✅ Volatility comparison PASSED")
    except Exception as e:
        print(f"❌ Volatility comparison FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Crypto volatility analysis
    print("\n📊 Test 5: Analyze crypto volatility (ETHUSDT)...")
    try:
        result = get_volatility_score("ETHUSDT")
        print_result("Volatility Score - ETH", result)
        
        assert result.get("source") == "yahoo_finance", "Should use Yahoo Finance data"
        # Crypto typically has higher volatility than stocks
        assert result.get("volatility_pct", 0) > 0, "Should have measurable volatility"
        print("✅ ETH volatility analysis PASSED")
    except Exception as e:
        print(f"❌ ETH volatility analysis FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
