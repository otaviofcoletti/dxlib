from __future__ import annotations

import numpy as np
import pandas as pd

from .indicators import TechnicalIndicators, SeriesIndicators
from .security import Security, SecurityManager


class Bar(pd.Series):
    def __init__(self, bar: str | tuple, *args, **kwargs):
        super().__init__(*args, **kwargs)
        symbol = None
        if isinstance(bar, str):
            symbol = bar
        elif isinstance(bar, tuple):
            symbol, data = bar
        self.symbol = symbol
        self.index = pd.to_datetime(kwargs["index"]) if kwargs.get("index", None) else None

    def __getattr__(self, attr):
        if hasattr(self, attr):
            return getattr(self, attr)
        else:
            raise AttributeError(f"'Bar' object has no attribute '{attr}'")

    def __getitem__(self, item):
        return self[item]


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
                 security_manager: SecurityManager = None,
                 df: pd.DataFrame | tuple | list[dict] | dict = None,
                 securities_level=None,
                 identifier=None):
        if security_manager is None:
            security_manager = SecurityManager()
        if df is None:
            df = pd.DataFrame()
        if identifier is None:
            identifier = hash(self)

        if isinstance(df, tuple):
            idx, row = df
            df = pd.DataFrame(row).transpose()
        elif isinstance(df, list):
            df = pd.DataFrame(df)

        if securities_level is None:
            securities_level = -1

        self.indicators = self.Indicators()
        self._securities_level = securities_level
        self._identifier = identifier
        self.security_manager = security_manager

        tickers = list(df.columns.get_level_values(securities_level).unique())
        self.security_manager.add(tickers)
        _securities: dict[str, Security] = self.security_manager.get(tickers)
        security_columns = tuple(_securities.values())

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.set_levels(security_columns, level=securities_level)
        else:
            df.columns = security_columns

        self.df = df

    def __len__(self):
        return len(self.df)

    def __iter__(self):
        return self.df.iterrows()

    def __getitem__(self, item):
        return self.df[item]

    def __add__(self, other: pd.DataFrame | History):
        if isinstance(other, pd.DataFrame):
            return self + History(self.security_manager, other)
        elif isinstance(other, History):
            return History(self.security_manager, pd.concat([self.df, other.df]).sort_index())

    def to_dict(self):
        return {
            "df": self.df.to_dict(),
            "security_manager": self.security_manager.to_dict()
        }

    @classmethod
    def from_dict(cls, attributes):
        df = attributes.get("df", None)
        security_manager = attributes.get("security_manager", None)
        return cls(security_manager, df)

    def serialize_multiindex(self):
        # Return list of lists for each level of the multiindex
        return [self.df.columns.get_level_values(i).unique().tolist() for i in range(self.df.columns.nlevels)]

    def serialized(self):
        return {
            "identifier": self._identifier,
            "df": {
                "index": self.df.index.strftime("%Y-%m-%d %H:%M:%S").tolist(),
                "columns": self.serialize_multiindex(),
            },
            "security_manager": self.security_manager.serialized()
        }

    @property
    def shape(self):
        return self.df.shape

    @property
    def start(self):
        return self.df.index[0]

    @property
    def end(self):
        return self.df.index[-1]

    def add_security(self, ticker, data):
        if isinstance(data, dict):
            data = pd.Series(data)

        new_series = data.reindex(self.df.index)

        if len(new_series) > len(data):
            new_series[len(data):] = np.nan

        self.df[ticker] = new_series

    def add_row(self, rows: pd.DataFrame | pd.Series, index: pd.Index = None):
        if isinstance(rows, pd.Series):
            rows = pd.DataFrame(rows).T
            rows.index = index
        self.df = pd.concat([self.df, rows])

    def last(self):
        return self.df.iloc[-1]

    def describe(self):
        return self.df.describe()

    def get(self, securities: Security | list[Security]):
        if isinstance(securities, str):
            securities = [securities]
        return self.df.loc[:, pd.IndexSlice[:, securities]]

    def get_by_ticker(self, ticker: str | list[str]):
        if isinstance(ticker, str):
            ticker = [ticker]
        securities = self.security_manager.get(ticker).values()
        return self.df.loc[:, pd.IndexSlice[:, securities]]

    def time(self):
        if len(self.df) == 0:
            return None
        return self.df.index[-1]
