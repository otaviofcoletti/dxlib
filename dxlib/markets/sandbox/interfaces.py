from __future__ import annotations

from ..interfaces import MarketInterface, PortfolioInterface, OrderInterface
from ..market import Market
from ...core.portfolio import Portfolio
from ...core.trading import Transaction
from ...core.trading.order import Order, OrderData, OrderType


class SandboxMarket(MarketInterface):
    def __init__(self, backtest: bool = False):
        super().__init__()
        self.markets = {"sandbox": Market("sandbox")}

    def get(self, identifier: str | None = None) -> Market:
        return self.markets["sandbox"]

    def subscribe(self, security):
        pass


class SandboxPortfolio(PortfolioInterface):
    def __init__(self):
        super().__init__()
        self._portfolio = Portfolio()

    def get(self, identifier=None) -> Portfolio:
        return self._portfolio

    def add(self, order: Order, market: Market):
        self._portfolio.add({market.identifier: order})

    def set(self, portfolio: Portfolio):
        self._portfolio = portfolio


class SandboxOrder(OrderInterface):
    def __init__(self):
        super().__init__()

    def send(self, order_data: OrderData, market: Market):
        order = Order.from_type(order_data)
        time = market.time

        if order.data.order_type != OrderType.MARKET:
            raise NotImplementedError("Only market orders are supported in the sandbox.")

        transaction = order.create_transaction(time)
        order.add_transaction(transaction)

    def cancel(self, order):
        pass

