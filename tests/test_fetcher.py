import unittest
from unittest.mock import patch

from src.fetcher import FeedFetcher

class TestFeedFetcher(unittest.TestCase):
    @patch('src.fetcher.feedparser.parse')
    def test_fetch_feed_exception_handling(self, mock_parse):
        # Configure the mock to raise a generic Exception
        mock_parse.side_effect = Exception("Mocked feedparser error")

        fetcher = FeedFetcher()
        result = fetcher.fetch_feed("http://fake-feed.url")

        # Verify the result is an empty list
        self.assertEqual(result, [])
        # Verify parse was actually called
        mock_parse.assert_called_once_with("http://fake-feed.url", agent=fetcher.user_agent)

if __name__ == '__main__':
    unittest.main()
