import requests

from dxlib.interfaces.external.alpaca_markets.routes import routes

from .market import AlpacaMarketAPI, AlpacaStreamAPI
from .order import AlpacaOrderAPI
from .portfolio import AlpacaPortfolioAPI


class UrlBuilder:
    def __init__(self, domain, version="v2"):
        self.domains = routes["domains"]
        self.endpoints = routes["endpoints"]

        self.domain = self.domains[domain]
        self.base_url = self.domain.format(version=version)

    def get(self, *endpoints):
        endpoint = self.endpoints
        for e in endpoints:
            endpoint = endpoint[e]

        return self.base_url + endpoint


class AlpacaAPI:
    class UrlBuilder:
        def __init__(self):
            pass

    def __init__(self, api_key, api_secret, live=False):
        self.__api_key = api_key
        self.__api_secret = api_secret

        self.market_api = AlpacaMarketAPI(api_key, api_secret)
        self.portfolio_api = AlpacaPortfolioAPI()
        self.order_api = AlpacaOrderAPI()
        self.stream_api = AlpacaStreamAPI(api_key, api_secret)

        self.url_builder = UrlBuilder("live" if live else "sandbox")

    def get_account(self):
        response = requests.get(
            self.url_builder.get("account"),
            headers={
                "APCA-API-KEY-ID": self.__api_key,
                "APCA-API-SECRET-KEY": self.__api_secret,
            },
        )

        if response.json().get("code", None) == 40110000:
            raise ConnectionError(
                f"Invalid credentials for selected environment ({self.url_builder.domain})"
            )

        return response.json()

    def get_orders(self):
        response = requests.get(
            self.url_builder.get("orders"),
            headers={
                "APCA-API-KEY-ID": self.__api_key,
                "APCA-API-SECRET-KEY": self.__api_secret,
            },
        )

        return response.json()

    def submit_order(self, symbol, qty, side, order_type, time_in_force=None):
        response = requests.post(
            self.url_builder.get("orders"),
            headers={
                "APCA-API-KEY-ID": self.__api_key,
                "APCA-API-SECRET-KEY": self.__api_secret,
            },
            json={
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "type": order_type,
                "time_in_force": time_in_force,
            },
        )

        return response.json()

    def get_positions(self):
        response = requests.get(
            self.url_builder.get("positions"),
            headers={
                "APCA-API-KEY-ID": self.__api_key,
                "APCA-API-SECRET-KEY": self.__api_secret,
            },
        )

        return response.json()

    def get_stream(self, stream):
        response = requests.get(
            self.url_builder.get("stream", stream),
            headers={
                "APCA-API-KEY-ID": self.__api_key,
                "APCA-API-SECRET-KEY": self.__api_secret,
            },
        )

        return response.json()
