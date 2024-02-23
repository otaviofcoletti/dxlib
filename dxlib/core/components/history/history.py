from __future__ import annotations

from functools import reduce
from typing import List, Dict

import pandas as pd

from .schema import HistorySchema, HistoryLevel
from ..security import SecurityManager


class History:
    def __init__(
            self,
            df: pd.DataFrame | dict | None = None,
            scheme: HistorySchema | None = None,
    ):
        """
        History is a multi-indexed dataframe encapsulation
        with dates and securities as the index and bar fields as the columns.

        Args:
            df: pandas DataFrame or dict with multi-index and bar fields as columns

        """
        if df is None:
            df = pd.DataFrame()
        elif isinstance(df, dict):
            df = pd.DataFrame.from_dict(df, orient="index")
        elif not isinstance(df, pd.DataFrame):
            raise ValueError(f"Invalid type {type(df)} for df")

        if scheme is None:
            scheme = HistorySchema()
        elif not isinstance(scheme, HistorySchema):
            raise ValueError(f"Invalid type {type(scheme)} for scheme")

        df.index = pd.MultiIndex.from_tuples(
            df.index, names=[level.value for level in scheme.levels]
        )

        self._scheme = scheme

        df.index = self.convert_index(df.index)
        self.df = df

    @property
    def scheme(self):
        return self._scheme

    @scheme.setter
    def scheme(self, value: HistorySchema):
        self._scheme = value
        self.df.index = self.convert_index(self.df.index)

    def convert_index(self, index: pd.MultiIndex) -> pd.MultiIndex:
        index = pd.MultiIndex.from_tuples(
            index, names=[level.value for level in self._scheme.levels]
        )
        if HistoryLevel.SECURITY in self.scheme.levels and not index.empty:
            security_level = index.names.index(HistoryLevel.SECURITY.value)
            index = index.set_levels(
                index.levels[security_level].map(self.scheme.security_manager.get),
                level=HistoryLevel.SECURITY.value
            )
        return index

    def __repr__(self):
        return self.df.__repr__()

    def __len__(self):
        return len(self.df)

    def __iter__(self):
        return self.df.iterrows()

    def __getitem__(self, item):
        return self.df.loc[item]

    def __add__(self, other: History):
        if not isinstance(other, History):
            raise ValueError(f"Invalid type {type(other)} for other")

        securities = set(
            self.level_unique(HistoryLevel.SECURITY)
            + other.level_unique(HistoryLevel.SECURITY)
        )
        security_manager = SecurityManager.from_list(list(securities))

        return History(
            pd.concat([self.df, other.df]),
            scheme=HistorySchema(security_manager=security_manager),
        )

    def to_dict(self, serializable=False):
        df_dict = {}
        serialize = self.scheme.serialize
        for idx, bar in self.df.iterrows():
            df_dict[serialize(idx)] = {serialize(k): serialize(v) for k, v in bar.items()}
        return {
            "df": {str(k): v for k, v in df_dict.items()} if serializable else df_dict
        }

    @classmethod
    def from_dict(cls, scheme: HistorySchema = None, serialized=False, **kwargs):
        if scheme is None:
            scheme = HistorySchema()

        to_key = eval if serialized else lambda x: x

        df_dict = {to_key(k): scheme.deserialize(v) for k, v in kwargs["df"].items()}
        df = pd.DataFrame.from_dict(df_dict, orient="index")
        df = scheme.apply_deserialize(df)
        return cls(df, scheme)

    @classmethod
    def from_tuple(cls, history: tuple, scheme: HistorySchema | None = None):
        return cls(
            pd.DataFrame([history[1]], index=pd.MultiIndex.from_tuples([history[0]])),
            scheme,
        )

    @classmethod
    def from_list(cls, history: List[pd.Series], scheme: HistorySchema | None = None):
        return cls(
            pd.DataFrame(pd.concat(history)),
            scheme,
        )

    @property
    def shape(self):
        return self.df.shape

    def level_unique(self, level: HistoryLevel = HistoryLevel.SECURITY):
        return self.df.index.get_level_values(level.value).unique().tolist()

    def levels_unique(
            self, levels: List[HistoryLevel] = None
    ) -> Dict[HistoryLevel, list]:
        if levels is None:
            levels = self._scheme.levels
        return {
            level: self.level_unique(level)
            for level in levels
            if level in self._scheme.levels
        }

    def add(self, data: History | pd.DataFrame | pd.Series | tuple | dict):
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
        if isinstance(data, pd.DataFrame):
            df = data
        elif isinstance(data, History):
            df = data.df
        elif isinstance(data, tuple):
            bar, idx = data
            df = pd.DataFrame([idx], index=pd.MultiIndex.from_tuples([bar]))
        elif isinstance(data, dict) or isinstance(data, pd.Series):
            df = pd.DataFrame(data, columns=self._scheme.fields)
        else:
            raise ValueError(f"Invalid type {type(data)} for data")
        df.index = self.convert_index(df.index)
        self.df = pd.concat([self.df, df])

    def get(
            self, levels: Dict[HistoryLevel, list] = None, fields: List[str] = None
    ) -> History:
        """
        Get historical data for a given security, field and date

        Args:

        Returns:
            pandas DataFrame with multi-index and fields as columns
        """
        return History(self.get_df(levels, fields), self._scheme)

    def get_df(
            self, levels: Dict[HistoryLevel, list] = None, fields: List[str] = None
    ) -> pd.DataFrame:
        if self.df.empty:
            return pd.DataFrame()

        if levels is None:
            levels = self.levels_unique()
        if fields is None:
            fields = self._scheme.fields

        masks = reduce(
            lambda x, y: x & y,
            (
                self.df.index.get_level_values(level.value).isin(values)
                for level, values in levels.items()
            ),
        )

        df = self.df[masks]

        return df[fields] if not df.empty else pd.DataFrame()

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
        if values is None:
            values = pd.DataFrame()

        if isinstance(values, pd.DataFrame):
            values = values.to_dict()
        elif not isinstance(values, dict):
            raise ValueError(f"Invalid type {type(values)} for values")

        self.set_df(fields=fields, values=values)

    def set_df(
            self,
            levels: Dict[HistoryLevel, list] = None,
            fields: List[str] = None,
            values: pd.DataFrame | dict = None,
    ):
        if self.df.empty:
            return

        if levels is None:
            levels = self.levels_unique()
        if fields is None:
            fields = self._scheme.fields

        if values is None:
            values = pd.DataFrame()

        df = self.df.copy()

        for level, value in levels.items():
            df.index = df.index.set_levels(value, level=level)

        df[fields] = values[fields]
        df.index = self.convert_index(df.index)
        self.df = df
