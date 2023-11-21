import numpy as np
import pandas as pd
from statsmodels.tsa import seasonal

from .indicators import Indicators


class SeriesIndicators(Indicators):
    def sma(self, series, window=20):
        ma = series.rolling(window=window).mean()
        ma.iloc[0] = series.iloc[0]
        return ma

    def ema(self, series, window=20):
        return series.ewm(span=window, adjust=False).mean()

    def diff(self, series, period=1):
        return series.diff(period)

    def detrend(self, series):
        return series - self.sma(series)

    def returns(self, series):
        return series.pct_change()

    def log_change(self, series, window=1):
        rolling_change = series / series.shift(window)
        return np.log(rolling_change)

    def relative_log_change(self, series, window=1):
        relative_change = series / series.rolling(window).sum()
        return np.log(relative_change)

    def autocorrelation(self, series, lag=15):
        if isinstance(series, pd.DataFrame):
            df = series.apply(self.autocorrelation, lag=lag)
            # Convert to list of autocorrelation values
            return df.iloc[0].tolist()
        else:
            return series.autocorr(lag=lag)

    def pacf(self, series, lag_range=15) -> pd.Series | pd.DataFrame:
        if isinstance(series, pd.DataFrame):
            pacf_series = pd.DataFrame(index=range(lag_range), columns=series.columns)
            for column in series.columns:
                pacf_series[column] = self.pacf(series[column], lag_range=lag_range)
            return pacf_series
        else:
            pacf_series = pd.Series(index=range(lag_range))
            for i in range(lag_range):
                pacf_series.iloc[i] = self.autocorrelation(series, lag=i)
            return pacf_series

    def seasonal_decompose(self, series, period=252):
        return seasonal.seasonal_decompose(series, period=period)
