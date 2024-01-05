from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Literal

import pandas as pd

from .indicators import TechnicalIndicators, SeriesIndicators
from .security import SecurityManager


class HistoryLevel(enum.Enum):
    DATE = "date"
    SECURITY = "security"


class History:
    def __init__(self,
                 df: pd.DataFrame | dict = None,
                 security_manager: SecurityManager = None,
                 ):
        """
        History is a multi-indexed dataframe encapsulation
        with dates and securities as the index and bar fields as the columns.

        Args:
            df: pandas DataFrame or dict with multi-index and bar fields as columns
            security_manager: SecurityManager object to keep track of securities
        """
        if security_manager is None:
            security_manager = SecurityManager()

        if df is None:
            self.df = pd.DataFrame()
        elif isinstance(df, dict):
            self.df = pd.DataFrame.from_dict(df, orient='index')
        elif isinstance(df, pd.DataFrame):
            self.df = df

        self.df.index = pd.MultiIndex.from_tuples(self.df.index, names=[HistoryLevel.DATE.value,
                                                                        HistoryLevel.SECURITY.value])

        self.security_manager: SecurityManager = security_manager
        self.security_manager.add(self.get_level())

    def __dict__(self):
        return {
            "df": self.df.to_dict(),
            "security_manager": self.security_manager.__dict__(),
        }

    def get_level(self, level: HistoryLevel = HistoryLevel.SECURITY):
        if self.df.empty:
            return []
        level = level.value
        return self.df.index.get_level_values(level).unique().tolist()

    def set_level(self, values, level: HistoryLevel = HistoryLevel.SECURITY):
        if self.df.empty:
            return
        self.df.index = self.df.index.set_levels(values, level=level)

    def _get(self, securities, fields, dates):
        if self.df.empty:
            return pd.DataFrame()

        mask_dates = self.df.index.get_level_values(HistoryLevel.DATE).isin(dates)
        mask_securities = self.df.index.get_level_values(HistoryLevel.SECURITY).isin(securities)

        df = self.df[mask_dates & mask_securities]

        return df[fields] if not df.empty else pd.DataFrame()

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
        elif len(dates) == 1:
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
        fields = [fields] if isinstance(fields, str) else fields

        dates = dates or self.get_level(level=HistoryLevel.DATE)
        dates = [dates] if isinstance(dates, str) else dates
        df = self._get(securities=securities, fields=fields, dates=dates)
        return History(df, self.security_manager, identifier=self._identifier)

    def date(self, position=-1):
        if self.df.empty:
            return None
        return self.df.index.get_level_values('date').unique().tolist()[position]

    def snapshot(self, securities=None):
        return self.get(securities=securities, dates=self.date())

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
