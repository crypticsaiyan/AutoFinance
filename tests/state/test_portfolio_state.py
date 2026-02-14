# Test suite for Portfolio State Management
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from state import portfolio_state


class TestPortfolioState(unittest.TestCase):
    def setUp(self):
        self.initial_state = portfolio_state.state.copy()

    def tearDown(self):
        portfolio_state.state = self.initial_state.copy()

    def test_state_structure(self):
        """Test portfolio state has required fields"""
        self.assertIn("capital", portfolio_state.state)
        self.assertIn("positions", portfolio_state.state)
        self.assertIn("daily_pnl", portfolio_state.state)
        self.assertIn("allocation", portfolio_state.state)
        self.assertIn("logs", portfolio_state.state)

    def test_initial_capital(self):
        """Test initial capital is correct"""
        self.assertEqual(portfolio_state.state["capital"], 100000)

    def test_positions_is_dict(self):
        """Test positions is a dictionary"""
        self.assertIsInstance(portfolio_state.state["positions"], dict)

    def test_daily_pnl_is_numeric(self):
        """Test daily PnL is numeric"""
        self.assertIsInstance(portfolio_state.state["daily_pnl"], (int, float))

    def test_logs_is_list(self):
        """Test logs is a list"""
        self.assertIsInstance(portfolio_state.state["logs"], list)


if __name__ == '__main__':
    unittest.main()
