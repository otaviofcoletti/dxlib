import unittest

import pandas as pd

import dxlib as dx
from dxlib import Inventory, History


class TestExecutor(unittest.TestCase):
    class LongOnlyStrategy(dx.Strategy):
        def execute(
                self, observation: any, position: Inventory, history: History
        ) -> pd.Series:
            idx, bar = observation
            date = idx[0]
            security = idx[1]

            signals = {
                (date, security): dx.OrderDetails(
                    security=security,
                    quantity=1,
                    price=bar["close"],
                    order_type=dx.OrderType.MARKET,
                    side=dx.Side.BUY,
                )
            }

            return pd.Series(signals)

    def setUp(self):
        self.schema = dx.HistorySchema(
            levels=[dx.HistoryLevel.DATE, dx.HistoryLevel.SECURITY],
            fields=["close"],
            security_manager=dx.SecurityManager.from_list(["AAPL", "MSFT"]),
        )
        self.sample_data = {
            (pd.Timestamp("2021-01-01"), "AAPL"): {"close": 100},
            (pd.Timestamp("2021-01-01"), "MSFT"): {"close": 200},
            (pd.Timestamp("2021-01-02"), "AAPL"): {"close": 110},
            (pd.Timestamp("2021-01-02"), "MSFT"): {"close": 210},
            (pd.Timestamp("2021-01-03"), "AAPL"): {"close": 120},
            (pd.Timestamp("2021-01-03"), "MSFT"): {"close": 220},
        }
        self.history = dx.History(self.sample_data, self.schema)

    def test_executor(self):
        position = dx.Inventory()
        strategy = self.LongOnlyStrategy()
        executor = dx.Executor(strategy, position, schema=self.schema)

        signals = executor.run(self.history)

        print(signals)


if __name__ == '__main__':
    unittest.main()
