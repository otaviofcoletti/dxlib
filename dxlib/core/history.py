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
