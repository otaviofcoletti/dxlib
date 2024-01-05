from __future__ import annotations

from ..portfolio.portfolio import Portfolio
from dxlib.core.components.history import History
from ..security import Security
from ..indicators import SeriesIndicators


class Report:
    def metrics(
        self,
        portfolio: Portfolio,
        history: History = None,
        baseline: Security | list[Security] = None,
        risk_free_rate: float = 0.05,
        window: int = 252,
    ):
        _metrics = {}
        if history is None and portfolio.history is None:
            raise ValueError("History is not provided")
        elif history is None:
            history = portfolio.history
        df = history.df

        value = portfolio.historical_value()
        returns = SeriesIndicators.log_change(value, window)

        return _metrics

    def profit(self, returns):
        total_net_profit = returns.sum(axis=1).sum()
        gross_profit = returns[returns > 0].sum(axis=1).sum()
        gross_loss = returns[returns < 0].sum(axis=1).sum()

        profit_factor = gross_profit / gross_loss

        return total_net_profit, gross_profit, gross_loss, profit_factor

    def trades(self, returns):
        average_trade_net_profit = returns.sum(axis=1).mean()
        total_trades = len(returns)
        percent_profitable = returns[returns > 0].count(axis=1).sum() / total_trades

        return total_trades, percent_profitable
