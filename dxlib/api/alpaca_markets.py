from enum import Enum

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

    def get_historical(self, ticker):
        url = self.form_url(
            f'{self.Endpoints.stocks.value}/trades?symbols={ticker}&start=2021-01-03&end=2023-01-03')
        response = self.get(url)
        return response
