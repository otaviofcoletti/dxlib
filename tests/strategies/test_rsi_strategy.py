import unittest

import pandas as pd

import dxlib as dx
from dxlib.strategies.custom_strategies import RsiStrategy


class TestRSIStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = RsiStrategy(window=1)

    def test_execute(self):
        schema = dx.HistorySchema(
            levels=[dx.HistoryLevel.DATE, dx.HistoryLevel.SECURITY],
            fields=["close"],
            security_manager=dx.SecurityManager.from_list(["AAPL", "MSFT"]),
        )

        inventory = dx.Inventory({security: 0 for security in schema.security_manager.values()})

        history = dx.History(
            {
                (pd.Timestamp("2021-01-01"), "AAPL"): {"close": 100},
                (pd.Timestamp("2021-01-01"), "MSFT"): {"close": 200},
                (pd.Timestamp("2021-01-02"), "AAPL"): {"close": 110},
                (pd.Timestamp("2021-01-02"), "MSFT"): {"close": 210},
                (pd.Timestamp("2021-01-03"), "AAPL"): {"close": 120},
                (pd.Timestamp("2021-01-03"), "MSFT"): {"close": 220},
            },
            schema,
        )

        executor = dx.Executor(self.strategy, inventory, schema)
        signals = executor.run(history)

        # date       security
        # 2021-01-01 AAPL (equity)  WAIT: None @ None
        #            MSFT (equity)  WAIT: None @ None
        # 2021-01-02 AAPL (equity)      SELL: 1 @ 110
        #            MSFT (equity)      SELL: 1 @ 210
        # 2021-01-03 AAPL (equity)      SELL: 1 @ 120
        #            MSFT (equity)      SELL: 1 @ 220
        self.assertEqual(
            signals.df.iloc[-1].to_dict()[0],
            dx.Signal(dx.Side.SELL, 1))

        self.assertEqual(
            signals.df.iloc[-2].to_dict()[0],
            dx.Signal(dx.Side.SELL, 1))


if __name__ == "__main__":
    unittest.main()
