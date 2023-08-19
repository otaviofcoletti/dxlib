from json import loads

import pandas as pd
import numpy as np

from .indicators import TechnicalIndicators, SeriesIndicators


class Bar:
    def __init__(self):
        pass


class History:
    class HistoryIndicators:
        def __init__(self, history):
            self.series: SeriesIndicators = SeriesIndicators(history)
            self.technical: TechnicalIndicators = TechnicalIndicators(history)

    def __init__(self, df: pd.DataFrame):
        self._indicators = self.HistoryIndicators(self)
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
    def indicators(self):
        return self._indicators

    @property
    def securities(self):
        return self.df.columns

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

    import seaborn
    import matplotlib.pyplot as plt

    seaborn.set_theme(style="darkgrid")

    seaborn.lineplot(hist.indicators.series.log_change())
    plt.show()

    moving_average = hist.indicators.series.sma(window=2)
    combined_df = pd.concat([hist.df, moving_average.add_suffix("_MA")], axis=1)
    combined_df.index = pd.to_datetime(combined_df.index)

    for sym in syms:
        plt.figure(figsize=(10, 6))
        seaborn.lineplot(
            data=combined_df, x=combined_df.index, y=sym, label="Stock Price"
        )
        seaborn.lineplot(
            data=combined_df,
            x=combined_df.index,
            y=f"{sym}_MA",
            label="Moving Average",
        )
        plt.title(f"{sym} Stock Price and Moving Average")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.show()
