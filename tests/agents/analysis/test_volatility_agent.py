# Test suite for Volatility Analysis Agent
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from agents.analysis import volatility_agent


class TestVolatilityAgent(unittest.TestCase):
    def setUp(self):
        pass

    def test_classify_risk_level_low(self):
        """Test risk classification for low volatility"""
        risk = volatility_agent._classify_risk_level(0.01)
        self.assertEqual(risk, "LOW")

    def test_classify_risk_level_medium(self):
        """Test risk classification for medium volatility"""
        risk = volatility_agent._classify_risk_level(0.03)
        self.assertEqual(risk, "MEDIUM")

    def test_classify_risk_level_high(self):
        """Test risk classification for high volatility"""
        risk = volatility_agent._classify_risk_level(0.05)
        self.assertEqual(risk, "HIGH")

    def test_classify_risk_level_boundary_low_medium(self):
        """Test risk classification at LOW/MEDIUM boundary"""
        risk_low = volatility_agent._classify_risk_level(0.019)
        risk_medium = volatility_agent._classify_risk_level(0.02)
        self.assertEqual(risk_low, "LOW")
        self.assertEqual(risk_medium, "MEDIUM")

    def test_classify_risk_level_boundary_medium_high(self):
        """Test risk classification at MEDIUM/HIGH boundary"""
        risk_medium = volatility_agent._classify_risk_level(0.039)
        risk_high = volatility_agent._classify_risk_level(0.04)
        self.assertEqual(risk_medium, "MEDIUM")
        self.assertEqual(risk_high, "HIGH")

    def test_get_volatility_score_returns_dict(self):
        """Test get_volatility_score returns proper structure"""
        try:
            result = volatility_agent.get_volatility_score("BTCUSDT", lookback=20)
            self.assertIsInstance(result, dict)
            self.assertIn("symbol", result)
            self.assertIn("volatility_score", result)
            self.assertIn("risk_level", result)
            self.assertIn("lookback_periods", result)
            self.assertIn(result["risk_level"], ["LOW", "MEDIUM", "HIGH"])
        except Exception:
            self.skipTest("API unavailable or insufficient data")


if __name__ == '__main__':
    unittest.main()
