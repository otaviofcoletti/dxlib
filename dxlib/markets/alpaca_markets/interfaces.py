from __future__ import annotations

from datetime import datetime

from .api import AlpacaAPI
from ..interfaces import MarketInterface, OrderInterface, PortfolioInterface
from ...core.portfolio import Portfolio, Inventory
from ...core.security import Security, SecurityManager
from ...core.trading import OrderData, Order


class AlpacaMarket(MarketInterface):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.security_manager = SecurityManager()

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

    def get(self, identifier: str | None = None, market: MarketInterface = None) -> Portfolio:
        portfolio = Portfolio()

        account = self.api.get_account()
        portfolio.cash = account['cash']

        positions = self.api.get_positions()

        securities = {market.security_manager.get_security(position['symbol']): position['qty']
                      for position in positions}

        portfolio.register_position(
            Inventory(
                securities=securities,
                source=hash(self)
            )
        )

        return portfolio

    def get_positions(self):
        return self.api.get_positions()

    def add(self, order: Order, market: MarketInterface):
        pass


class AlpacaOrder(OrderInterface):
    def __init__(self, api: AlpacaAPI):
        super().__init__()
        self.api = api

    def cancel(self, order_identifier):
        response = self.api.cancel_order(order_identifier)
        return response

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
            if len(orders) > 0 and filtered_order:
                return Order(
                    security=Security(filtered_order['symbol']),
                    quantity=filtered_order['qty'],
                    price=filtered_order['filled_avg_price'],
                    side=1 if filtered_order['side'] == 'buy' else -1,
                    order_type=filtered_order['type'],
                    partial=filtered_order['filled_qty'] < filtered_order['qty'],
                    identifier=filtered_order['id'],
                )
        else:
            return None

    def post(self, order_data: OrderData, _: MarketInterface = None):
        status = self.api.post_order(
            symbol=order_data.security.ticker,
            qty=order_data.quantity,
            side="buy" if order_data.side.value == 1 else "sell",
            order_type=order_data.order_type.value,
            time_in_force="day",
            limit_price=order_data.price,
        )

        if status.get('status', None) == 'rejected':
            raise ValueError(f"Order rejected: {status.get('reject_reason', None)}")

        return Order.from_type(order_data, identifier=status['id'])
