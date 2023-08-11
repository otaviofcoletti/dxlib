from . import Strategy
from .. import Signal, TradeType


class RsiStrategy(Strategy):
    """

    A strategy that generate buy/sell signals based on the RSI indicator.

    Parameters:
    - period (int): Number of days to calculate the RSI 
    - upper_bound (int): the upper threshold to start selling
    - lower_bound (int): the lower threshold to start buying

    Methods:
    - fit(history): Calculate moving averages and identify trends.
    - execute(row, idx, history) -> dict: Generate trading signals based on moving averages.
    """

    def __init__(self, period=14, upper_bound=70, lower_bound=30):
        super().__init__()
        self.period = period
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

    def execute(self, row, idx, history) -> list[Signal]:
        """
        Generate trading signals based on Relative Strength Index(RSI).

        Args:
        - row (pd.Series): Latest row of equity prices.
        - idx (int): Index of the current row.
        - history (pd.DataFrame): Historical price data of multiple equities.

        Returns:
        dict: Trading signals for each equity.
        """

        signals = [Signal(TradeType.WAIT) for _ in range(len(history.columns))]
        if idx > self.period:   
            delta = history.iloc[idx-self.period:idx].diff()

            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            # Calculate the average gain and average loss for the specified period
            avg_gain = gain.mean()
            avg_loss = loss.mean()

            # Calculate the Relative Strength (RS) by dividing the average gain by the average loss
            rs = avg_gain / avg_loss

            # Calculate the Relative Strength Index (RSI)
            RSI = 100 - (100 / (1 + rs))
            
            # if RSI > upper_bound -> SELL
            # if RSI < lower_bound -> BUY
            # ELSE                 -> WAIT
            for idx in enumerate(history.columns):
                if RSI > self.upper_bound: 
                    signals[idx] = Signal(TradeType.SELL, 1)
                elif RSI < self.lower_bound:
                    signals[idx] = Signal(TradeType.BUY, 1)

        return signals