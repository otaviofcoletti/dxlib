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
        self.security_manager: SecurityManager = security_manager

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
        serial = {}

        for security in df:
            serial[security.ticker] = {
                "bars": df[security]["bars"],
                "dates": [date.strftime("%Y-%m-%d") for date in df[security]["dates"]]
            }

        return {
            "df": serial,
            "security_manager": self.security_manager.to_dict()
        }

    def get_level(self, level: str = 'security'):
        if self.df.empty:
            return []
        return self.df.index.get_level_values(level).unique().tolist()

    def set_level(self, values: list = None, level: str = 'security'):
        if self.df.empty:
            return
        if values is None:
            values = self.get_level(level)
        self.df.index = self.df.index.set_levels(values, level=level)

    def to_dict(self, orient: Literal['dict', 'list', 'series', 'split', 'records', 'index', 'bars'] = 'bars'):
        if orient == 'bars':
            return {
                "df": {
                    security: {
                        "dates": self.get_raw(securities=[security]).index.get_level_values('date').tolist(),
                        "bars": self.get_raw(securities=[security]).values.tolist()
                    } for security in self.get_level()
                },
                "security_manager": self.security_manager.to_dict()
            }
        return {
            "df": self.df.to_dict(orient),
            "security_manager": self.security_manager.to_dict()
        }

    def _get(self, securities, fields, dates):
        mask_dates = self.df.index.get_level_values('date').isin(dates)
        mask_securities = self.df.index.get_level_values('security').isin(securities)

        return self.df[mask_dates & mask_securities][fields]

    def get_raw(self, securities=None, fields=None, dates=None) -> pd.Series | pd.DataFrame:
        if securities is None:
            securities = self.get_level()
        if fields is None:
            fields = self.df.columns.tolist()
        if dates is None:
            dates = self.get_level(level='date')

        df = self._get(securities=securities, fields=fields, dates=dates)

        if len(fields) == 1:
            df = df[fields[0]]
        if len(securities) == 1:
            df = df.xs(securities[0], level='security')
        if len(dates) == 1:
            df = df.xs(dates[0], level='date')

        return df

    def get(self, securities=None, fields=None, dates=None) -> History:
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
        df = self._get(securities=securities, fields=fields, dates=dates)
        return History(df, self.security_manager, identifier=self._identifier)

    def get_interval(self, securities=None, fields=None, intervals: list[tuple[str, str]] = None) -> History:
        dates = self.get_level(level='date')

        if len(intervals) == 1:
            interval = intervals[0]

            closest_interval = [min(dates, key=lambda x: abs(pd.to_datetime(x) - pd.to_datetime(date))) for date in interval]
            dates = dates[dates.index(closest_interval[0]):dates.index(closest_interval[1])]

            return self.get(securities=securities, fields=fields, dates=dates)

        filtered_dates = []
        for start, end in intervals:
            filtered_dates += dates[dates.index(start):dates.index(end)]

        return self.get(securities=securities, fields=fields, dates=filtered_dates)

    def date(self, position=-1):
        if self.df.empty:
            return None
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
        other = other.df if isinstance(other, History) else other
        # Map other index securities to securities in self using security manager
        other_securities = other.index.get_level_values('security').unique().tolist()
        other = other.rename(index=self.security_manager.get(other_securities))
        return History(pd.concat([self.df, other]).drop_duplicates().sort_index(), self.security_manager)

    def __iadd__(self, other: pd.DataFrame | History):
        other = other.df if isinstance(other, History) else other
        # Map other index securities to securities in self using security manager
        other_securities = other.index.get_level_values('security').unique().tolist()
        other = other.rename(index=self.security_manager.get(other_securities))
        self.df = pd.concat([self.df, other]).drop_duplicates().sort_index()
        return self

    def __repr__(self):
        return self.df.__repr__()
