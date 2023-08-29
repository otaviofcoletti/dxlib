import numpy as np
import pandas as pd

from ..strategy import Strategy
from ...core import History, Signal, TradeType


class PairTradingStrategy(Strategy):
    """
    A pair trading strategy that identifies trading opportunities between two correlated equities.

    Parameters:
    - threshold (float): Z-score threshold to trigger trading signals.

    Methods:
    - fit(history): Identify suitable pairs based on correlation and other criteria.
    - execute(row, idx, history) -> dict: Generate trading signals based on Z-score.
    """

    def __init__(self, threshold=2.0):
        super().__init__()
        self.threshold = threshold
        self.pair = None

    def fit(self, history):
        """
        Identify suitable pairs for trading based on correlation and other criteria.

        Args:
        - history (History): Historical price data of multiple equities.

        Returns:
        None
        """
        pass

    def execute(self, idx: pd.Index, position: pd.Series, history: History) -> pd.Series:
        """
        Generate trading signals based on the Z-score of the selected equity pair.

        Args:
        - row (pd.Series): Latest row of equity prices.
        - idx (int): Index of the current row.
        - history (pd.DataFrame): Historical price data of multiple equities.

        Returns:
        dict: Trading signals for each equity.
        """
        signals = pd.Series(Signal(TradeType.WAIT), index=position.index)
        if self.pair is not None:
            z_scores = (position[self.pair[0]] - position[self.pair[1]]) / np.std(
                history[self.pair[0]] - history[self.pair[1]]
            )
            if z_scores > self.threshold:
                signals[self.pair[0]] = Signal(TradeType.SELL, 1)
                signals[self.pair[1]] = Signal(TradeType.BUY, 1)
            elif z_scores < -self.threshold:
                signals[self.pair[0]] = Signal(TradeType.BUY, 1)
                signals[self.pair[1]] = Signal(TradeType.SELL, 1)
        return signals
