from __future__ import annotations

import enum
from typing import List, Dict

import pandas as pd

from .security import SecurityManager


class HistoryLevel(enum.Enum):
    DATE = "date"
    SECURITY = "security"

    @classmethod
    def levels(cls):
        return list(cls.__members__.values())


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
        self.fields = self.df.columns.tolist()

    def __repr__(self):
        return self.df.__repr__()

    def __dict__(self):
        return {
            "df": self.df.to_dict(),
            "security_manager": self.security_manager.__dict__(),
        }

    def __iter__(self):
        return self.df.iterrows()

    def __getitem__(self, item):
        return self.df.loc[item]

    def __add__(self, other: pd.DataFrame | History):
        if isinstance(other, pd.DataFrame):
            other = History(other)

        securities = set(self.get_level(HistoryLevel.SECURITY) + other.get_level(HistoryLevel.SECURITY))
        security_manager = SecurityManager.from_list(list(securities))

        return History(pd.concat([self.df, other.df]), security_manager)

    def __iadd__(self, other: pd.DataFrame | History):
        self.df = self + other
        return self

    @property
    def shape(self):
        return self.df.shape

    def get_level(self, level: HistoryLevel = HistoryLevel.SECURITY):
        if self.df.empty:
            return []
        level = level.value
        return self.df.index.get_level_values(level).unique().tolist()

    def set_level(self, values, level: HistoryLevel = HistoryLevel.SECURITY):
        if self.df.empty:
            return
        self.df.index = self.df.index.set_levels(values, level=level)

    def _get(self, levels: Dict[HistoryLevel, list] = None, fields: List[str] = None) -> pd.DataFrame:
        if self.df.empty:
            return pd.DataFrame()

        # If default levels
        # mask_dates = self.df.index.get_level_values(HistoryLevel.DATE).isin(dates)
        # mask_securities = self.df.index.get_level_values(HistoryLevel.SECURITY).isin(securities)
        #
        # df = self.df[mask_dates & mask_securities]

        # If generic levels
        if levels is None:
            levels = {
                level: self.get_level(level) for level in HistoryLevel.levels()
            }

        if fields is None:
            fields = self.fields

        masks = []
        for level, values in levels.items():
            masks.append(self.df.index.get_level_values(level).isin(values))

        df = self.df[tuple(masks)]

        return df[fields] if not df.empty else pd.DataFrame()

    def _set(self,
             levels: Dict[HistoryLevel, list] = None,
             fields: List[str] = None,
             values: pd.DataFrame | dict = None):
        if self.df.empty:
            return

        if levels is None:
            levels = {
                level: self.get_level(level) for level in HistoryLevel.levels()
            }

        if fields is None:
            fields = self.fields

        if values is None:
            values = pd.DataFrame()

        df = self.df.copy()

        for level, value in levels.items():
            df.index = df.index.set_levels(value, level=level)

        df[fields] = values[fields]

        self.df = df

    def get(self, levels: Dict[HistoryLevel, list] = None, fields: List[str] = None) -> History:
        """
        Get historical data for a given security, field and date

        Args:

        Returns:
            pandas DataFrame with multi-index and fields as columns

        Examples:
            >>> data = {
                    ('2024-01-01', 'AAPL'): Bar(close=155, open=150, high=160, low=140, volume=1000000, vwap=150),
                    ('2024-01-01', 'MSFT'): Bar(close=255, open=250, high=260, low=240, volume=2000000, vwap=250)
                }
            >>> history = History(data)
            >>> history.get(
            # Output:
            # date        security
            # 2024-01-01  AAPL      155
            # Name: close, dtype: int64
        """
        return History(self._get(levels, fields), self.security_manager)

    def add(self, data: pd.DataFrame | History):
        """
        Add historical data to history

        Args:
            data: pandas DataFrame or History object

        Examples:
            >>> bars = {
                    ('2024-01-01', 'AAPL'): Bar(close=155, open=150, high=160, low=140, volume=1000000, vwap=150),
                    ('2024-01-01', 'MSFT'): Bar(close=255, open=250, high=260, low=240, volume=2000000, vwap=250)
                }
            >>> history = History(data)
            >>> history.add({
                    ('2024-01-02', 'AAPL'): Bar(close=160, open=155, high=165, low=145, volume=1000000, vwap=155),
                    ('2024-01-02', 'MSFT'): Bar(close=260, open=255, high=265, low=245, volume=2000000, vwap=255)
                })
            >>> history.get(securities='AAPL', fields='close', dates='2024-01-02')
            # Output:
            # date        security
            # 2024-01-02  AAPL      160
            # Name: close, dtype: int64
        """
        self.df = self + data
        self._update()

    def set(self, fields: List[str] = None, values: pd.DataFrame | dict = None):
        """
        Set historical data for a given security, field and date

        Args:
            fields: list of bar fields
            values: pandas DataFrame or dict with multi-index and bar fields as columns

        Examples:
            >>> history = History()
            >>> history.set(
                    fields=['close'],
                    values={
                        ('2024-01-01', 'AAPL'): 155,
                        ('2024-01-01', 'MSFT'): 255
                    }
                )
            >>> history.get(securities='AAPL', fields='close', dates='2024-01-01')
            # Output:
            # date        security
            # 2024-01-01  AAPL      155
            # Name: close, dtype: int64
        """
        self._set(fields=fields, values=values)
        self._update()

    def _update(self):
        self.security_manager.add(self.get_level())
        self.fields = self.df.columns.tolist()
