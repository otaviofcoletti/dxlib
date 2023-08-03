import pandas
import numpy


class Bar:
    def __init__(self):
        pass


class History:
    def __init__(self, df):
        self.df = df

    def add_symbol(self, symbol, data):
        if isinstance(data, dict):
            data = pandas.Series(data)

        new_series = data.reindex(self.df.index)

        if len(new_series) > len(data):
            new_series[len(data):] = numpy.nan

        self.df[symbol] = new_series
