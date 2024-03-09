import pandas as pd

from ..core import History, Portfolio, Inventory, Security, SchemaLevel

"""
Start                     2004-08-19 00:00:00
End                       2013-03-01 00:00:00
Duration                   3116 days 00:00:00
Exposure Time [%]                       94.27
Equity Final [$]                     68935.12
Equity Peak [$]                      68991.22
Return [%]                             589.35
Buy & Hold Return [%]                  703.46
Return (Ann.) [%]                       25.42
Volatility (Ann.) [%]                   38.43
Sharpe Ratio                             0.66
Sortino Ratio                            1.30
Calmar Ratio                             0.77
"""


class PortfolioMetrics:
    @classmethod
    def apply_value(cls, row, prices):
        price = prices[row.name[0]]['close']
        return pd.Series(
            {
                "value": row['inventory'].value(price),
            }
        )

    @classmethod
    def value(cls, portfolio: Portfolio, prices: History) -> History:
        return portfolio.history.apply(
            lambda row: cls.apply_value(row, prices),
            axis=1
        )

    @classmethod
    def changes(cls, portfolio: Portfolio) -> Portfolio:
        return portfolio.diff()

    @classmethod
    def duration(cls, portfolio: Portfolio):
        df = portfolio.history.df
        return (df.index.get_level_values(SchemaLevel.DATE.value).max() -
                df.index.get_level_values(SchemaLevel.DATE.value).min()) + pd.Timedelta(days=1)

    @classmethod
    def exposure_time(cls, portfolio: Portfolio):
        changes = cls.changes(portfolio)

        return 1 - (changes.history.df.apply(lambda x: x['inventory'].empty, axis=1)).sum() / len(changes.history)

    @classmethod
    def equity(cls, portfolio: Portfolio, prices: History) -> History:
        cash_usage = -cls.value(portfolio, prices)
        cash_value = Portfolio(cash_usage).cumsum()
        value = cls.value(portfolio.cumsum(), prices)
        return History(
            value.df + cash_value.history.df,
            schema=value.schema
        )
