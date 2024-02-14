from abc import ABC, abstractmethod

from .alpaca_markets import *
from .alpha_vantage import *
from .yfinance import *
from ... import History, Portfolio, Order, OrderDetails


class ExternalInterface(ABC):
    pass


class MarketInterface(ExternalInterface, ABC):
    @property
    @abstractmethod
    def history(self) -> History:
        pass

    def subscribe(self, security):
        pass


class MarketUtilities:
    def __init__(self):
        pass

    @staticmethod
    def get_close_price(market, security):
        return market.history.snapshot(security).get(fields="close")


class PortfolioInterface(ExternalInterface, ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def get(self) -> Portfolio:
        pass

    @abstractmethod
    def get_open(self) -> Portfolio:
        pass

    def add(self, order: Order, market: MarketInterface):
        pass


class OrderInterface(ExternalInterface, ABC):
    @abstractmethod
    def send(
        self, order_data: OrderDetails, market: MarketInterface = None, *args, **kwargs
    ) -> Order:
        pass

    def cancel(self, order):
        pass
