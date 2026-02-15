#!/usr/bin/env python3
"""
Test script for Fundamental Analysis MCP Server
Tests all tools with real Yahoo Finance data
"""

import sys
sys.path.append('/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/fundamental')

from server import (
    analyze_fundamentals,
    get_company_overview,
    compare_fundamentals,
    get_investment_thesis
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
    
    print("🧪 Testing Fundamental Analysis Server with REAL DATA")
    print("=" * 60)
    
    # Test 1: Analyze fundamentals for AAPL
    print("\n📊 Test 1: Analyze fundamentals for AAPL...")
    try:
        result = analyze_fundamentals("AAPL")
        print_result("Fundamental Analysis - AAPL", result)
        
        assert result.get("source") == "yahoo_finance", "Should use Yahoo Finance data"
        assert "recommendation" in result, "Should include recommendation"
        assert "scores" in result, "Should include scores"
        assert "fundamentals" in result, "Should include fundamental metrics"
        print("✅ AAPL fundamental analysis PASSED")
    except Exception as e:
        print(f"❌ AAPL fundamental analysis FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Company overview for MSFT
    print("\n📊 Test 2: Get company overview for MSFT...")
    try:
        result = get_company_overview("MSFT")
        print_result("Company Overview - MSFT", result)
        
        assert result.get("source") == "yahoo_finance", "Should use Yahoo Finance data"
        assert "valuation" in result, "Should have valuation data"
        assert "profitability" in result, "Should have profitability data"
        assert "growth" in result, "Should have growth data"
        print("✅ MSFT company overview PASSED")
    except Exception as e:
        print(f"❌ MSFT company overview FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Compare fundamentals
    print("\n📊 Test 3: Compare fundamentals across AAPL, MSFT, GOOGL...")
    try:
        result = compare_fundamentals(["AAPL", "MSFT", "GOOGL"])
        print_result("Compare Fundamentals", result)
        
        assert result.get("source") == "yahoo_finance", "Should use Yahoo Finance data"
        assert result.get("count") == 3, "Should compare all 3 symbols"
        assert "top_pick" in result, "Should identify top pick"
        print("✅ Fundamental comparison PASSED")
    except Exception as e:
        print(f"❌ Fundamental comparison FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Investment thesis for TSLA
    print("\n📊 Test 4: Generate investment thesis for TSLA...")
    try:
        result = get_investment_thesis("TSLA")
        print_result("Investment Thesis - TSLA", result)
        
        assert result.get("source") == "yahoo_finance", "Should use Yahoo Finance data"
        assert "investment_case" in result, "Should have investment case"
        assert "strengths" in result, "Should list strengths"
        assert "weaknesses" in result, "Should list weaknesses"
        print("✅ TSLA investment thesis PASSED")
    except Exception as e:
        print(f"❌ TSLA investment thesis FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
