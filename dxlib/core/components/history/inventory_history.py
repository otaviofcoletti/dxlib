from datetime import datetime
from typing import Dict

from .history import History
from .schema import HistorySchema
from ..inventory import Inventory


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

    @classmethod
    def from_inventories(cls, inventories: Dict[datetime, Inventory], scheme: HistorySchema | None = None):
        df = {
            (date, security): {"quantity": quantity}
            for date, inventory in inventories.items()
            for security, quantity in inventory.items()
        }
        return cls(df, scheme)
