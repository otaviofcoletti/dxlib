import pandas as pd

from ..core import History, Portfolio, SchemaLevel

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
        price = prices[row.name[0]]['close'].to_dict()
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
    def return_pct(cls, history: History) -> float:
        return (cls._finalized(history) - cls._starting(history)) / cls._starting(history)

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
    def cash_value(cls, portfolio: Portfolio, prices: History, fees: dict = None) -> Portfolio:
        cash_usage = -cls.value(cls.changes(portfolio), prices)

        fees = fees or {}
        fixed_fees = fees.get('fixed', 0)
        percent_fees = fees.get('percent', 0)

        # for rows in cash usage, calculate the fees
        for idx, row in cash_usage.df.iterrows():
            value = row['value']
            if row['value'] != 0:
                value = value - fixed_fees
            if row['value'] > 0:
                value *= (1 - percent_fees)

            cash_usage.df.loc[idx, 'value'] = value

        cash_value = Portfolio(cash_usage).cumsum()
        return cash_value

    @classmethod
    def equity(cls, portfolio: Portfolio, cash_value: Portfolio, prices: History) -> History:
        value = cls.value(portfolio, prices)
        equity = History(
            value.df + cash_value.history.df,
            schema=value.schema
        )
        return equity

    @classmethod
    def _start(cls, history: History) -> pd.Timestamp:
        return history.df.index.get_level_values(SchemaLevel.DATE.value).min()

    @classmethod
    def _starting(cls, history: History, field='value') -> float:
        return history.df.loc[cls._start(history)][field][0]

    @classmethod
    def _final(cls, history: History) -> float:
        return history.df.index.get_level_values(SchemaLevel.DATE.value).max()

    @classmethod
    def _finalized(cls, history: History, field='value') -> float:
        return history.df.loc[cls._final(history)][field][0]

    @classmethod
    def _peak(cls, history: History) -> float:
        return history.df.max()[0]

    @classmethod
    def metrics(cls, portfolio: Portfolio, cash_value: Portfolio, prices: History):
        equity = cls.equity(portfolio, cash_value, prices)
        return {
            "Start": cls._start(equity),
            "End": cls._final(equity),
            "Duration": cls.duration(portfolio),
            "Exposure Time [%]": cls.exposure_time(portfolio),
            "Equity Final [$]": cls._finalized(equity),
            "Equity Peak [$]": cls._peak(equity),
            "Return [%]": cls.return_pct(equity) * 100,
            # "Buy & Hold Return [%]": cls.get_return(prices) * 100,
            # "Return (Ann.) [%]": cls.get_return(equity) / cls.duration(portfolio).days * 365 * 100,
            # "Volatility (Ann.) [%]": cls.volatility(equity) * 100,
            # "Sharpe Ratio": cls.sharpe_ratio(equity),
            # "Sortino Ratio": cls.sortino_ratio(equity),
            # "Calmar Ratio": cls.calmar_ratio(equity)
        }
