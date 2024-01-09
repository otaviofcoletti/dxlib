import unittest

import pandas as pd

import dxlib as dx


class TestSimpleStrategy(unittest.TestCase):
    class SimpleStrategy(dx.Strategy):
        def __init__(self):
            super().__init__()

        @staticmethod
        def get_state(history: dx.History, idx):
            universe = history.level_unique(dx.HistoryLevel.SECURITY)

            levels = {
                dx.HistoryLevel.DATE: [idx],
            }

            prices = history.get(levels, fields=["close"]).df

            return universe, prices

        def execute(
            self, bar, position: dx.Inventory, history: dx.History
        ) -> pd.Series:
            idx, bar = bar
            universe, prices = self.get_state(history, idx)

            signals = {
                security: dx.Signal(dx.Side.BUY, 1, prices.loc[idx, security])
                for security in universe
            }

            return pd.Series(signals)

    def test_execute(self):
        strategy = self.SimpleStrategy()
        schema = dx.HistorySchema(
            levels=[dx.HistoryLevel.DATE, dx.HistoryLevel.SECURITY],
            fields=["close"],
            security_manager=dx.SecurityManager.from_list(["AAPL", "MSFT"]),
        )

        inventory = dx.Inventory({security: 0 for security in schema.security_manager})

        history = dx.History(
            {
                (pd.Timestamp("2021-01-01"), "AAPL"): {"close": 100},
                (pd.Timestamp("2021-01-01"), "MSFT"): {"close": 200},
                (pd.Timestamp("2021-01-02"), "AAPL"): {"close": 110},
                (pd.Timestamp("2021-01-02"), "MSFT"): {"close": 210},
            },
            schema,
        )

        executor = dx.Executor(strategy, inventory, schema)
        signals = executor.run(history)

        print(signals)


if __name__ == "__main__":
    unittest.main()
