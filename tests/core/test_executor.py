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
                (date, security): dx.OrderData(
                    security=security,
                    quantity=1,
                    price=bar["close"],
                    order_type=dx.OrderType.MARKET,
                    side=dx.Side.BUY,
                )
            }

            return pd.Series(signals)

    def setUp(self):
        self.schema = dx.StandardSchema(
            levels=[dx.StandardLevel.DATE, dx.StandardLevel.SECURITY],
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
        executor = dx.Executor(strategy, position)

        signals = executor.run(self.history)

        self.assertEqual(len(signals), 6)
        for idx, signal in signals:
            self.assertEqual(signal.iloc[0].side, dx.Side.BUY)

    def test_async_executor(self):
        position = dx.Inventory()
        strategy = self.LongOnlyStrategy()
        executor = dx.Executor(strategy, position)

        def async_generator():
            for idx, bar in self.history:
                yield idx, bar

        signal_generator = executor.run(async_generator(), input_schema=self.schema)

        signal_list = []

        for signal in signal_generator:
            signal_list.append(signal)
            self.assertEqual(signal.iloc[0].side, dx.Side.BUY)

        self.assertEqual(len(signal_list), 6)


if __name__ == '__main__':
    unittest.main()
