import pandas as pd
import numpy as np
from .indicators import TechnicalIndicators


class Bar:
    def __init__(self):
        pass


class History:
    def __init__(self, df: pd.DataFrame):
        self._technical_indicators = TechnicalIndicators(self)
        self.df = df

    def add_symbol(self, symbol, data):
        if isinstance(data, dict):
            data = pd.Series(data)

        new_series = data.reindex(self.df.index)

        if len(new_series) > len(data):
            new_series[len(data):] = np.nan

        self.df[symbol] = new_series

    def __len__(self):
        return len(self.df)

    def __iter__(self):
        return self.df.iterrows()

    def __getitem__(self, item):
        return self.df[item]

    @property
    def shape(self):
        return self.df.shape

    @property
    def indicators(self):
        return self._technical_indicators

    def add_row(self, rows: pd.DataFrame | pd.Series, index: pd.Index = None):
        if isinstance(rows, pd.Series):
            rows = pd.DataFrame(rows).T
            rows.index = index
        self.df = pd.concat([self.df, rows])

    def last(self):
        return self.df.iloc[-1]

    def describe(self):
        return self.df.describe()

    def moving_average(self, window):
        moving_average = self.df.rolling(window=window).mean()
        moving_average.iloc[0] = self.df.iloc[0]
        return moving_average

    def exponential_moving_average(self, window):
        return self.df.ewm(span=window, adjust=False).mean()

    def bollinger_bands(self, window, num_std=2):
        rolling_mean = self.moving_average(window)
        rolling_std = self.df.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        upper_band.iloc[0] = self.df.iloc[0]
        lower_band.iloc[0] = self.df.iloc[0]
        return upper_band, lower_band

    def log_change(self, window=1, progressive=False):
        rolling_change = self.df / self.df.shift(window)

        if progressive:
            for i in range(0, window):
                rolling_change.iloc[i] = self.df.iloc[i] / self.df.iloc[0]
        return np.log(rolling_change)

    def relative_log_change(self, window=1):
        relative_change = self.df / self.df.rolling(window).sum()

        return np.log(relative_change)

    def volatility(self, window=252, progressive=False, min_interval: int = None):
        if progressive and min_interval is None:
            min_interval = int(np.sqrt(window))
        log_returns = self.log_change()
        rolling_volatility = log_returns.rolling(window).std(ddof=0) * np.sqrt(window)

        if progressive:
            for i in range(min_interval, window):
                rolling_volatility.iloc[i] = (log_returns.rolling(i).std(ddof=0) * np.sqrt(window)).iloc[i]

        return rolling_volatility

    def drawdown(self):
        return self.df / self.df.cummax() - 1


if __name__ == "__main__":
    symbols: list[str] = ['TSLA', 'GOOGL', 'MSFT']
    price_data = np.array([
        [150.0, 2500.0, 300.0],
        [152.0, 2550.0, 305.0],
        [151.5, 2510.0, 302.0],
        [155.0, 2555.0, 308.0],
        [157.0, 2540.0, 306.0],
    ])
    price_data = pd.DataFrame(price_data, columns=symbols)
    history = History(price_data)

    print(history.describe())

    import seaborn
    import matplotlib.pyplot as plt

    seaborn.set_theme(style="darkgrid")

    seaborn.lineplot(history.log_change())
    plt.show()

    moving_average_df = history.moving_average(window=2)
    combined_df = pd.concat([history.df, moving_average_df.add_suffix('_MA')], axis=1)
    combined_df.index = pd.to_datetime(combined_df.index)

    for symbol in symbols:
        plt.figure(figsize=(10, 6))
        seaborn.lineplot(data=combined_df, x=combined_df.index, y=symbol, label="Stock Price")
        seaborn.lineplot(data=combined_df, x=combined_df.index, y=f'{symbol}_MA', label="Moving Average")
        plt.title(f"{symbol} Stock Price and Moving Average")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.show()
