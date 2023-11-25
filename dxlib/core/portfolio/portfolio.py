from __future__ import annotations

import json
from typing import Dict

from .inventory import Inventory
from ..logger import no_logger
from ..trading.order import Order


class Portfolio:
    def __init__(self, inventory: Inventory | None = None, name: str = None, logger=None):
        """
        Manages a collection of inventories.
        Useful for registering trading histories and calculating portfolio value.
        Can be used for backtesting and live trading, and can be used to manage multiple portfolios.

        Args:
            inventory: An inventory to initialize the portfolio with.
            name: The name of the portfolio.
            logger: A logger if you want to log actions taken by the portfolio.
        """
        self.name: str = name

        self._inventory: Inventory = inventory if inventory else Inventory()
        self._orders: Dict[str, Order] = {}

        self.logger = logger if logger else no_logger(__name__)

    def to_dict(self):
        return {
            "name": str(self.name),
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def add_inventory(self, inventory: Inventory):
        self._inventory += inventory

    @property
    def inventory(self):
        return self._inventory

    def value(self, prices: dict[str, float] | None = None):
        return self._inventory.value(prices)

    def financial_weights(self, prices: dict[str, float] | None = None):
        return self._inventory.weights(prices)

    def add(self, orders: Dict[str, Order]):
        """
        Adds orders to the portfolio inventory and transaction history.

        Args:
            orders: A dictionary of orders to add to the portfolio.
        """
        self.logger.info(f"Adding order {orders}")

        self._inventory += [order for order in orders.values()]
        self._orders.update(orders)
