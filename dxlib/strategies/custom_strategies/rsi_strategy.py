import pandas as pd
from pandas import MultiIndex

from ... import Inventory, Signal, Side, HistoryLevel
from ...core import History, Strategy
from ...core.indicators.technical_indicators import TechnicalIndicators as ti


class RsiStrategy(Strategy):
    """
    A strategy that generates buy/sell signals based on the RSI indicator.

    Parameters:
    - period (int): Number of days to roll the RSI window.
    - upper_bound (int): the upper threshold to start selling
    - lower_bound (int): the lower threshold to start buying

    Methods:
    - fit(history): Calculate moving averages and identify trends.
    - execute(row, idx, history) -> dict: Generate trading signals based on moving averages.
    """

    def __init__(self,
                 field="close",
                 window=14,
                 upper_bound=70,
                 lower_bound=30):
        super().__init__()
        self.field = field
        self.window = window
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    def fit(self, history):
        """
        Calculate moving averages and identify trends.

        Args:
        - history (History): Historical price data of multiple equities.

        Returns:
        None
        """
        pass

    def execute(
            self, observation: any, position: Inventory, history: History
    ) -> pd.Series:  # pd.Series[TradeSignal]
        """
        Generate trading signals based on Relative Strength Index(RSI).

        Args:
        - row (pd.Series): Latest row of equity prices.
        - idx (int): Index of the current row.
        - history (pd.DataFrame): Historical price data of multiple equities.

        Returns:
        dict: Trading signals for each equity.
        """
        levels = history.levels_unique()
        idx, _ = observation
        signals = pd.Series(
            Signal(Side.WAIT), index=MultiIndex.from_tuples([idx], names=levels.keys())
        )
        date, security = idx

        # For all securities that have more than self.window days of history, calculate the RSI
        df = history.get_df({HistoryLevel.SECURITY: [security]}, [self.field])
        if len(df) > self.window:
            rsi = ti.rsi(df, self.window).iloc[-1][self.field]

            if rsi > self.upper_bound:
                signals.loc[idx] = Signal(Side.SELL, 1)
            elif rsi < self.lower_bound:
                signals.loc[idx] = Signal(Side.BUY, 1)

        return signals
