from __future__ import annotations

from abc import ABC

from .market import Market
from ..core.portfolio import Portfolio
from ..core.trading.order import OrderData, Order


class MarketInterface(ABC):
    def __init__(self):
        pass

    def get(self, identifier: str | None = None) -> Market:
        pass

    def subscribe(self, security):
        pass


class PortfolioInterface(ABC):
    def __init__(self):
        pass

    def get(self, identifier: str | None = None) -> Portfolio:
        pass

    def add(self, order: Order, market: Market):
        pass


class OrderInterface(ABC):
    def __init__(self):
        pass

    def send(self, order_data: OrderData, market: Market) -> Order:
        pass

    def cancel(self, order):
        pass
