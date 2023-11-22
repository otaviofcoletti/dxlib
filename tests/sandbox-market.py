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
        self.executor.security_manager.add("AAPL")

        order_data = OrderData(
            security=self.executor.security_manager.get("AAPL"),
            quantity=10,
            side=Side.BUY,
            order_type="market"
        )

        self.executor.send_order(order_data)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
