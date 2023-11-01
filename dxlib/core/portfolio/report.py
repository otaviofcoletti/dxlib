from __future__ import annotations

from .portfolio import Portfolio
from ..history import History
from ..security import Security
from ..indicators import TechnicalIndicators, SeriesIndicators


class Report:
    def metrics(self,
                portfolio: Portfolio,
                history: History = None,
                baseline: Security | list[Security] = None,
                risk_free_rate: float = 0.05,
                window: int = 252):
        _metrics = {}
        if history is None and portfolio.history is None:
            raise ValueError("History is not provided")
        elif history is None:
            history = portfolio.history
        df = history.df

        value = portfolio.historical_value()
        returns = SeriesIndicators.log_change(value, window)

        _metrics = {}

        total_net_profit = returns.sum(axis=1).sum()
        gross_profit = returns[returns > 0].sum(axis=1).sum()
        gross_loss = returns[returns < 0].sum(axis=1).sum()

        profit_factor = gross_profit / gross_loss

        total_trades = len(portfolio.transaction_history)
        percent_profitable = df[df > 0].count(axis=1).sum() / total_trades

        return _metrics