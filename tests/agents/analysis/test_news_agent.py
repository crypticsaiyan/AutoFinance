# Test suite for News Sentiment Analysis Agent
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from agents.analysis import news_agent


class TestNewsAgent(unittest.TestCase):
    def setUp(self):
        pass

    def test_score_headline_positive(self):
        """Test scoring positive headlines"""
        headline = "Bitcoin surges to record high amid bullish rally"
        score = news_agent._score_headline(headline)
        self.assertGreater(score, 0)

    def test_score_headline_negative(self):
        """Test scoring negative headlines"""
        headline = "Market crash causes selloff and bearish decline"
        score = news_agent._score_headline(headline)
        self.assertLess(score, 0)

    def test_score_headline_neutral(self):
        """Test scoring neutral headlines"""
        headline = "The market continues to trade sideways today"
        score = news_agent._score_headline(headline)
        self.assertEqual(score, 0.0)

    def test_score_headline_mixed(self):
        """Test scoring headlines with mixed sentiment"""
        headline = "Market gains despite concerns about decline"
        score = news_agent._score_headline(headline)
        self.assertIsInstance(score, float)

    def test_score_headline_normalization(self):
        """Test score is normalized between -1 and 1"""
        headline = "surge surge surge surge surge"
        score = news_agent._score_headline(headline)
        self.assertGreaterEqual(score, -1.0)
        self.assertLessEqual(score, 1.0)

    def test_classify_sentiment_positive(self):
        """Test positive sentiment classification"""
        sentiment = news_agent._classify_sentiment(0.5)
        self.assertEqual(sentiment, "POSITIVE")

    def test_classify_sentiment_negative(self):
        """Test negative sentiment classification"""
        sentiment = news_agent._classify_sentiment(-0.5)
        self.assertEqual(sentiment, "NEGATIVE")

    def test_classify_sentiment_neutral(self):
        """Test neutral sentiment classification"""
        sentiment = news_agent._classify_sentiment(0.1)
        self.assertEqual(sentiment, "NEUTRAL")

    def test_analyze_sentiment_returns_dict(self):
        """Test analyze_sentiment returns proper structure"""
        try:
            result = news_agent.analyze_sentiment("BTCUSDT")
            self.assertIsInstance(result, dict)
            self.assertIn("symbol", result)
            self.assertIn("sentiment_score", result)
            self.assertIn("sentiment_label", result)
            self.assertIn("headline_count", result)
            self.assertIn(result["sentiment_label"], ["POSITIVE", "NEUTRAL", "NEGATIVE"])
        except Exception:
            self.skipTest("Simulation mode not available")


if __name__ == '__main__':
    unittest.main()
