import unittest

import numpy as np
import pandas as pd
from dxlib import TechnicalIndicators as ti
import dxlib as dx
from dxlib import Strategy, History, Inventory, Signal, Side, SchemaLevel


class BreakoutStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.field = 'close'
        self.lookback_period = 5
        self.multiplier = 0.25

    def execute(
            self, observation: any, history: History, position: Inventory
    ) -> pd.Series:
        levels = history.levels_unique()
        idx, _ = observation
        signals = pd.Series(
            Signal(Side.WAIT), index=pd.MultiIndex.from_tuples([idx], names=levels.keys())
        )

        security_level = history.schema.levels.index(SchemaLevel.SECURITY)
        security = idx[security_level]

        df = history.get_df({SchemaLevel.SECURITY: [security]}, [self.field])

        volatility = ti.volatility(df, self.lookback_period)

        if len(df) > self.lookback_period * 2:
            volatility_lookback = np.mean(volatility.reset_index()[self.field].dropna().iloc[len(df) - self.lookback_period: len(df)])
            if volatility_lookback and all(volatility.loc[idx] > self.multiplier * volatility_lookback):
                signals[idx] = Signal(dx.Side.BUY, 1)
        return signals


class TestBreakoutStrategy(unittest.TestCase):
    strategy = None
    executor = None

    @classmethod
    def setUpClass(cls):
        cls.strategy = BreakoutStrategy()
        cls.executor = dx.Executor(cls.strategy)

    def test_execute(self):
        api = dx.interfaces.YFinanceAPI()
        historical = api.historical(
            ['AAPL', 'BTC-USD', 'NVDC34.SA'],
            dx.Date.prevdays(365),
            dx.Date.today()
        )
        signals = self.executor.run(historical)
        portfolio = dx.Portfolio.from_orders(dx.OrderInterface.execute_history(signals))
        print(signals)
        print(dx.PortfolioMetrics.equity(portfolio, historical))


if __name__ == "__main__":
    unittest.main()
