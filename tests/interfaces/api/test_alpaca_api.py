import unittest
from dxlib.interfaces.external.alpaca_markets import AlpacaAPI
from config import API_KEY_PAPER, API_SECRET_PAPER


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.api = AlpacaAPI(API_KEY_PAPER, API_SECRET_PAPER, live=False)

    def test_auth(self):
        print(self.api.get_account())

    def test_get_order(self):
        print(self.api.get_orders())

    def test_get_positions(self):
        print(self.api.get_positions())


if __name__ == '__main__':
    unittest.main()
