import unittest
from src.bars import static_bar
from rich.text import Text

class TestStaticBar(unittest.TestCase):
    def test_full_bar(self):
        bar = static_bar(100, "green")
        self.assertIn("█", bar.plain)
        self.assertIn("100.0%", bar.plain)

    def test_half_bar(self):
        bar = static_bar(50, "yellow")
        self.assertIn("█", bar.plain)
        self.assertIn("50.0%", bar.plain)

    def test_empty_bar(self):
        bar = static_bar(0, "magenta")
        self.assertNotIn("█", bar.plain)
        self.assertIn("0.0%", bar.plain)

if __name__ == "__main__":
    unittest.main()