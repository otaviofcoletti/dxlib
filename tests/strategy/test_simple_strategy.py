import unittest

import pandas as pd

import dxlib as dx


class TestSimpleStrategy(unittest.TestCase):
    class SimpleStrategy(dx.Strategy):
        def __init__(self):
            super().__init__()

        def execute(self, idx, position: dx.Inventory, history: dx.History) -> pd.Series:
            # Simple strategy, buy and hold for every asset in the universe
            universe = history.get_level(dx.HistoryLevel.SECURITY)
            return pd.Series(
                dx.Signal(
                    side=dx.Side.BUY,
                    quantity=1,
                    price=history.get_raw(securities=universe, fields=['close'], dates=[idx])
                ),
                index=universe
            )

    def test_execute(self):
        pass


if __name__ == '__main__':
    unittest.main()
