import pandas as pd


class TechnicalIndicators:
    def __init__(self, history):
        self.history = history

    def sharpe_ratio(self, periods=252, risk_free_rate=0.05):
        returns = self.history.log_change()
        daily_risk_free = (1 + risk_free_rate) ** (1/periods) - 1

        excess_returns = returns - daily_risk_free

        return excess_returns.mean() / excess_returns.std()

    def rsi(self, window=252):
        delta = self.history.df.diff()

        gain = delta.where(delta > 0, 0).fillna(0)
        loss = -delta.where(delta < 0, 0).fillna(0)

        avg_gain = gain.rolling(window=window, min_periods=1).mean()
        avg_loss = loss.rolling(window=window, min_periods=1).mean()

        rs = avg_gain / avg_loss

        return 100 - (100 / (1 + rs))

    def beta(self) -> pd.Series:
        returns = self.history.log_change().dropna()

        betas = {}

        for asset in returns.columns:
            market_returns = returns.drop(columns=[asset]).mean(axis=1)

            asset_returns = returns[asset]

            covariance = asset_returns.cov(market_returns)
            market_variance = market_returns.var()

            beta = covariance / market_variance
            betas[asset] = beta

        return pd.Series(betas)
