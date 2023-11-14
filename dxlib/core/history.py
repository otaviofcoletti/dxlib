from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from .indicators import TechnicalIndicators, SeriesIndicators
from .security import SecurityManager


@dataclass
class Bar:
    close: float = None
    open: float = None
    high: float = None
    low: float = None
    volume: float = None
    vwap: float = None

    def serialized(self):
        return {
            "close": self.close,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "volume": self.volume,
            "vwap": self.vwap,
        }


class History:
    class Indicators:
        def __init__(self):
            self.series: SeriesIndicators = SeriesIndicators()
            self.technical: TechnicalIndicators = TechnicalIndicators()

        def __getattr__(self, attr):
            if hasattr(self.series, attr):
                return getattr(self.series, attr)
            elif hasattr(self.technical, attr):
                return getattr(self.technical, attr)
            else:
                raise AttributeError(f"'IndicatorsProxy' object has no attribute '{attr}'")

    def __init__(self,
                 df: pd.DataFrame | dict = None,
                 security_manager: SecurityManager = None,
                 identifier=None):
        """
        History is a multi-indexed dataframe encapsulation
        with dates and securities as the index and bar fields as the columns.

        Args:
            df: pandas DataFrame or dict with multi-index and bar fields as columns
            security_manager: SecurityManager object to keep track of securities
            identifier: unique identifier for the history object
        """
        if security_manager is None:
            security_manager = SecurityManager()
        if identifier is None:
            identifier = hash(self)

        if df is None:
            df = pd.DataFrame()
        elif isinstance(df, dict):
            df = pd.DataFrame.from_dict(df, orient='index')
            df.index = pd.MultiIndex.from_tuples(df.index, names=['date', 'security'])

        self.df = df

        self.indicators = self.Indicators()
        self._identifier = identifier
        self.security_manager = security_manager

        self.security_manager.add(self.get_level())
        self.set_level(list(self.security_manager.get(self.get_level()).values()))

    @classmethod
    def from_dict(cls, attributes):
        df = attributes.get("df", None)
        security_manager = attributes.get("security_manager", None)
        return cls(security_manager, df)

    @classmethod
    def serialize(cls, history: History):
        return history.serialized()

    def serialized(self):
        """Serialize the history object into default types for transmission, storage or visualization"""
        df = self.to_dict(orient='bars')['df']

        # Also serialize the security manager and the securities
        for date, securities in df.items():
            for security, bar in securities.items():
                df[date][security.serialized()] = bar.serialized()

        return {
            "df": df,
            "security_manager": self.security_manager.to_dict()
        }

    def get_level(self, level: str = 'security'):
        return self.df.index.get_level_values(level).unique().tolist()

    def set_level(self, values: list = None, level: str = 'security'):
        if values is None:
            values = self.get_level(level)
        self.df.index = self.df.index.set_levels(values, level=level)

    def to_dict(self, orient: Literal['dict', 'list', 'series', 'split', 'records', 'index', 'bars'] = 'bars'):
        if orient == 'bars':
            return {
                "df": {
                    date: group.droplevel(0).to_dict(orient='index')
                    for date, group in self.df.groupby(level=0)
                },
                "security_manager": self.security_manager.to_dict()
            }
        return {
            "df": self.df.to_dict(orient),
            "security_manager": self.security_manager.to_dict()
        }

    def _get(self, securities=None, fields=None, dates=None):
        mask_dates = self.df.index.get_level_values('date').isin(dates)
        mask_securities = self.df.index.get_level_values('security').isin(securities)

        return self.df[mask_dates & mask_securities][fields]

    def get(self, securities=None, fields=None, dates=None):
        """
        Get historical data for a given security, field and date

        Args:
            securities: single security or list of securities
            fields: single bar field or list of bar fields, such as 'close', 'open', 'high', 'low', 'volume', 'vwap'
            dates: single date or list of dates

        Returns:
            pandas DataFrame with multi-index and fields as columns

        Examples:
            >>> data = {
                    ('2023-01-01', 'AAPL'): Bar(close=155, open=150, high=160, low=140, volume=1000000, vwap=150),
                    ('2023-01-01', 'MSFT'): Bar(close=255, open=250, high=260, low=240, volume=2000000, vwap=250)
                }
            >>> history = History(data)
            >>> history.get(securities='AAPL', fields='close', dates='2023-01-01')
            # Output:
            # date        security
            # 2023-01-01  AAPL      155
            # Name: close, dtype: int64
        """
        df = self.df

        securities = list(self.security_manager.get(securities).values()) or self.get_level()
        fields = fields or df.columns.tolist()

        dates = dates or self.get_level(level='date')
        dates = [dates] if isinstance(dates, str) else dates

        if len(fields) == 1 and len(securities) == 1:
            return df.xs(securities[0], level='security')[fields[0]]

        if len(fields) == 1:
            return df.loc[(dates, securities), fields[0]].unstack()

        if len(securities) == 1:
            return df.loc[(dates, securities[0]), fields].droplevel(1)

        return self._get(securities=securities, fields=fields, dates=dates)

    def get_interval(self, securities=None, fields=None, intervals: list[tuple[str, str]] = None):
        dates = self.get_level(level='date')

        if len(intervals) == 1:
            return self.get(securities=securities, fields=fields, dates=intervals[0])

        filtered_dates = []

        for start, end in intervals:
            filtered_dates += dates[dates.index(start):dates.index(end)]

        return self.get(securities=securities, fields=fields, dates=filtered_dates)

    def date(self, position=-1):
        return self.df.index.get_level_values('date').unique().tolist()[position]

    def snapshot(self, securities=None):
        self.get(securities=securities, dates=self.date)

    @property
    def shape(self):
        return self.df.shape

    @property
    def fields(self):
        return self.df.columns.tolist()

    def __len__(self):
        return len(self.df.index.levels[0])

    def __iter__(self):
        return self.df.iterrows()

    def __getitem__(self, item):
        return self.df[item]

    def __add__(self, other: pd.DataFrame | History):
        if isinstance(other, pd.DataFrame):
            return self + History(other, self.security_manager)
        elif isinstance(other, History):
            return History(pd.concat([self.df, other.df]), self.security_manager)

    def __repr__(self):
        return self.df.__repr__()
