from __future__ import annotations

from abc import ABC, abstractmethod

from ..core.history import History
from ..core.portfolio import Portfolio
from ..core.trading.order import OrderData, Order


class MarketInterface(ABC):
    def __init__(self):
        """
        MarketInterface is an abstract class that defines the interface for a market.

        A market is a source of data for a security and can be used to get historical data or live data.
        Also provides a way to subscribe to a security, and get data updates.
        """
        pass

    @property
    @abstractmethod
    def history(self) -> History:
        """
        Returns the history of the market.
        Returns:
            History: A history object that contains the data for the market, as well as methods for manipulating it.
        """
        pass

    def subscribe(self, security):
        """
        Subscribes to a security and starts receiving data updates.
        Args:
            security: The security to subscribe to.

        Returns:
            An observable that emits data updates for the security.
        """
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
