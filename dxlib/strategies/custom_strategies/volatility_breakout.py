import numpy as np
import pandas as pd

from ..strategy import Strategy
from ...core import History, Signal, TradeType


class VolatilityBreakoutStrategy(Strategy):
    """
    A volatility breakout strategy that generates buy signals during periods of high volatility.

    Parameters:
    - lookback_period (int): Number of days to calculate historical volatility.
    - multiplier (float): Multiplier for determining high volatility.

    Methods:
    - fit(history): Calculate historical volatility and set strategy parameters.
    - execute(row, idx, history) -> dict: Generate trading signals based on volatility breakout.

    """

    def __init__(self, lookback_period=252, multiplier=2):
        super().__init__()
        self.lookback_period = lookback_period
        self.multiplier = multiplier

    def fit(self, history):
        """
        Calculate historical volatility and set strategy parameters.

        Args:
        - history (History): Historical price data of multiple equities.

        Returns:
        None
        """
        pass

    def execute(self, idx: pd.Index, position: pd.Series, history: History) -> pd.Series:
        """
        Generate trading signals based on volatility breakout.

        Args:
        - row (pd.Series): Latest row of equity prices.
        - idx (int): Index of the current row.
        - history (pd.DataFrame): Historical price data of multiple equities.

        Returns:
        dict: Trading signals for each equity.
        """
        signals = pd.Series(Signal("wait"), index=history.df.columns)
        volatility = history.indicators.volatility()

        for idx, equity in enumerate(history.df.columns):
            if volatility[equity].iloc[idx] > self.multiplier * np.mean(
                    volatility[equity].iloc[idx - self.lookback_period: idx]
            ):
                signals[idx] = Signal(TradeType.BUY, 1)
        return signals
