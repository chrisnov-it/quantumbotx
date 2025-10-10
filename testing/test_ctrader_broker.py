# testing/test_ctrader_broker.py
import unittest
from unittest.mock import patch
from datetime import datetime
from core.brokers.ctrader_broker import CTraderBroker

class TestCTraderBroker(unittest.TestCase):
    """
    Test cases for the cTrader broker implementation, focusing on market hours.
    """

    def setUp(self):
        """Set up a CTraderBroker instance for testing."""
        self.broker = CTraderBroker(demo=True)

    @patch('core.brokers.ctrader_broker.datetime')
    def test_is_market_open_weekday(self, mock_datetime):
        """Test that the market is open on a standard weekday."""
        # Wednesday, 12:00 UTC
        mock_datetime.utcnow.return_value = datetime(2023, 1, 4, 12, 0, 0)
        self.assertTrue(self.broker.is_market_open())

    @patch('core.brokers.ctrader_broker.datetime')
    def test_is_market_closed_saturday(self, mock_datetime):
        """Test that the market is closed on Saturday."""
        # Saturday, 12:00 UTC
        mock_datetime.utcnow.return_value = datetime(2023, 1, 7, 12, 0, 0)
        self.assertFalse(self.broker.is_market_open())

    @patch('core.brokers.ctrader_broker.datetime')
    def test_is_market_opens_sunday_evening(self, mock_datetime):
        """Test that the market opens on Sunday evening."""
        # Sunday, 22:01 UTC (market is open)
        mock_datetime.utcnow.return_value = datetime(2023, 1, 8, 22, 1, 0)
        self.assertTrue(self.broker.is_market_open())

    @patch('core.brokers.ctrader_broker.datetime')
    def test_is_market_closed_sunday_morning(self, mock_datetime):
        """Test that the market is closed on Sunday morning."""
        # Sunday, 10:00 UTC (market is closed)
        mock_datetime.utcnow.return_value = datetime(2023, 1, 8, 10, 0, 0)
        self.assertFalse(self.broker.is_market_open())

    @patch('core.brokers.ctrader_broker.datetime')
    def test_is_market_closes_friday_evening(self, mock_datetime):
        """Test that the market closes on Friday evening."""
        # Friday, 22:01 UTC (market is closed)
        mock_datetime.utcnow.return_value = datetime(2023, 1, 6, 22, 1, 0)
        self.assertFalse(self.broker.is_market_open())

    @patch('core.brokers.ctrader_broker.datetime')
    def test_is_market_open_friday_morning(self, mock_datetime):
        """Test that the market is open on Friday morning."""
        # Friday, 10:00 UTC (market is open)
        mock_datetime.utcnow.return_value = datetime(2023, 1, 6, 10, 0, 0)
        self.assertTrue(self.broker.is_market_open())

if __name__ == '__main__':
    unittest.main()
