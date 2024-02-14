import unittest

from dxlib import Side, SecurityManager
from dxlib.sandbox import SandboxMarket, SandboxPortfolio, SandboxOrder
from dxlib.trading import OrderData


class TestSandbox(unittest.TestCase):
    def setUp(self):
        self.security_manager = SecurityManager()

        self.market = SandboxMarket(self.security_manager)
        self.portfolio = SandboxPortfolio()
        self.order = SandboxOrder()

    def test_order(self):
        self.security_manager.add("AAPL")

        order_data = OrderData(
            security=self.security_manager["AAPL"],
            quantity=10,
            side=Side.BUY,
            order_type="market",
        )

        self.order.send(order_data, self.market)

        self.assertEqual(True, True)

    def test_market(self):
        pass

    def test_portfolio(self):
        pass


if __name__ == "__main__":
    unittest.main()
