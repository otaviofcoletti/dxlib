import numpy as np
import pandas as pd

from .series_indicators import SeriesIndicators
from .indicators import Indicators


class TechnicalIndicators(Indicators):
    series_indicators = SeriesIndicators()

    def __init__(self):
        super().__init__()

    @classmethod
    def volatility(cls, series, window=252, period=252):
        # if window == 252 and period == 252 it is calculating annualized volatility over the past trading year
        volatility = series.rolling(window).std() * np.sqrt(1 / period)
        return volatility

    @classmethod
    def drawdown(cls, series):
        return (series / series.cummax()) - 1

    @classmethod
    def sharpe_ratio(cls, series, window=252, risk_free_rate=0.05):
        returns = cls.series_indicators.log_change(series, window)
        excess_returns = returns - risk_free_rate

        return excess_returns.mean() / excess_returns.std()

    @classmethod
    def rsi(cls, series, window=252):
        returns = cls.series_indicators.log_change(series, window)

        up_returns = returns[returns > 0].fillna(0)
        down_returns = returns[returns < 0].fillna(0).abs()

        up_gain = up_returns.ewm(com=window - 1, min_periods=window).mean()
        down_loss = down_returns.ewm(com=window - 1, min_periods=window).mean()

        rs = up_gain / down_loss

        return 100 - (100 / (1 + rs))

    @classmethod
    def beta(cls, series, window=252) -> pd.Series:
        returns = cls.series_indicators.log_change(series, window).dropna()

        betas = {}

        for asset in returns.columns:
            market_returns = returns.drop(columns=[asset]).mean(axis=1)

            asset_returns = returns[asset]

            covariance = asset_returns.cov(market_returns)
            market_variance = market_returns.var()

            beta = covariance / market_variance
            betas[asset] = beta

        return pd.Series(betas)

    @classmethod
    def bollinger_bands(cls, series, window, num_std=2):
        rolling_mean = cls.series_indicators.sma(series, window)
        rolling_std = series.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band

    @classmethod
    def macd(cls, series, fast=12, slow=26, signal=9):
        ema_fast = cls.series_indicators.ema(series, fast)
        ema_slow = cls.series_indicators.ema(series, slow)

        macd = ema_fast - ema_slow
        signal = cls.series_indicators.ema(macd, signal)

        return macd, signal
