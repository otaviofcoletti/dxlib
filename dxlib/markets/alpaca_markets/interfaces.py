from __future__ import annotations

from datetime import datetime

from .api import AlpacaAPI
from ..interfaces import MarketInterface, OrderInterface, PortfolioInterface
from ...core.security import Security
from ...core.portfolio import Portfolio
from ...core.trading.order import OrderData, Order


class AlpacaMarket(MarketInterface):
    def __init__(self, api):
        super().__init__()
        self.api = api

    def get(self, identifier: str | None = None) -> MarketInterface:
        pass

    def history(self):
        return None

    def subscribe(self, security):
        pass


class AlpacaPortfolio(PortfolioInterface):
    def __init__(self, api):
        super().__init__()
        self.api = api

    def get(self, identifier: str | None = None) -> Portfolio:
        pass

    def get_positions(self, identifier):
        pass

    def add(self, order: Order, market: MarketInterface):
        pass


class AlpacaOrder(OrderInterface):
    def __init__(self, api: AlpacaAPI):
        super().__init__()
        self.api = api

    def send(self, order_data: OrderData, market: MarketInterface) -> Order:
        pass

    def cancel(self, order):
        pass

    def get(self, identifier=None, start: datetime = None, end: datetime = None):
        orders = self.api.get_orders()
        filtered_order = None

        if identifier or start or end:
            for order in orders:
                date = datetime.fromisoformat(order['created_at'])
                if order['id'] == identifier:
                    filtered_order = order
                elif start and date >= start:
                    filtered_order = order
                elif end and date <= end:
                    filtered_order = order
        else:
            filtered_order = orders[0]

        if not filtered_order:
            raise ValueError("No order found with the given parameters.")

        return Order(
            security=Security(filtered_order['symbol']),
            quantity=filtered_order['qty'],
            price=filtered_order['filled_avg_price'],
            side=1 if filtered_order['side'] == 'buy' else -1,
            order_type=filtered_order['type'],
            partial=filtered_order['filled_qty'] < filtered_order['qty'],
        )
