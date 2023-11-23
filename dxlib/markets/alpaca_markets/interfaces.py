from __future__ import annotations

import requests

from ...core.portfolio import Portfolio
from ...core.trading.order import OrderData, Order
from ..interfaces import MarketInterface, OrderInterface, PortfolioInterface


class AlpacaAPI:
    class UrlBuilder:
        def __init__(self):
            pass

    from .routes import routes

    def __init__(self, api_key, api_secret, live=False):
        self._domain = self.routes["domains"]["live"] if live else self.routes["domains"]["sandbox"]
        self.__api_key = api_key
        self.__api_secret = api_secret
        self._version = "v2"

    def get_account(self):
        response = requests.get(self._domain.format(version=self._version) + self.routes["endpoints"]["account"],
                                headers={
                                    "APCA-API-KEY-ID": self.__api_key,
                                    "APCA-API-SECRET-KEY": self.__api_secret
                                })

        if response.json().get("code", None) == 40110000:
            raise ConnectionError(f"Invalid credentials for selected environment ({self._domain})")

        return response.json()


class AlpacaMarket(MarketInterface):
    def get(self, identifier: str | None = None) -> MarketInterface:
        pass

    def history(self):
        return None

    def subscribe(self, security):
        pass


class AlpacaPortfolio(PortfolioInterface):
    def __init__(self, api_key, api_secret):
        super().__init__()

        self.api_key = api_key
        self.api_secret = api_secret

    def get(self, identifier: str | None = None) -> Portfolio:
        pass

    def get_positions(self, identifier):
        pass

    def add(self, order: Order, market: MarketInterface):
        pass


class AlpacaOrder(OrderInterface):
    def send(self, order_data: OrderData, market: MarketInterface) -> Order:
        pass

    def cancel(self, order):
        pass
