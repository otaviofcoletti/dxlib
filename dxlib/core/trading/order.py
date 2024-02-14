from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..components import Security
from .transaction import Transaction
from .signal import Side


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

    def __repr__(self):
        return self.name

    def to_json(self):
        return self.value


@dataclass
class OrderDetails:
    def __init__(
        self,
        security: Security,
        price: float | int = None,
        quantity: float | int = 0,
        side: Side | int = Side.BUY,
        order_type: OrderType = OrderType.MARKET,
    ):
        self.security = security
        self.price = price
        self.quantity = quantity
        self.side = side
        self.order_type = order_type

    def __repr__(self):
        return (
            f"OrderDetails({self.side}: {self.security} {self.quantity} @ {self.price})"
        )

    def __str__(self):
        return f"{self.side.name}: {self.security} {self.quantity} @ {self.price}"

    def to_json(self):
        return {
            "security": self.security,
            "price": self.price,
            "quantity": self.quantity,
            "side": self.side.to_json(),
            "order_type": self.order_type.to_json(),
        }


class Order:
    def __init__(
        self,
        data: OrderDetails,
        transactions: list[Transaction] = None,
    ):
        self._data = data
        self._transactions: list[Transaction] = transactions or []

    @property
    def data(self):
        return self._data

    def __repr__(self):
        return f"Order({self.data.__repr__()}, [{len(self._transactions)}])"

    def __str__(self):
        return f"{self.data} -> [{len(self._transactions)} transactions]"

    def to_json(self):
        return {
            "data": self._data.to_json(),
            "transactions": [t.to_json() for t in self._transactions],
        }

    def __getitem__(self, item):
        return self._transactions[item]

    def __len__(self):
        return len(self._transactions)

    def __iter__(self):
        return iter(self._transactions)

    def add_transaction(self, transaction: Transaction | list[Transaction]):
        if transaction.security != self._data.security:
            raise ValueError("Transaction security must match order security")
        if isinstance(transaction, list):
            self._transactions.extend(transaction)
        elif isinstance(transaction, Transaction):
            self._transactions.append(transaction)

    @property
    def executed_quantity(self):
        return sum([t.quantity for t in self._transactions])
