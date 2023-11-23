import unittest
from dxlib.markets import AlpacaAPI
from config import API_KEY, API_SECRET


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.api = AlpacaAPI(API_KEY, API_SECRET, live=True)

    def test_auth(self):
        print(self.api.get_account())

    def test_get_order(self):
        pass


if __name__ == '__main__':
    unittest.main()
