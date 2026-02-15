"""
Master test script - Run all server tests
"""

import subprocess
import sys
from pathlib import Path

# Test scripts to run in order
TESTS = [
    "test_market_server.py",
    "test_technical_server.py",
    "test_fundamental_server.py",
    "test_volatility_server.py",
    "test_news_server.py",
    "test_macro_server.py",
    "test_risk_server.py",
    "test_execution_server.py",
]

def run_test(test_file):
    """Run a single test script"""
    print(f"\n{'='*80}")
    print(f"Running: {test_file}")
    print('='*80)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=Path(__file__).parent,
            capture_output=False,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ {test_file} TIMED OUT")
        return False
    except Exception as e:
        print(f"❌ {test_file} FAILED: {e}")
        return False

def main():
    print("=" * 80)
    print("AutoFinance - Master Test Suite")
    print("=" * 80)
    print(f"\nRunning {len(TESTS)} test scripts...\n")
    
    results = {}
    for test in TESTS:
        results[test] = run_test(test)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results.values() if r)
    failed = len(results) - passed
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test}")
    
    print(f"\nTotal: {passed}/{len(results)} passed")
    
    if failed > 0:
        print(f"\n⚠️  {failed} test(s) failed!")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
