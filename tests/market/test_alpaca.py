import os
import unittest

import dxlib
from dxlib.markets.alpaca_markets import AlpacaAPI, AlpacaOrder


class TestAPI(unittest.TestCase):
    def setUp(self):
        # Load API keys from environment variables
        self.api = AlpacaAPI(os.environ.get("API_KEY_PAPER"), os.environ.get("API_SECRET_PAPER"), live=False)

    def test_auth(self):
        print(self.api.get_account())

    def test_get_order(self):
        print(self.api.get_orders())

    def test_get_positions(self):
        print(self.api.get_positions())


class TestInterface(unittest.TestCase):
    def setUp(self):
        self.api = AlpacaAPI(os.environ.get("API_KEY_PAPER"), os.environ.get("API_SECRET_PAPER"), live=False)
        self.order_interface = AlpacaOrder(self.api)

    def test_market(self):
        pass

    def test_portfolio(self):
        pass

    def test_order(self):
        print(self.order_interface.get())

    def test_post_order(self):
        order = dxlib.OrderData(dxlib.Security("AAPL"), 190.5, 10, -1, "limit")
        print(self.order_interface.post(order))


if __name__ == '__main__':
    unittest.main()
