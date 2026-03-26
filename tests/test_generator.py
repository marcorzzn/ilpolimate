import unittest
import sys
from unittest.mock import patch, mock_open, MagicMock
import json
import os

# Mock dependencies before importing the module under test
sys.modules['markdown'] = MagicMock()
sys.modules['gtts'] = MagicMock()

from src.generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        # We can use default paths or specific ones for testing
        self.output_dir = "test_posts"
        self.site_data_dir = "test_assets/data"
        self.audio_dir = "test_assets/audio"

        # Patch os.makedirs to avoid creating directories during initialization
        with patch('os.path.exists', return_value=True):
            self.generator = ReportGenerator(
                output_dir=self.output_dir,
                site_data_dir=self.site_data_dir
            )

    @patch('builtins.open', new_callable=mock_open)
    def test_save_ticker_data(self, mocked_open):
        # Sample headlines data
        headlines = [
            {"symbol": "AAPL", "price": 150.0, "change": 1.5},
            {"symbol": "GOOGL", "price": 2800.0, "change": -0.5}
        ]

        # Call the method under test
        self.generator.save_ticker_data(headlines)

        # Verify the file path
        expected_path = os.path.join(self.site_data_dir, "headlines.json")
        mocked_open.assert_called_once_with(expected_path, "w", encoding="utf-8")

        # Verify the content written
        # json.dump calls write multiple times or once depending on implementation
        # For simple verification, we can join all calls to write
        written_content = "".join(call.args[0] for call in mocked_open().write.call_args_list)
        self.assertEqual(json.loads(written_content), headlines)

if __name__ == '__main__':
    unittest.main()
