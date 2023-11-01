from __future__ import annotations

from .portfolio import Portfolio
from ..security import Security


class Report:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def metrics(self,
                baseline: Security | list[Security] = None,
                risk_free_rate: float = 0.05,
                window: int = 252):
        _metrics = {}

        total_net_profit = self.df.sum(axis=1).sum()
        gross_profit = self.df[self.df > 0].sum(axis=1).sum()
        gross_loss = self.df[self.df < 0].sum(axis=1).sum()

        profit_factor = gross_profit / gross_loss

        return _metrics