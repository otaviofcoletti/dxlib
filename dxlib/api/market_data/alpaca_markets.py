import datetime
import os
from enum import Enum

import pandas as pd

from .data_api import DataApi


class AlpacaMarketsAPI(DataApi):
    def __init__(self, api_key, api_secret):
        super().__init__('https://data.alpaca.markets', api_key, api_secret, 'v2')

    class Endpoints(Enum):
        stocks = 'stocks'
        exchanges = 'exchanges'
        symbols = 'symbols'
        bars = 'bars'

    def get_trades(self, ticker):
        url = self.form_url(f'{self.Endpoints.stocks.value}/trades/latest?symbols={ticker}')
        response = self.get(url)
        return response

    @staticmethod
    def format_trade_data(trade):
        formatted_data = {
            'Time': trade['t'],
            'Exchange': trade['x'],
            'Price': trade['p'],
            'Size': trade['s'],
            'Conditions': ', '.join(trade['c']),
            'ID': trade['i'],
            'Tape': trade['z']
        }
        return formatted_data

    def get_historical_trades(self, tickers, start: datetime.date = None, end: datetime.date = None):
        if isinstance(tickers, str):
            tickers = [tickers]
        start, end = self.date_to_str(self.default_date_interval(start, end))

        ticker_str = ','.join(tickers)
        url = self.form_url(
            f'{self.Endpoints.stocks.value}/trades?symbols={ticker_str}&start={start}&end={end}')
        response = self.get(url)

        formatted_data = []

        for ticker, trades in response['trades'].items():
            for trade in trades:
                formatted_trade = {
                    'Ticker': ticker,
                    'Time': trade['t'],
                    'Exchange': trade['x'],
                    'Price': trade['p'],
                    'Size': trade['s'],
                    'Conditions': ', '.join(trade['c']),
                    'ID': trade['i'],
                    'Tape': trade['z']
                }
                formatted_data.append(formatted_trade)

        return formatted_data

    def _query_historical_bars(self, tickers, timeframe, start, end):
        ticker_str = ','.join(tickers)
        url = self.form_url(
            f'{self.Endpoints.stocks.value}/bars?symbols='
            f'{ticker_str}&start={start}&end={end}&adjustment=all&timeframe={timeframe}')

        response = self.get(url)
        formatted_data = []

        for ticker, bars in response['bars'].items():
            for bar in bars:
                formatted_bar = {
                    'Ticker': ticker,
                    'Time': datetime.datetime.strptime(bar['t'], '%Y-%m-%dT%H:%M:%SZ'),
                    'Open': bar['o'],
                    'High': bar['h'],
                    'Low': bar['l'],
                    'Close': bar['c'],
                    'Volume': bar['v'],
                    'NumTrades': bar['n'],
                    'VWAP': bar['vw']
                }
                formatted_data.append(formatted_bar)
        formatted_df = pd.DataFrame(formatted_data)

        pivoted_df = formatted_df.pivot_table(index='Time', columns='Ticker',
                                              values=['Open', 'High', 'Low', 'Close', 'Volume', 'NumTrades', 'VWAP'])
        return pivoted_df

    def get_historical_bars(self,
                            tickers,
                            start: datetime.date = None,
                            end: datetime.date = None,
                            timeframe="1Day",
                            cache=True):
        tickers = self.format_tickers(tickers)
        start, end = self.date_to_str(self.default_date_interval(start, end))

        cache_filename = self.cache_filename(tickers, start, end, timeframe, "alpaca_market_bars")
        if os.path.exists(cache_filename) and cache:
            return pd.read_csv(cache_filename, header=[0, 1], index_col=0, parse_dates=True)

        historical_bars = self._query_historical_bars(tickers, timeframe, start, end)

        if cache:
            historical_bars.to_csv(cache_filename)

        return historical_bars
