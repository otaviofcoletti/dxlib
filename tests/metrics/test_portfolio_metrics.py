import unittest
from datetime import datetime, timedelta

import dxlib as dx


class TestPortfolioMetrics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        security_manager = dx.SecurityManager.from_list(["AAPL", "MSFT"])

        cls.history = dx.History(
            {
                (datetime(2021, 1, 1),): {
                    "inventory": dx.Inventory({}),
                },
                (datetime(2021, 1, 2),): {
                    "inventory": dx.Inventory({
                        security_manager.get("AAPL"): 5,
                    }),
                },
                (datetime(2021, 1, 3),): {
                    "inventory": dx.Inventory({
                        security_manager.get("AAPL"): 10,
                        security_manager.get("MSFT"): 10,
                    }),
                },
            },
            schema=dx.Schema(
                levels=[dx.SchemaLevel.DATE],
                fields=["inventory"],
                security_manager=security_manager,
            ),
        )

        cls.price_history = dx.History(
            {
                (datetime(2021, 1, 1), "AAPL"): {"close": 100},
                (datetime(2021, 1, 1), "MSFT"): {"close": 200},
                (datetime(2021, 1, 2), "AAPL"): {"close": 110},
                (datetime(2021, 1, 2), "MSFT"): {"close": 210},
                (datetime(2021, 1, 3), "AAPL"): {"close": 120},
                (datetime(2021, 1, 3), "MSFT"): {"close": 220},
            },
            schema=dx.Schema(
                levels=[dx.SchemaLevel.DATE, dx.SchemaLevel.SECURITY],
                fields=["close"],
                security_manager=security_manager,
            ),
        )

    def test_value(self):
        portfolio = dx.Portfolio(self.history)

        metrics = dx.metrics.PortfolioMetrics()
        portfolio_value = metrics.value(portfolio, self.price_history)
        print(portfolio_value)

    def test_changes(self):
        portfolio = dx.Portfolio(self.history).cumsum()

        metrics = dx.metrics.PortfolioMetrics()
        changes = metrics.changes(portfolio)
        self.assertEqual(
            changes.history, self.history
        )

    def test_duration(self):
        portfolio = dx.Portfolio(self.history)

        metrics = dx.metrics.PortfolioMetrics()
        duration = metrics.duration(portfolio)
        self.assertEqual(
            duration, timedelta(days=3)
        )

    def test_exposure_time(self):
        portfolio = dx.Portfolio(self.history)

        metrics = dx.metrics.PortfolioMetrics()
        exposure_time = metrics.exposure_time(portfolio)
        self.assertAlmostEqual(
            exposure_time, 2/3, places=7
        )

    def test_equity(self):
        portfolio = dx.Portfolio(self.history)

        metrics = dx.metrics.PortfolioMetrics()
        equity, final, peak = metrics.equity(portfolio, self.price_history)
        self.assertEqual(
            final, 50
        )
        self.assertEqual(
            peak, 50
        )

    def test(self):
        portfolio = dx.Portfolio(self.history)

        print(
            dx.PortfolioMetrics.metrics(portfolio, self.price_history)
        )


if __name__ == '__main__':
    unittest.main()
