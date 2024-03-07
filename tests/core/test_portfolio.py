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

    def test_portfolio(self):
        portfolio = Portfolio()
        self.assertIsInstance(portfolio, Portfolio)
        self.assertIsInstance(portfolio.inventory, dx.Inventory)
        self.assertEqual(len(portfolio.inventory), 0)

    def test_init(self):
        portfolio = Portfolio(self.inventory1)
        self.assertIsInstance(portfolio, Portfolio)
        self.assertIsInstance(portfolio.inventory, dx.Inventory)
        self.assertEqual(len(portfolio.inventory), 3)

    def test_add(self):
        portfolio1 = Portfolio(self.inventory1)
        portfolio2 = Portfolio(self.inventory2)
        portfolio3 = portfolio1 + portfolio2
        self.assertIsInstance(portfolio3, Portfolio)
        self.assertEqual(len(portfolio3.inventory), 3)
        self.assertEqual(portfolio3.inventory.get(self.security_manager.get("AAPL")), 500)

        portfolio3.add(self.inventory1)
        self.assertEqual(len(portfolio3.inventory), 3)

    def test_iadd(self):
        portfolio1 = Portfolio(self.inventory1)
        portfolio2 = Portfolio(self.inventory2)
        portfolio1 += portfolio2
        self.assertEqual(len(portfolio1.inventory), 3)
        self.assertEqual(portfolio1.inventory.get(self.security_manager.get("AAPL")), 500)

    def test_iter(self):
        portfolio = Portfolio(self.inventory1)
        for security in portfolio:
            self.assertIsInstance(security, dx.Security)


class TestPortfolioHistory(unittest.TestCase):
    security_manager = None
    inventory1 = None
    inventory2 = None
    portfolio1 = None
    portfolio2 = None

    @classmethod
    def setUpClass(cls):
        cls.security_manager = dx.SecurityManager.from_list(["AAPL", "GOOGL"])
        cls.inventory1 = dx.Inventory({
            cls.security_manager.get("AAPL"): 100,
            cls.security_manager.get("GOOGL"): 200,
        })
        cls.inventory2 = dx.Inventory({
            cls.security_manager.get("AAPL"): 400,
            cls.security_manager.get("GOOGL"): 500,
        })
        cls.portfolio1 = dx.Portfolio(cls.inventory1)
        cls.portfolio2 = dx.Portfolio(cls.inventory2)

    def test(self):
        portfolio = Portfolio(
            schema=dx.Schema(
                levels=[dx.SchemaLevel.DATE],
                fields=["inventory"],
                security_manager=self.security_manager
            )
        )

        history = {
            (datetime.datetime(2021, 1, 1),): {
                "inventory": self.inventory1
            },
            (datetime.datetime(2021, 1, 2), ): {
                "inventory": self.inventory2
            }
        }

        portfolio.add_history(history)
        self.assertEqual(len(portfolio.history), 2)
        self.assertEqual(portfolio.get(self.security_manager.get("AAPL")), 500)


if __name__ == '__main__':
    unittest.main()
