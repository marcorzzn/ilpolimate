import unittest
import re

def simulate_news_rendering(item):
    """Simulates the logic in ultima-ora.html for rendering news items."""
    source_name = item.get('source') or "AGENZIA"
    if len(source_name) > 20:
        source_name = source_name[:17] + "..."

    time_str = "ORA"
    # Published date parsing not easily testable here without mocking Date

    desc = item.get('content') or ""
    if desc.startswith("[FONTE ORIGINALE:"):
        idx = desc.find("]")
        if idx != -1:
            desc = desc[idx + 1:]
            # The actual regex in JS was .replace(/^ - /, "")
            desc = re.sub(r'^ - ', '', desc).strip()

    # The fix uses textContent and regex stripping
    # Simulate stripping: .replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim()
    title_processed = re.sub(r'<[^>]*>', '', item.get('title', ''))
    desc_processed = re.sub(r'<[^>]*>', '', desc).replace('&nbsp;', ' ').strip()

    return {
        'source': source_name,
        'title': title_processed,
        'desc': desc_processed
    }

class TestXSSFix(unittest.TestCase):
    def test_html_stripping(self):
        item = {
            "source": "Test Source",
            "title": "Title with <strong>HTML</strong>",
            "content": "[FONTE ORIGINALE: Test] - This is <em>content</em> with &nbsp; entities."
        }
        rendered = simulate_news_rendering(item)

        self.assertEqual(rendered['title'], "Title with HTML")
        self.assertEqual(rendered['desc'], "This is content with   entities.")

    def test_xss_injection_strip(self):
        item = {
            "source": "Malicious",
            "title": "Safe Title",
            "content": "[FONTE ORIGINALE: Hack] - <script>alert('XSS')</script>But this is text."
        }
        rendered = simulate_news_rendering(item)

        # In reality, textContent would escape the tags if they weren't stripped,
        # but our code also explicitly strips them.
        self.assertNotIn("<script>", rendered['desc'])
        self.assertIn("alert('XSS')But this is text.", rendered['desc'])

    def test_source_cleanup(self):
        item = {
            "source": "A Very Long Source Name That Exceeds Twenty Characters",
            "title": "Title",
            "content": "Content"
        }
        rendered = simulate_news_rendering(item)
        self.assertTrue(len(rendered['source']) <= 20)
        self.assertTrue(rendered['source'].endswith("..."))

if __name__ == '__main__':
    unittest.main()
