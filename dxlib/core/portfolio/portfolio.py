from __future__ import annotations

import pandas as pd

from ..components import Security, Inventory, History, SchemaLevel
from ..logger import LoggerMixin


class Portfolio(LoggerMixin):
    def __init__(
            self,
            history: History = None,
            logger=None
    ):
        super().__init__(logger)
        self.history = history or History()

    @property
    def inventory(self):
        # get last inventory from history
        if len(self.history):
            return self.history.df["inventory"].iloc[-1]
        return Inventory()

    def __repr__(self):
        return f"Portfolio({len(self.inventory)})"

    def __add__(self, other: Portfolio):
        return Portfolio(
            self.history + other.history
        )

    def __iadd__(self, other: Portfolio):
        self.history += other.history
        return self

    def __iter__(self):
        return iter(self.history)

    def __getitem__(self, item):
        return self.history[item]

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

    def cumsum(self) -> Portfolio:
        return Portfolio(
            History(
                self.history.df.cumsum(),
                schema=self.history.schema
            )
        )

    def diff(self) -> Portfolio:
        df = self.history.df.diff()
        df.iloc[0] = self.history.df.iloc[0]
        return Portfolio(
            History(
                df,
                schema=self.history.schema
            )
        )

    def to_dict(self, serializable: bool = False):
        return {
            "inventory": self.inventory.to_dict(serializable=serializable),
            "history": self.history.to_dict(serializable=serializable)
        }

    def add(self, idx: any | tuple, inventory: Inventory):
        if not isinstance(idx, tuple):
            idx = (idx,)
        self.add_history(
            {
                idx: {
                    "inventory": inventory
                }
            }
        )

    def add_history(self, history: History | pd.DataFrame | dict):
        if isinstance(history, (dict, pd.DataFrame)):
            history = History(history, self.history.schema)
        self.history.add(history)

    @classmethod
    def from_orders(cls, orders: History):
        # aggregate orders into inventory for each date
        inventories = orders.apply({
            SchemaLevel.DATE: lambda x: pd.Series({"inventory": Inventory.from_orders(x["order"].values)})
        })
        inventories.df = inventories.df.cumsum()

        return cls(
            history=inventories
        )

