from __future__ import annotations

from datetime import datetime
from typing import AsyncGenerator, Callable

from dxlib.core.components.inventory import Inventory
from dxlib.core.security import Security
from dxlib.core.portfolio import Portfolio
from dxlib.core.trading.order import OrderData, Order, Side

from .api import AlpacaAPI
from dxlib.interfaces.external.external_interfaces import MarketInterface, PortfolioInterface, OrderInterface


class AlpacaMarket(MarketInterface):
    def __init__(self, api: AlpacaAPI):
        super().__init__()
        self.api = api
        self.subscriptions = {}

    def get(self, identifier: str | None = None) -> MarketInterface:
        pass

    def history(self):
        return None

    def subscribe(self, security, method: Callable = None) -> AsyncGenerator | None:
        # If method is passed, call method when new data is received
        # else, return AsyncGenerator
        pass

    def snapshot(self, security):
        pass


class AlpacaPortfolio(PortfolioInterface):
    def __init__(self, api):
        super().__init__()
        self.api = api

    @property
    def name(self):
        return self.api.get_account()["id"]

    def get(self, accumulate=False) -> Portfolio | Inventory:
        inventory = self.api.get_positions()
        portfolio = Portfolio(
            Inventory.from_dict({i["symbol"]: float(i["qty"]) for i in inventory})
        )
        if not accumulate:
            return portfolio
        return portfolio.accumulate()

    def get_open(self) -> Portfolio:
        # Call get_orders() to get all open orders
        open_orders = self.api.get_orders()

        # Sum them up into a single dictionary
        # Then return the Portfolio object
        inventories = {}
        for order in open_orders:
            # If sell order, subtract from inventory
            if order["symbol"] in inventories:
                inventories[order["symbol"]] += float(order["qty"]) * (
                    -1 if order["side"] == "sell" else 1
                )
            else:
                inventories[order["symbol"]] = float(order["qty"]) * (
                    -1 if order["side"] == "sell" else 1
                )

        return Portfolio(Inventory.from_dict(inventories))

    def add(self, order: Order, market: MarketInterface):
        pass


class AlpacaOrder(OrderInterface):
    def __init__(self, api: AlpacaAPI):
        super().__init__()
        self.api = api

    def send(
        self, order_data: OrderData, market: MarketInterface = None, *args, **kwargs
    ) -> Order | None:
        try:
            self.api.submit_order(
                symbol=order_data.security.ticker,
                qty=order_data.quantity,
                side="buy" if order_data.side == Side.BUY else "sell",
                order_type=order_data.order_type.name.lower(),
                time_in_force="gtc",
            )

            return Order(order_data)
        except Exception as e:
            print(e)
            return None

    def cancel(self, order):
        pass

    def get(self, identifier=None, start: datetime = None, end: datetime = None):
        orders = self.api.get_orders()
        filtered_order = None

        if identifier or start or end:
            for order in orders:
                date = datetime.fromisoformat(order["created_at"])
                if order["id"] == identifier:
                    filtered_order = order
                elif start and date >= start:
                    filtered_order = order
                elif end and date <= end:
                    filtered_order = order
        else:
            filtered_order = orders

        if not filtered_order:
            return None

        order = filtered_order[0]

        return Order(
            security=Security(order["symbol"]),
            quantity=order["qty"],
            price=order["filled_avg_price"],
            side=1 if order["side"] == "buy" else -1,
            order_type=order["type"],
            partial=order["filled_qty"] < order["qty"],
        )
