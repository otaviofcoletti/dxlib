from enum import Enum

from .core import Api


class AlpacaMarkets(Api):
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
        print(response)
