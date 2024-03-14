import pandas as pd
from pandas import MultiIndex

from ...core import History, Strategy, Inventory, Signal, Side, SchemaLevel
from ...core.indicators.technical_indicators import TechnicalIndicators as ti


class LongOnlyStrategy(Strategy):
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
                 ):
        super().__init__()
        self.field = field
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
        signals.loc[idx] = Signal(Side.BUY, quantity=self.quantity)

        return signals
