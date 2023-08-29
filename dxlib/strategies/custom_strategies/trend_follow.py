import pandas as pd

from ..strategy import Strategy
from ...core import History, Signal, TradeType


class TrendFollowStrategy(Strategy):
    """
    A trend-following strategy that generates buy/sell signals based on moving average crossovers.

    Parameters:
    - short_window (int): Short-term moving average window.
    - long_window (int): Long-term moving average window.

    Methods:
    - fit(history): Calculate moving averages and identify trends.
    - execute(row, idx, history) -> dict: Generate trading signals based on moving averages.
    """

    def __init__(self, short_window=50, long_window=200):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window

    def fit(self, history):
        """
        Calculate moving averages and identify trends.

        Args:
        - history (History): Historical price data of multiple equities.

        Returns:
        None
        """
        pass

    def execute(self, idx: pd.Index, position: pd.Series, history: History) -> pd.Series:
        """
        Generate trading signals based on moving average crossovers.

        Args:
        - row (pd.Series): Latest row of equity prices.
        - idx (int): Index of the current row.
        - history (pd.DataFrame): Historical price data of multiple equities.

        Returns:
        dict: Trading signals for each equity.
        """
        signals = pd.Series(Signal(TradeType.WAIT), index=history.df.index)
        if idx >= self.long_window:
            short_ma = history.indicators.sma(self.short_window).mean()
            long_ma = history.indicators.sma(self.long_window).mean()

            for idx, equity in enumerate(history.df.columns):
                if short_ma[equity] > long_ma[equity]:
                    signals[idx] = Signal(TradeType.BUY, 1)
                else:
                    signals[idx] = Signal(TradeType.SELL, 1)
        return signals
