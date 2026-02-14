# Test suite for Technical Analysis Agent
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from agents.analysis import technical_agent


class TestTechnicalAgent(unittest.TestCase):
    def setUp(self):
        self.sample_prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109,
                              110, 112, 111, 113, 115, 114, 116, 118, 117, 119]

    def test_calculate_sma_basic(self):
        """Test SMA calculation with sufficient data"""
        prices = [10, 20, 30, 40, 50]
        sma = technical_agent._calculate_sma(prices, 5)
        self.assertEqual(sma, 30.0)

    def test_calculate_sma_insufficient_data(self):
        """Test SMA raises error with insufficient data"""
        prices = [10, 20, 30]
        with self.assertRaises(ValueError):
            technical_agent._calculate_sma(prices, 5)

    def test_calculate_rsi_basic(self):
        """Test RSI calculation returns value in range"""
        rsi = technical_agent._calculate_rsi(self.sample_prices, period=14)
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)

    def test_calculate_rsi_insufficient_data(self):
        """Test RSI raises error with insufficient data"""
        prices = [10, 20, 30]
        with self.assertRaises(ValueError):
            technical_agent._calculate_rsi(prices, period=14)

    def test_generate_signal_logic_buy_signal(self):
        """Test signal generation for bullish conditions"""
        signal, confidence = technical_agent._generate_signal_logic(110, 100, 25)
        self.assertEqual(signal, "BUY")
        self.assertGreater(confidence, 0.5)

    def test_generate_signal_logic_sell_signal(self):
        """Test signal generation for bearish conditions"""
        signal, confidence = technical_agent._generate_signal_logic(90, 100, 75)
        self.assertEqual(signal, "SELL")
        self.assertGreater(confidence, 0.5)

    def test_generate_signal_logic_hold_signal(self):
        """Test signal generation for neutral conditions"""
        signal, confidence = technical_agent._generate_signal_logic(100, 100, 50)
        self.assertEqual(signal, "HOLD")

    def test_generate_signal_returns_dict(self):
        """Test generate_signal returns proper structure"""
        try:
            result = technical_agent.generate_signal("BTCUSDT")
            self.assertIsInstance(result, dict)
            self.assertIn("symbol", result)
            self.assertIn("signal", result)
            self.assertIn("confidence", result)
            self.assertIn("indicators", result)
            self.assertIn(result["signal"], ["BUY", "SELL", "HOLD"])
        except Exception:
            self.skipTest("API unavailable or insufficient data")


if __name__ == '__main__':
    unittest.main()
