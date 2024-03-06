from __future__ import annotations

from typing import Dict

from ..components import Security, Inventory, History
from ..logger import LoggerMixin


class InventoryHistory(History):
    def __repr__(self):
        return f"InventoryHistory({self.df.__repr__()})"

    def unstack(self) -> History:
        # Break each row inventory into its own columns
        # This is useful for plotting
        # for each inventory (row) call inventory.items() to get cols
        df = self.df.apply(
            lambda row: self._unstack(row["inventory"]),
            axis=1
        )

        df = pd.DataFrame(df.stack(), columns=["quantity"])

        schema = Schema(
            levels=[SchemaLevel.DATE, SchemaLevel.SECURITY],
            fields=["quantity"],
            security_manager=self.schema.security_manager
        )

        return History(df, schema)

    @staticmethod
    def _to_order(row, index):
        security = row.name[index]
        return pd.Series({'order_data': OrderData.from_signal(row['signal'], security)})

    @classmethod
    def _stack(cls, inventory: pd.DataFrame, index):
        inventory = inventory.apply(cls._to_order, axis=1, index=index)['order_data'].to_list()
        return pd.Series({"inventory": Inventory.from_order_data(inventory)})

    @classmethod
    def stack(cls, df: pd.DataFrame, schema: Schema) -> "InventoryHistory":
        # Stack the dataframe into a single column
        # This is useful for running a strategy
        inventory_schema = Schema(
            levels=[SchemaLevel.DATE],
            fields=["inventory"],
            security_manager=schema.security_manager
        )

        security_index = schema.levels.index(SchemaLevel.SECURITY)
        df_group = df.groupby(SchemaLevel.DATE.value).apply(cls._stack, security_index)
        return cls(df_group, inventory_schema)

    @classmethod
    def from_inventories(cls, inventories: Dict[datetime, Inventory], scheme: Schema | None = None):
        df = {
            (date, security): {"quantity": quantity}
            for date, inventory in inventories.items()
            for security, quantity in inventory.items()
        }
        return cls(df, scheme)


class Portfolio(LoggerMixin):
    def __init__(
        self, inventories: Dict[str, Inventory] | Inventory | None = None, logger=None
    ):
        super().__init__(logger)

        if isinstance(inventories, Inventory):
            inventories = {hash(inventories): inventories}

        self._inventories: Dict[str, Inventory] = inventories if inventories else {}
        self.history = InventoryHistory()

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
