from __future__ import annotations

import pandas as pd

from ..components import Security, Inventory, History, Schema, SchemaLevel
from ..logger import LoggerMixin


class Portfolio(LoggerMixin):
    def __init__(
            self,
            inventory: Inventory | None = None,
            schema: Schema | None = None,
            logger=None
    ):
        super().__init__(logger)
        self.inventory = inventory if inventory else Inventory()
        self.history = History(schema=schema)

    def __repr__(self):
        return f"Portfolio({len(self.inventory)})"

    def __add__(self, other: Portfolio):
        return Portfolio(
            self.inventory + other.inventory,
        )

    def __iadd__(self, other: Portfolio):
        self.inventory += other.inventory
        return self

    def __iter__(self):
        return iter(self.inventory)

    def __getitem__(self, item):
        return self.inventory[item]

    def __len__(self):
        return len(self.inventory)

    def get(self, security: Security, default: float | int = None):
        return self.inventory.get(security, default)

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

    def to_dict(self, serializable: bool = False):
        return {
            "inventory": self.inventory.to_dict(serializable=serializable),
            "history": self.history.to_dict(serializable=serializable)
        }

    def add(self, inventory: Inventory, idx: any = None):
        self.inventory += inventory

        if idx is not None:
            self.history.add(
                pd.DataFrame({
                    "inventory": [inventory],
                }, index=[idx])
            )

    def add_history(self, history: History | pd.DataFrame | dict):
        if isinstance(history, (dict, pd.DataFrame)):
            history = History(history, self.history.schema)
        self.history.add(history)
        # cumulate inventory from history
        self.inventory += history.df["inventory"].sum()

    @classmethod
    def from_orders(cls, orders: History):
        # aggregate orders into inventory for each date
        inventories = orders.apply({
            SchemaLevel.DATE: lambda x: pd.Series({"inventory": Inventory.from_orders(x["order"].values)})
        })
        return inventories
