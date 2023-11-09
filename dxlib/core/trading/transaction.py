from __future__ import annotations

import json
from enum import Enum

from dxlib.core.security import Security
from dxlib.core.history import History


class TransactionType(Enum):
    BUY = 1
    WAIT = 0
    SELL = -1

    def __eq__(self, other):
        if isinstance(other, Transaction):
            return self.value == other.value
        return False


class Transaction:
    _cost = 2e-2

    def __init__(
            self,
            security: Security = None,
            quantity=None,
            price=None,
            trade_type=TransactionType.BUY,
            timestamp=None,
    ):
        self.attributed_histories = {}
        self._price = None
        self._quantity = None
        self._value = None

        self.security = security
        self.trade_type = trade_type
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.trade_type.name}: {self.security.symbol} {self.quantity} @ {self.price}"

    def to_dict(self):
        return {
            "security": self.security.symbol,
            "trade_type": self.trade_type.name,
            "quantity": float(self.quantity),
            "price": float(self.price),
            "timestamp": self.timestamp,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        self._price = price
        if self._quantity and self._price and self.trade_type:
            self._value = (self._price * self._quantity) * self.trade_type.value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        self._quantity = quantity
        if self._quantity and self._price and self.trade_type:
            self._value = (self._price * self._quantity) * self.trade_type.value

    @property
    def value(self):
        return self._value

    @property
    def cost(self):
        return self._cost

    def get_time(self, history: History | None):
        if history is not None:
            return self.attributed_histories[history]
        else:
            return 0
