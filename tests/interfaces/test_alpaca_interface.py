import unittest

from dxlib import Side, SecurityManager
from dxlib.interfaces.external.alpaca_markets import AlpacaAPI, AlpacaOrder, AlpacaMarket, AlpacaPortfolio
from dxlib.trading import OrderData

from tests.interfaces.config import API_KEY_PAPER, API_SECRET_PAPER


class TestAlpacaInterface(unittest.TestCase):
    def setUp(self):
        self.api = AlpacaAPI(API_KEY_PAPER, API_SECRET_PAPER, live=False)
        self.order_interface = AlpacaOrder(self.api)
        self.market_interface = AlpacaMarket(self.api)
        self.portfolio_interface = AlpacaPortfolio(self.api)

        self.security_manager = SecurityManager()
        self.security_manager.add("AAPL")

    def test_market(self):
        market = self.market_interface.get()
        print(market)

    def test_portfolio_position(self):
        portfolio = self.portfolio_interface.get()
        print(portfolio)

    def test_portfolio_open(self):
        portfolio = self.portfolio_interface.get_open()
        print(portfolio)

    def test_portfolio(self):
        portfolio = self.portfolio_interface.get() + self.portfolio_interface.get_open()
        print(portfolio.accumulate())

    def test_get_order(self):
        print(self.order_interface.get())

    def test_post_order(self):

        order_data = OrderData(
            security=self.security_manager["AAPL"],
            side=Side.SELL,
            quantity=1,
            order_type="market",
        )

        order = self.order_interface.send(order_data, self.market_interface)
        print(order)


if __name__ == '__main__':
    unittest.main()
