import pandas as pd
import numpy as np

from .indicators import Indicators


class SeriesIndicators(Indicators):
    def __init__(self, history):
        super().__init__(history)

    @property
    def df(self) -> pd.DataFrame:
        return self.history.df

    def sma(self, window=20):
        ma = self.df.rolling(window=window).mean()
        ma.iloc[0] = self.df.iloc[0]
        return ma

    def ema(self, window):
        return self.df.ewm(span=window, adjust=False).mean()

    def bollinger_bands(self, window, num_std=2):
        rolling_mean = self.sma(window)
        rolling_std = self.df.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        upper_band.iloc[0] = self.df.iloc[0]
        lower_band.iloc[0] = self.df.iloc[0]
        return upper_band, lower_band

    def log_change(self, window=1, progressive=False):
        rolling_change = self.df / self.df.shift(window)

        if progressive:
            for i in range(0, window):
                rolling_change.iloc[i] = self.df.iloc[i] / self.df.iloc[0]
        return np.log(rolling_change)

    def relative_log_change(self, window=1):
        relative_change = self.df / self.df.rolling(window).sum()

        return np.log(relative_change)

    def volatility(self, window=252, progressive=False, min_interval: int = None):
        if progressive and min_interval is None:
            min_interval = int(np.sqrt(window))
        log_returns = self.log_change()
        volatility = log_returns.rolling(window).std(ddof=0) * np.sqrt(window)

        if progressive:
            for i in range(min_interval, window):
                volatility.iloc[i] = (
                    log_returns.rolling(i).std(ddof=0) * np.sqrt(window)
                ).iloc[i]

        return volatility
