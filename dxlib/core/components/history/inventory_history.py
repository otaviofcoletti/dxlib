from datetime import datetime
from typing import Dict

import pandas as pd

from .history import History
from .schema import Schema, StandardLevel, StandardSchema
from ..inventory import Inventory
from ...trading import OrderData


class InventoryHistory(History):
    # data = pd.Series({date: dx.OrderData.from_signal(signal, aapl) for date, signal in signals.df["signal"].items()})
    #
    #     prices = history.df["close"]
    #     traded = pd.Series({date: (order.quantity or 0) * order.side.value for date, order in data.items()})
    #     shares = traded.cumsum()
    #     returns = prices.pct_change().shift(-1).fillna(0)
    #     value = ((shares * returns).cumsum() * prices[0]).reset_index()[0]
    #     shares = shares.reset_index()[0]
    def __repr__(self):
        return f"InventoryHistory({self.df.__repr__()})"

    @staticmethod
    def _unstack(inventory):
        # transform inventory into pd.Series
        return pd.Series(inventory)

    def unstack(self) -> History:
        # Break each row inventory into its own columns
        # This is useful for plotting
        # for each inventory (row) call inventory.items() to get cols
        df = self.df.apply(
            lambda row: self._unstack(row["inventory"]),
            axis=1
        )

        df = pd.DataFrame(df.stack(), columns=["quantity"])

        schema = StandardSchema(
            levels=[StandardLevel.DATE, StandardLevel.SECURITY],
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
        inventory_schema = StandardSchema(
            levels=[StandardLevel.DATE],
            fields=["inventory"],
            security_manager=schema.security_manager
        )

        security_index = schema.levels.index(StandardLevel.SECURITY)
        df_group = df.groupby(StandardLevel.DATE.value).apply(cls._stack, security_index)
        return cls(df_group, inventory_schema)

    @classmethod
    def from_inventories(cls, inventories: Dict[datetime, Inventory], scheme: Schema | None = None):
        df = {
            (date, security): {"quantity": quantity}
            for date, inventory in inventories.items()
            for security, quantity in inventory.items()
        }
        return cls(df, scheme)
