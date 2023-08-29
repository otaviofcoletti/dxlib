import numpy as np
import pandas as pd

from ..strategy import Strategy
from ...core import Signal, History, TradeType


class BollingerBreakoutStrategy(Strategy):
    def __init__(self, window=15, short_window=7, long_window=30, multiplier=1):
        super().__init__()
        self.multiplier = multiplier
        self.short_window = short_window
        self.long_window = long_window
        self.window = window

    def execute(self, idx: pd.Index, position: pd.Series, history: History) -> pd.Series:
        signals = pd.Series(Signal("wait"), index=history.df.columns)
        volatility = history.indicators.volatility()

        upper, lower = history.indicators.bollinger_bands(self.window)
        var_mean = np.mean(upper - lower)
        var_var = np.std(upper - lower)

        var_historical = ((upper - lower) - var_mean) / var_var

        var_normalized = (volatility.loc[idx] - var_mean) / var_var

        pos = history.df.index.get_loc(idx)
        short_ma = history.df.iloc[pos - self.short_window : pos].mean()
        long_ma = history.df.iloc[pos - self.long_window : pos].mean()

        for idx, equity in enumerate(history.df.columns):
            if abs(var_normalized[equity]) > abs(self.multiplier * var_historical):
                if short_ma[equity] > long_ma[equity]:
                    signals[equity] = Signal(TradeType.BUY, 1)
                else:
                    signals[equity] = Signal(TradeType.SELL, 1)

        return signals
