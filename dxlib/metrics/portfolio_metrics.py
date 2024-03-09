from ..core import History, Portfolio


class PortfolioMetrics:
    def __init__(self):
        pass

    @classmethod
    def portfolio_value(cls, portfolio: Portfolio, price: History):
        return portfolio.history.apply_on(
            price, lambda row: row['inventory'].value(price[row.name[0]])
        )
