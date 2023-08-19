import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

from .indicators import Indicators


class TechnicalIndicators(Indicators):
    def __init__(self, history):
        super().__init__(history)

    @property
    def df(self):
        return self.history.df

    @property
    def series_indicators(self):
        return self.history.indicators

    def sharpe_ratio(self, periods=252, risk_free_rate=0.05):
        returns = self.series_indicators.log_change()
        daily_risk_free = (1 + risk_free_rate) ** (1 / periods) - 1

        excess_returns = returns - daily_risk_free

        return excess_returns.mean() / excess_returns.std()

    def rsi(self, window=252):
        delta = self.df.diff()

        gain = delta.where(delta > 0, 0).fillna(0)
        loss = -delta.where(delta < 0, 0).fillna(0)

        avg_gain = gain.rolling(window=window, min_periods=1).mean()
        avg_loss = loss.rolling(window=window, min_periods=1).mean()

        rs = avg_gain / avg_loss

        return 100 - (100 / (1 + rs))

    def beta(self) -> pd.Series:
        returns = self.series_indicators.log_change().dropna()

        betas = {}

        for asset in returns.columns:
            market_returns = returns.drop(columns=[asset]).mean(axis=1)

            asset_returns = returns[asset]

            covariance = asset_returns.cov(market_returns)
            market_variance = market_returns.var()

            beta = covariance / market_variance
            betas[asset] = beta

        return pd.Series(betas)

    def drawdown(self):
        return self.df / self.df.cummax() - 1
    
    
    def autocorrelation(self, lag=15) -> pd.Series:

      returns = self.series_indicatos.log_change()

      acorr = returns.autocorr(lag=lag)

      return acorr

    def trend(self):
      decompose_result =  seasonal_decompose(self.df, model="multiplicative", period=252)

      return decompose_result.trend

    def seasonal(self):
      decompose_result =  seasonal_decompose(self.df, model="multiplicative", period=252)

      return decompose_result.seasonal
      
    def residual(self):
      decompose_result =  seasonal_decompose(self.df, model="multiplicative", period=252)

      return decompose_result.resid

    def plot_trend(self):
      trend = self.trend()      
      plt.figure(figsize=(8,3))
      plt.plot(trend)
      plt.grid(color='r', linestyle='--', linewidth=1, alpha=0.3)
      plt.ylabel('TREND')
      plt.show()
      
    def plot_seasonal(self):
      seasonal = self.seasonal()      
      plt.figure(figsize=(8,3))
      plt.plot(seasonal)
      plt.grid(color='r', linestyle='--', linewidth=1, alpha=0.3)
      plt.ylabel('SEASONAL')
      plt.show()

    def plot_residual(self):
      residual = self.residual()
      plt.figure(figsize=(8,3))
      plt.plot(residual)
      plt.grid(color='r', linestyle='--', linewidth=1, alpha=0.3)
      plt.ylabel('RESIDUAL')
      plt.show()
