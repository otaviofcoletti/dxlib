from __future__ import annotations

from typing import Dict

from ..components import Security, Inventory, History, Schema, SchemaLevel, SecurityManager
from ..logger import LoggerMixin


class Portfolio(LoggerMixin):
    def __init__(
            self,
            inventories: Dict[str, Inventory] | Inventory | None = None,
            security_manager: SecurityManager = None,
            logger=None
    ):
        super().__init__(logger)

        if isinstance(inventories, Inventory):
            inventories = {hash(inventories): inventories}

        self._inventories: Dict[str, Inventory] = inventories if inventories else {}
        self.history = History(Schema(
            levels=[SchemaLevel.DATE, SchemaLevel.SECURITY],
            fields=["quantity"],
            security_manager=security_manager if security_manager else SecurityManager()
        ))

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

    def stack(self):
        self.history.df = self.history.df.stack().groupby(level=0).apply(
            lambda x: Inventory({Security(k): v for k, v in x.items()})
        )
        # remove security index level from df and schema
        self.history.df.index = self.history.df.index.droplevel(1)
        self.history.schema.levels = self.history.schema.levels[1:]

    def unstack(self):
        self.history.df = self.history.df.apply(
            lambda x: x.securities
        ).unstack().stack()

        # add security index level to df and schema
        self.history.df.index = self.history.df.index.set_names(["date", "security"])
        self.history.schema.levels = ["date", "security"] + self.history.schema.levels
        return self

    def to_dict(self):
        return {
            "inventories": {
                identifier: inventory.to_dict()
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
