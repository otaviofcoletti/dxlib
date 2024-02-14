from __future__ import annotations

from typing import Dict

from dxlib.logger import LoggerMixin

from dxlib.core.components.inventory import Inventory
from ..components import Security


class Portfolio(LoggerMixin):
    def __init__(
        self, inventories: Dict[str, Inventory] | Inventory | None = None, logger=None
    ):
        super().__init__(logger)

        if isinstance(inventories, Inventory):
            inventories = {hash(inventories): inventories}

        self._inventories: Dict[str, Inventory] = inventories if inventories else {}

    def __repr__(self):
        return f"Portfolio({len(self._inventories)})"

    def __add__(self, other: Portfolio):
        return Portfolio(self._inventories | other._inventories)

    def __iadd__(self, other: Portfolio):
        self._inventories = (self + other)._inventories
        return self

    def __iter__(self):
        return iter(self._inventories.values())

    def __getitem__(self, item):
        return self._inventories[item]

    def __len__(self):
        return len(self._inventories)

    def to_json(self):
        return {
            "inventories": {
                identifier: inventory.to_json()
                for identifier, inventory in self._inventories.items()
            }
        }

    def accumulate(self) -> Inventory:
        inventory = Inventory()
        for identifier in self._inventories:
            inventory += self._inventories[identifier]
        return inventory

    def value(self, prices: dict[Security, float] | None = None):
        return sum(
            [inventory.value(prices) for inventory in self._inventories.values()]
        )

    def add(self, inventory: Inventory, identifier: str = None):
        self.logger.debug(f"Adding inventory {inventory} to portfolio")
        if identifier is None:
            identifier = hash(inventory)
        self._inventories[identifier] = inventory
