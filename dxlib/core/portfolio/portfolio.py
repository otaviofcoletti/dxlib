from __future__ import annotations

import json
from typing import Dict

from ..logger import no_logger

from .inventory import Inventory
from ..trading.order import Order


class Portfolio:
    def __init__(self, inventories: Dict[str, Inventory] | None = None, name: str = None, logger=None):
        self.name: str = name

        self._inventories: Dict[str, Inventory] = inventories if inventories else {}

        self.logger = logger if logger else no_logger(__name__)

    def to_dict(self):
        return {
            "name": str(self.name),
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def register_position(self, inventory: Inventory, identifier: str | None = None):
        if identifier is None:
            identifier = hash(inventory)
        self._inventories[identifier] = inventory

    def value(self, prices: dict[str, float] | None = None):
        return sum([inventory.value(prices) for inventory in self._inventories.values()])

    def financial_weights(self, prices: dict[str, float] | None = None):
        inventory = Inventory()
        for i in self._inventories:
            inventory += i
        return inventory.financial_weights(prices)

    def add(self, orders: Dict[str, Order]):
        self.logger.info(f"Adding order {orders}")

        for identifier in orders:
            if identifier not in self._inventories:
                self._inventories[identifier] = Inventory()
                self.logger.info(f"New inventory: {self._inventories[identifier]}")
            self._inventories[identifier] += orders[identifier].data.quantity
