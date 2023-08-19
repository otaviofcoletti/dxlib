from json import loads

import pandas as pd
import numpy as np

from .security import Security, SecurityManager
from .indicators import TechnicalIndicators, SeriesIndicators


class Bar(pd.Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def elefante(self):
        return self.index


class History:
    security_manager = SecurityManager()

    class HistoryIndicators:
        def __init__(self, history):
            self.series: SeriesIndicators = SeriesIndicators(history)
            self.technical: TechnicalIndicators = TechnicalIndicators(history)

        def __getattr__(self, attr):
            # Try to get the attribute from series_indicators, and then from technical_indicators
            if hasattr(self.series, attr):
                return getattr(self.series, attr)
            elif hasattr(self.technical, attr):
                return getattr(self.technical, attr)
            else:
                raise AttributeError(f"'IndicatorsProxy' object has no attribute '{attr}'")

    def __init__(self, df: pd.DataFrame):
        self._indicators = self.HistoryIndicators(self)
        self._securities: dict[str, Security] = self.security_manager.get_securities(list(df.columns))

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


if __name__ == "__main__":
    syms: list[str] = ["TSLA", "GOOGL", "MSFT"]
    price_data = np.array(
        [
            [150.0, 2500.0, 300.0],
            [152.0, 2550.0, 305.0],
            [151.5, 2510.0, 302.0],
            [155.0, 2555.0, 308.0],
            [157.0, 2540.0, 306.0],
        ]
    )
    price_data = pd.DataFrame(price_data, columns=syms)
    hist = History(price_data)

    print(hist.describe())

    moving_average = hist.indicators.series.sma(window=2)
    combined_df = pd.concat([hist.df, moving_average.add_suffix("_MA")], axis=1)
    combined_df.index = pd.to_datetime(combined_df.index)

    from ..api import YFinanceAPI
    historical_bars = YFinanceAPI().get_historical_bars(["TSLA", "AAPL"], cache=False)
    print(hist.securities)
    print(hist.indicators.technical.autocorrelation(1))
