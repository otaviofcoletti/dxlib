from __future__ import annotations

from abc import ABC, abstractmethod

from ..core.history import History
from ..core.portfolio import Portfolio
from ..core.trading.order import OrderData, Order
from ..managers.handler import MessageHandler


class Interface(ABC):
    def __init__(self):
        self.message_handler: MessageHandler | None = None
    pass


class MarketInterface(Interface, ABC):
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


class PortfolioInterface(Interface, ABC):
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


class OrderInterface(Interface, ABC):
    @abstractmethod
    def send(self, order_data: OrderData, market: MarketInterface = None, *args, **kwargs) -> Order:
        pass

    def cancel(self, order):
        pass
