from __future__ import annotations

from ...core.portfolio import Portfolio
from ...core.security import SecurityManager
from ...core.trading.order import Order, OrderData, OrderType
from ...core import History
from ...servers.endpoint import Endpoint
from ..interfaces import (
    MarketInterface,
    PortfolioInterface,
    OrderInterface,
    MarketUtilities,
)


class SandboxMarket(MarketInterface):
    def __init__(
        self, security_manager=SecurityManager(), allow_backtest: bool = False
    ):
        super().__init__()
        self.identifier = "Sandbox"
        self.security_manager = security_manager
        self.allow_backtest = allow_backtest
        self._history = History()

    @property
    @Endpoint.get("/market/{security}", "Get the entire market history.")
    def history(self) -> History:
        return self._history

    def get_price(self, security):
        return self.history.snapshot(security)["close"]

    def subscribe(self, security):
        pass

    def __repr__(self):
        return f"{self.identifier}Market"


class SandboxPortfolio(PortfolioInterface):
    def __init__(self):
        super().__init__()
        self._portfolio = Portfolio()

    def get(self, identifier=None) -> Portfolio:
        return self._portfolio

    def add(self, order: Order, market: MarketInterface):
        self._portfolio.add({str(market): order})

    def set(self, portfolio: Portfolio):
        self._portfolio = portfolio


class SandboxOrder(OrderInterface):
    def __init__(self):
        super().__init__()

    def send(
        self, order_data: OrderData, market: MarketInterface = None, *args, **kwargs
    ) -> Order:
        order = Order.from_type(order_data)

        if order.data.order_type != OrderType.MARKET:
            raise NotImplementedError(
                "Only market orders are supported in the sandbox."
            )
        if market is None:
            raise NotImplementedError(
                "Pass a market to get the latest reference prices."
            )

        order.data.price = MarketUtilities.get_close_price(market, order.data.security)

        order.create_transaction()
        return order

    def cancel(self, order):
        pass
