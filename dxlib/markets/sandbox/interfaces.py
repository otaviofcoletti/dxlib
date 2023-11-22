from __future__ import annotations

from ..interfaces import MarketInterface, PortfolioInterface, OrderInterface, MarketUtilities
from ...core import History
from ...core.portfolio import Portfolio
from ...core.security import SecurityManager
from ...core.trading.order import Order, OrderData, OrderType


class SandboxMarket(MarketInterface):
    def __init__(self, allow_backtest: bool = False):
        super().__init__()
        self.identifier = "Sandbox"
        self.security_manager = SecurityManager()
        self.allow_backtest = allow_backtest

        self._history = History(security_manager=self.security_manager)

    def get_price(self, security):
        return self.history.snapshot(security)['close']

    def subscribe(self, security):
        pass

    def __repr__(self):
        return f"{self.identifier}Market"

    @property
    def history(self):
        return self._history


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

    def send(self, order_data: OrderData, market: MarketInterface):
        order = Order.from_type(order_data)
        time = market.history.date()

        if order.data.order_type != OrderType.MARKET:
            raise NotImplementedError("Only market orders are supported in the sandbox.")
        if not time:
            raise ValueError("Market did not show any valid historical bars.")

        order.data.price = MarketUtilities.get_close_price(market, order.data.security)

        order.create_transaction(time)

    def cancel(self, order):
        pass
