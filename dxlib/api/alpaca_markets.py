import datetime
from enum import Enum

import pandas

from .request import Api


class AlpacaMarketsAPI(Api):
    def __init__(self, api_key, api_secret):
        super().__init__(api_key, api_secret, 'https://data.alpaca.markets', 'v2')

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
        if start is None:
            start = datetime.date.today() - datetime.timedelta(days=365)
        if end is None:
            end = datetime.date.today()

        end -= datetime.timedelta(days=1)

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

    def get_historical_bars(self, tickers, timeframe="1Day", start: datetime.date = None, end: datetime.date = None):
        if start is None:
            start = datetime.date.today() - datetime.timedelta(days=365)
        if end is None:
            end = datetime.date.today()

        end -= datetime.timedelta(days=1)

        ticker_str = ','.join(tickers)
        url = self.form_url(
            f'{self.Endpoints.stocks.value}/bars?symbols='
            f'{ticker_str}&start={start}&end={end}&adjustment=raw&timeframe={timeframe}')
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

        return pandas.DataFrame(formatted_data)

    def get_close_bars(self, tickers: list[str] | str = None, bars: pandas.DataFrame = None, values='Close'):
        if tickers is None and bars is None:
            raise ValueError("Must provide either tickers or bars")
        if isinstance(tickers, str):
            tickers = [tickers]
        if bars is None:
            bars = self.get_historical_bars(tickers)

        close_bars = bars.pivot_table(index='Time', columns='Ticker', values=values, aggfunc='mean')
        close_bars.reset_index(drop=True, inplace=True)
        close_bars.columns.name = None
        return close_bars
