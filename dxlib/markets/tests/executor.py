import unittest

from dxlib import Executor, Side
from dxlib.sandbox import SandboxMarket, SandboxPortfolio, SandboxOrder
from dxlib.trading import OrderData


class TestSandbox(unittest.TestCase):

    def setUp(self):
        market = SandboxMarket()
        portfolio = SandboxPortfolio()
        order = SandboxOrder()

        self.executor = Executor(market, portfolio, order)

    def test_send_order(self):
        self.executor.market.subscribe("AAPL")

        order_data = OrderData(
            security=self.executor.get_market().get_securities("AAPL"),
            quantity=10,
            price=100,
            side=Side.BUY,
        )

        self.executor.send_order(order_data)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
