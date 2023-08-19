from json import loads

import pandas as pd
import numpy as np

from .security import Security, SecurityManager
from .indicators import TechnicalIndicators, SeriesIndicators


class Bar(pd.Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class History:
    security_manager = SecurityManager()

    class HistoryIndicators:
        def __init__(self, history):
            self.series: SeriesIndicators = SeriesIndicators(history)
            self.technical: TechnicalIndicators = TechnicalIndicators(history)

        def __getattr__(self, attr):
            if hasattr(self.series, attr):
                return getattr(self.series, attr)
            elif hasattr(self.technical, attr):
                return getattr(self.technical, attr)
            else:
                raise AttributeError(f"'IndicatorsProxy' object has no attribute '{attr}'")

    def __init__(self, df: pd.DataFrame, securities_level=None):
        if securities_level is None and isinstance(df.columns, pd.MultiIndex):
            securities_level = -1

        self._indicators = self.HistoryIndicators(self)
        self._securities_level = securities_level

        symbols = list(df.columns.get_level_values(securities_level).unique())
        self.security_manager.add_securities(symbols)
        self._securities: dict[str, Security] = self.security_manager.get_securities(symbols)

        security_columns = tuple(self._securities.values())

        if isinstance(df.columns, pd.MultiIndex):
            existing_multiindex = df.columns
            new_columns = existing_multiindex.set_levels(security_columns, level=securities_level)
        else:
            new_columns = security_columns

        df.columns = new_columns
        self.df = df

    def __len__(self):
        return len(self.df)

    def __iter__(self):
        return self.df.iterrows()

    def __getitem__(self, item):
        return self.df[item]

    def to_json(self):
        return loads(self.df.to_json())

    @property
    def shape(self):
        return self.df.shape

    @property
    def securities(self):
        return self._securities

    @property
    def indicators(self) -> HistoryIndicators:
        return self._indicators

    def add_security(self, symbol, data):
        if isinstance(data, dict):
            data = pd.Series(data)

        new_series = data.reindex(self.df.index)

        if len(new_series) > len(data):
            new_series[len(data):] = np.nan

        self.df[symbol] = new_series

    def add_row(self, rows: pd.DataFrame | pd.Series, index: pd.Index = None):
        if isinstance(rows, pd.Series):
            rows = pd.DataFrame(rows).T
            rows.index = index
        self.df = pd.concat([self.df, rows])

    def last(self):
        return self.df.iloc[-1]

    def describe(self):
        return self.df.describe()

    def get_securities(self, securities: Security | list[Security]):
        return self.df[securities]

    def get(self, securities: Security | list[Security]):
        if isinstance(securities, str):
            securities = [securities]
        return self.df.loc[:, pd.IndexSlice[:, securities]]

    def get_by_symbols(self, symbols: str | list[str]):
        if isinstance(symbols, str):
            symbols = [symbols]
        securities = self.security_manager.get_securities(symbols).values()
        return self.df.loc[:, pd.IndexSlice[:, securities]]


if __name__ == "__main__":
    # syms: list[str] = ["TSLA", "GOOGL", "MSFT"]
    # price_data = np.array(
    #     [
    #         [150.0, 2500.0, 300.0],
    #         [152.0, 2550.0, 305.0],
    #         [151.5, 2510.0, 302.0],
    #         [155.0, 2555.0, 308.0],
    #         [157.0, 2540.0, 306.0],
    #     ]
    # )
    # price_data = pd.DataFrame(price_data, columns=syms)
    # hist = History(price_data)
    #
    # print(hist.describe())
    #
    # moving_average = hist.indicators.series.sma(window=2)
    # combined_df = pd.concat([hist.df, moving_average.add_suffix("_MA")], axis=1)
    # combined_df.index = pd.to_datetime(combined_df.index)

    from ..api import YFinanceAPI
    historical_bars = YFinanceAPI().get_historical_bars(["TSLA", "AAPL"], cache=False)
    hist = History(historical_bars)
    print(hist.get_by_symbols("TSLA"))
