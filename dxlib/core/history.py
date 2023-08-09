import pandas
import numpy


class Bar:
    def __init__(self):
        pass


class History:
    def __init__(self, df: pandas.DataFrame):
        self.df = df

    def add_symbol(self, symbol, data):
        if isinstance(data, dict):
            data = pandas.Series(data)

        new_series = data.reindex(self.df.index)

        if len(new_series) > len(data):
            new_series[len(data):] = numpy.nan

        self.df[symbol] = new_series

    def __len__(self):
        return len(self.df)

    def __iter__(self):
        return self.df.iterrows()

    def __getitem__(self, item):
        return self.df[item]

    def add_row(self, rows: pandas.DataFrame | pandas.Series):
        if isinstance(rows, pandas.Series):
            rows = pandas.DataFrame(rows).T
        self.df = pandas.concat([self.df, rows], ignore_index=True)

    def last(self):
        return self.df.iloc[-1]

    def get_log_returns(self):
        return numpy.log(self.df / self.df.shift(1)).fillna(0)

    def describe(self):
        return self.df.describe()

    def moving_average(self, window):
        moving_average = self.df.rolling(window=window).mean()
        moving_average.iloc[0] = self.df.iloc[0]
        return moving_average

    def bollinger_bands(self, window, num_std=2):
        rolling_mean = self.moving_average(window)
        rolling_std = self.df.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        upper_band.iloc[0] = self.df.iloc[0]
        lower_band.iloc[0] = self.df.iloc[0]
        return upper_band, lower_band


if __name__ == "__main__":
    symbols: list[str] = ['TSLA', 'GOOGL', 'MSFT']
    price_data = numpy.array([
        [150.0, 2500.0, 300.0],
        [152.0, 2550.0, 305.0],
        [151.5, 2510.0, 302.0],
        [155.0, 2555.0, 308.0],
        [157.0, 2540.0, 306.0],
    ])
    price_data = pandas.DataFrame(price_data, columns=symbols)
    history = History(price_data)

    print(history.describe())

    import seaborn
    import matplotlib.pyplot as plt

    seaborn.set_theme(style="darkgrid")

    seaborn.lineplot(history.get_log_returns())
    plt.show()

    moving_average_df = history.moving_average(window=2)
    combined_df = pandas.concat([history.df, moving_average_df.add_suffix('_MA')], axis=1)
    combined_df.index = pandas.to_datetime(combined_df.index)

    for symbol in symbols:
        plt.figure(figsize=(10, 6))
        seaborn.lineplot(data=combined_df, x=combined_df.index, y=symbol, label="Stock Price")
        seaborn.lineplot(data=combined_df, x=combined_df.index, y=f'{symbol}_MA', label="Moving Average")
        plt.title(f"{symbol} Stock Price and Moving Average")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.show()
