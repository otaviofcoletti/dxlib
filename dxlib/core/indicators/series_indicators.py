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

    def log_change(self, series, window=1):
        rolling_change = series / series.shift(window)
        return np.log(rolling_change)

    def relative_log_change(self, series, window=1):
        relative_change = series / series.rolling(window).sum()
        return np.log(relative_change)

    def autocorrelation(self, series, lag=15) -> pd.Series:
        return series.autocorr(lag=lag)

    def acf(self, series, lag=15) -> pd.Series:
        autocorr_series = np.zeros(lag)
        for i in range(lag):
            autocorr_series[i] = series.autocorr(lag=i)

        return pd.Series(autocorr_series)

    def pacf(self, series, lag=15) -> pd.Series:
        pacf_series = np.zeros(lag)
        for i in range(lag):
            pacf_series[i] = series.pacf(lag=i)

        return pd.Series(pacf_series)

    def seasonal_decompose(self, series, period=252):
        return seasonal.seasonal_decompose(series, period=period)
