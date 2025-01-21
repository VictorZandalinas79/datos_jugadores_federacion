import unittest
from src.scraper import FootballScraper

class TestFootballScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = FootballScraper()

    def test_get_player_ids(self):
        # Add your test cases here
        pass

    def test_get_player_data(self):
        # Add your test cases here
        pass

if __name__ == '__main__':
    unittest.main()