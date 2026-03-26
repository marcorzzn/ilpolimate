import unittest
from src.analyzer import ContentAnalyzer

class TestContentAnalyzer(unittest.TestCase):
    def test_analyze_cluster_groq_empty_items(self):
        analyzer = ContentAnalyzer()
        result = analyzer.analyze_cluster_groq("test_cluster", [])
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
