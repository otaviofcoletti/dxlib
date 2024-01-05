from .interfaces import MarketInterface, OrderInterface, PortfolioInterface
from ..core.security import SecurityManager
from ..core.trading.order import Order, OrderData


class Executor:
    def __init__(
        self,
        market: MarketInterface,
        portfolio: PortfolioInterface,
        order: OrderInterface,
    ):
        self.market = market
        self.portfolio = portfolio
        self.order = order

        self.security_manager = SecurityManager()

    def send_order(self, order_data: OrderData):
        market = self.market
        order = self.order.send(order_data, market)
        self.portfolio.add(order, market)
        return order

    def cancel_order(self, order: Order):
        partial_order = self.order.cancel(order)
        return partial_order

    def subscribe(self, listener: callable = None):
        return self.market.subscribe(listener)
