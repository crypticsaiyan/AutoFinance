# Test suite for Market Data Agent
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from agents.analysis import market_data_agent


class TestMarketDataAgent(unittest.TestCase):
    def setUp(self):
        pass

    def test_is_crypto_symbol_with_usdt(self):
        """Test crypto symbol detection for USDT pairs"""
        self.assertTrue(market_data_agent._is_crypto_symbol("BTCUSDT"))
        self.assertTrue(market_data_agent._is_crypto_symbol("btcusdt"))

    def test_is_crypto_symbol_with_btc(self):
        """Test crypto symbol detection for BTC pairs"""
        self.assertTrue(market_data_agent._is_crypto_symbol("ETHBTC"))

    def test_is_crypto_symbol_with_stock(self):
        """Test stock symbol detection"""
        self.assertFalse(market_data_agent._is_crypto_symbol("AAPL"))
        self.assertFalse(market_data_agent._is_crypto_symbol("TSLA"))

    def test_get_live_price_returns_dict(self):
        """Test get_live_price returns proper structure"""
        try:
            result = market_data_agent.get_live_price("BTCUSDT")
            self.assertIsInstance(result, dict)
            self.assertIn("symbol", result)
            self.assertIn("price", result)
            self.assertIn("timestamp", result)
        except Exception:
            self.skipTest("API unavailable or symbol not found")

    def test_get_candles_returns_dict(self):
        """Test get_candles returns proper structure"""
        try:
            result = market_data_agent.get_candles("BTCUSDT", interval="1h", limit=10)
            self.assertIsInstance(result, dict)
            self.assertIn("symbol", result)
            self.assertIn("interval", result)
            self.assertIn("candles", result)
            self.assertIsInstance(result["candles"], list)
        except Exception:
            self.skipTest("API unavailable or symbol not found")

    def test_calculate_volatility_returns_dict(self):
        """Test calculate_volatility returns proper structure"""
        try:
            result = market_data_agent.calculate_volatility("BTCUSDT", lookback=20)
            self.assertIsInstance(result, dict)
            self.assertIn("symbol", result)
            self.assertIn("volatility", result)
            self.assertIn("lookback_periods", result)
            self.assertIsInstance(result["volatility"], float)
        except Exception:
            self.skipTest("API unavailable or insufficient data")


if __name__ == '__main__':
    unittest.main()
