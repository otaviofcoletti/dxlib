from dataclasses import dataclass

import pandas as pd


@dataclass
class Bar:
    close: float
    open: float = None
    high: float = None
    low: float = None
    volume: float = None
    vwap: float = None


# Sample data using the Bar dataclass, with dates as strings and securities as the keys
sample_data = {
    ('2023-01-01', 'AAPL'): Bar(close=155, open=150, high=160, low=140, volume=1000000, vwap=150),
    ('2023-01-01', 'MSFT'): Bar(close=255, open=250, high=260, low=240, volume=2000000, vwap=250),
    # ... more data
}

sample_data2 = {
    ('2023-01-01', 'TSLA'): Bar(close=155, open=150, high=160, low=140, volume=1000000, vwap=150),
    ('2023-01-02', 'AAPL'): Bar(close=155, open=150, high=160, low=140, volume=1000000, vwap=150),
    ('2023-01-02', 'TSLA'): Bar(close=255, open=250, high=260, low=240, volume=2000000, vwap=250),
}

# Create multi-indexed dataframe from sample data
df = pd.DataFrame.from_dict(sample_data, orient='index')
df.index = pd.MultiIndex.from_tuples(df.index, names=['date', 'security'])

df2 = pd.DataFrame.from_dict(sample_data2, orient='index')
df2.index = pd.MultiIndex.from_tuples(df2.index, names=['date', 'security'])

print(df)

# Get all securities for a given date
print(df.loc['2023-01-01'])

# Get all close prices for a given date
print(df.loc['2023-01-01', 'close'])

# Get all prices for a given security
print(df.xs('AAPL', level='security'))

# Get all prices for multiple securities
# Obs: cant just use .xs(['AAPL', 'MSFT'], level='security') because it will give you a KeyError
print(df.loc[(slice(None), ['AAPL', 'MSFT']), :])

# Get a list of all securities
print(df.index.get_level_values('security').unique().tolist())

print("\nIterate over rows")
print(list(df.iterrows()))

print("Concat")
print(pd.concat([df, df2]))

print("transforming into dict={(date, security): [fields]}}")
print(df.to_dict(orient='index'))

df = pd.concat([df, df2])

from dxlib import History

history = History(df=df)
