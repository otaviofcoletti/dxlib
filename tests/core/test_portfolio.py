import datetime
import unittest

import dxlib as dx
from dxlib import Portfolio


class TestPortfolio(unittest.TestCase):
    inventory1 = None
    inventory2 = None
    security_manager = None

    @classmethod
    def setUpClass(cls):
        cls.security_manager = dx.SecurityManager.from_list(["AAPL", "GOOGL", "MSFT"])
        cls.inventory1 = dx.Inventory({
            cls.security_manager.get("AAPL"): 100,
            cls.security_manager.get("GOOGL"): 200,
            cls.security_manager.get("MSFT"): 300
        })
        cls.inventory2 = dx.Inventory({
            cls.security_manager.get("AAPL"): 400,
            cls.security_manager.get("GOOGL"): 500,
            cls.security_manager.get("MSFT"): 600
        })

        schema = dx.Schema(
                levels=[dx.SchemaLevel.DATE],
                fields=["inventory"],
                security_manager=cls.security_manager
            )

        cls.history1 = dx.History(
            {
                (datetime.datetime(2021, 1, 1),): {
                    "inventory": cls.inventory1
                },
            },
            schema=schema
        )

        cls.history2 = dx.History(
            {
                (datetime.datetime(2021, 1, 2),): {
                    "inventory": cls.inventory2
                },
            },
            schema=schema
        )

    def test_portfolio(self):
        portfolio = Portfolio()
        self.assertIsInstance(portfolio, Portfolio)
        self.assertIsInstance(portfolio.inventory, dx.Inventory)
        self.assertEqual(len(portfolio.inventory), 0)

    def test_init(self):
        portfolio = Portfolio(self.history1)
        self.assertIsInstance(portfolio, Portfolio)
        self.assertIsInstance(portfolio.inventory, dx.Inventory)
        self.assertEqual(len(portfolio.inventory), 3)

    def test_add(self):
        portfolio1 = Portfolio()
        portfolio2 = Portfolio(self.history2)
        portfolio3 = portfolio1 + portfolio2
        self.assertIsInstance(portfolio3, Portfolio)
        self.assertEqual(len(portfolio3.inventory), 3)
        self.assertEqual(portfolio3.inventory.get(self.security_manager.get("AAPL")), 400)

        portfolio3.add(datetime.datetime(2021, 1, 2), self.inventory2)
        self.assertEqual(len(portfolio3.inventory), 3)

    def test_iadd(self):
        portfolio1 = Portfolio()
        portfolio2 = Portfolio(self.history2)
        portfolio1 += portfolio2
        self.assertEqual(len(portfolio1.inventory), 3)
        self.assertEqual(portfolio1.inventory.get(self.security_manager.get("AAPL")), 400)

    def test_iter(self):
        portfolio = Portfolio(self.history1)
        for row in portfolio:
            self.assertIsInstance(row, tuple)
            idx, value = row
            self.assertIsInstance(idx[0], datetime.datetime)
            self.assertIsInstance(value['inventory'], dx.Inventory)


if __name__ == '__main__':
    unittest.main()
