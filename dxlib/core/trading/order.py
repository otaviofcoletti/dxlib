from __future__ import annotations

from enum import Enum

from .transaction import Side, Transaction
from ..security import Security


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderData:
    def __init__(self,
                 security: Security,
                 price: float | int = None,
                 quantity: float | int = 0,
                 side: Side | str = Side.BUY,
                 order_type: str = OrderType.MARKET,
                 ):
        self.security = security
        self.price = price
        self.quantity = quantity
        self.side = side if isinstance(side, Side) else Side(side)
        self.order_type = order_type if isinstance(order_type, OrderType) else OrderType(order_type.upper())

    def __repr__(self):
        return f"{self.side.name}: {self.security.ticker} {self.quantity} @ {self.price}"

    def serialized(self):
        return {
            "security": self.security.serialized(),
            "quantity": self.quantity,
            "price": self.price,
            "side": self.side.serialized(),
            "order_type": self.order_type,
        }


class Order:
    def __init__(self,
                 security: Security,
                 quantity: float | int,
                 price: float | int,
                 side: Side,
                 order_type: str,
                 partial: bool = False):
        self._data = OrderData(security, quantity, price, side, order_type)
        self._transactions = []
        self._remaining = quantity
        self._partial = partial

    @property
    def data(self):
        return self._data

    @property
    def finished(self):
        return self._remaining == 0

    def __repr__(self):
        return f"{self.data.side.name}: {self.data.security.ticker} {self.data.quantity} @ {self.data.price}"

    def serialized(self):
        return {
            "data": self.data.serialized(),
            "transactions": [transaction.serialized() for transaction in self._transactions],
            "partial": self._partial,
        }

    def create_transaction(self, time, quantity=None):
        transaction = Transaction(
            self.data.security,
            quantity or self.data.quantity,
            self.data.price,
            self.data.side,
            time,
        )
        self._transactions.append(transaction)
        return transaction

    def add_transaction(self, transaction: Transaction):
        if not self._partial and transaction.data.quantity != self.data.quantity:
            raise ValueError("Order is not partial and transaction quantity does not match order quantity")

        self._transactions.append(transaction)

        if self._partial:
            self._remaining -= transaction.data.quantity

    @classmethod
    def from_type(cls, data: OrderData):
        return cls(
            data.security,
            data.quantity,
            data.price,
            data.side,
            data.order_type,
        )
