from __future__ import annotations

from abc import ABC, abstractmethod

from ..core.history import History
from ..core.portfolio import Portfolio
from ..core.trading.order import OrderData, Order


class MarketInterface(ABC):
    def __init__(self):
        pass

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
        return market.history.snapshot(security)['close']


class PortfolioInterface(ABC):
    def __init__(self):
        pass

    def get(self, identifier: str | None = None) -> Portfolio:
        pass

    def add(self, order: Order, market: MarketInterface):
        pass


class OrderInterface(ABC):
    def __init__(self):
        pass

    def send(self, order_data: OrderData, market: MarketInterface) -> Order:
        pass

    def cancel(self, order):
        pass
