import unittest
from src.fetcher import FeedFetcher

class TestFeedFetcherCleanHtml(unittest.TestCase):
    def setUp(self):
        self.fetcher = FeedFetcher()

    def test_clean_html_empty_string(self):
        """Test that an empty string returns an empty string."""
        self.assertEqual(self.fetcher._clean_html(""), "")

    def test_clean_html_plain_text(self):
        """Test that plain text is returned unmodified."""
        text = "Hello world! This is plain text."
        self.assertEqual(self.fetcher._clean_html(text), text)

    def test_clean_html_p_tags(self):
        """Test that <p> and </p> are handled correctly."""
        html = "<p>First paragraph</p><p>Second paragraph</p>"
        # </p> becomes \n, so lines split.
        expected = "First paragraph\nSecond paragraph"
        self.assertEqual(self.fetcher._clean_html(html), expected)

    def test_clean_html_div_tags(self):
        """Test that <div> and </div> are removed."""
        html = "<div>Some content</div> <div>More content</div>"
        expected = "Some content More content"
        self.assertEqual(self.fetcher._clean_html(html), expected)

    def test_clean_html_br_tags(self):
        """Test that <br> and <br/> become newlines."""
        html = "Line 1<br>Line 2<br/>Line 3"
        expected = "Line 1\nLine 2\nLine 3"
        self.assertEqual(self.fetcher._clean_html(html), expected)

    def test_clean_html_massive_whitespace(self):
        """Test that massive whitespace and empty lines are removed."""
        html = "   Line 1   \n\n\n  \tLine 2 \n\nLine 3   "
        expected = "Line 1\nLine 2\nLine 3"
        self.assertEqual(self.fetcher._clean_html(html), expected)

    def test_clean_html_complex_mix(self):
        """Test a combination of tags and whitespace."""
        html = "<p>   First paragraph  </p><div>   Div content   </div><br/>  <p>Last paragraph</p>  "
        expected = "First paragraph\nDiv content\nLast paragraph"
        self.assertEqual(self.fetcher._clean_html(html), expected)

if __name__ == '__main__':
    unittest.main()
