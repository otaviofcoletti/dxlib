import pandas as pd
from pandas import MultiIndex

from ...core import History, Strategy, Inventory, Signal, Side, SchemaLevel
from ...core.indicators.technical_indicators import TechnicalIndicators as ti


class RsiStrategy(Strategy):
    """
    A strategy that generates buy/sell signals based on the RSI indicator.

    Parameters:
    - period (int): Number of days to roll the RSI window.
    - upper (int): the upper threshold to start selling
    - lower (int): the lower threshold to start buying

    Methods:
    - fit(history): Calculate moving averages and identify trends.
    - execute(row, idx, history) -> dict: Generate trading signals based on moving averages.
    """

    def __init__(self,
                 field="close",
                 window=14,
                 upper=70,
                 lower=30,
                 reverse=False):
        super().__init__()
        self.field = field
        self.window = window
        self.upper = upper
        self.lower = lower
        self.reverse = reverse
        self.quantity = 1

    def set(self, quantity: int):
        self.quantity = quantity

    def execute(
            self, observation: any, history: History, position: Inventory=None,
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

        security_level = history.schema.levels.index(SchemaLevel.SECURITY)
        security = idx[security_level]

        # For all securities that have more than self.window days of history, calculate the RSI
        df = history.get_df({SchemaLevel.SECURITY: [security]}, [self.field])
        if len(df) > self.window:
            rsi = ti.rsi(df, self.window).iloc[-1][self.field]

            if rsi > self.upper:
                signals.loc[idx] = Signal(Side.BUY if self.reverse else Side.SELL, self.quantity)
            elif rsi < self.lower:
                signals.loc[idx] = Signal(Side.SELL if self.reverse else Side.BUY, self.quantity)

        return signals
