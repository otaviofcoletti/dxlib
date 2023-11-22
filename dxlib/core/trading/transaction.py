from __future__ import annotations

import math
from enum import Enum
from datetime import datetime

from ..security import Security


class Side(Enum):
    BUY = 1
    SELL = -1

    def __eq__(self, other):
        if isinstance(other, Side):
            return self.value == other.value
        return False

    def serialized(self):
        return self.value

    @staticmethod
    def serialize(side):
        if isinstance(side, Side):
            return side.serialized()
        elif isinstance(side, str):
            return Side[side].serialized()
        elif isinstance(side, int):
            return side
        else:
            raise ValueError("Invalid transaction type")


class TransactionData:
    def __init__(self,
                 security: Security,
                 side: Side,
                 quantity: float | int,
                 price: float | int):
        self.security = security
        self.side = side
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return f"{self.side.name}: {self.security.ticker} {self.quantity} @ {self.price}"

    def __add__(self, other):
        if isinstance(other, TransactionData):
            if self.security == other.security:

                quantity = self.quantity * self.side.value + other.quantity * other.side.value
                side = Side(int(math.copysign(1, quantity)))

                return TransactionData(
                    self.security,
                    side,
                    quantity,
                    self.price,
                )
            else:
                raise ValueError("Cannot add transactions of different securities")
        else:
            raise ValueError("Cannot sum different types of objects for transactions")

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["security"],
            data["side"],
            data["quantity"],
            data["price"],
        )

    @staticmethod
    def serialize(transaction_data):
        if isinstance(transaction_data, TransactionData):
            return transaction_data.serialized()
        elif isinstance(transaction_data, dict):
            return TransactionData.from_dict(transaction_data).serialized()
        else:
            raise ValueError("Invalid transaction data")

    def serialized(self):
        return {
            "security": self.security.serialized(),
            "trade_type": self.side.serialized(),
            "quantity": self.quantity,
            "price": self.price,
        }


class Transaction:
    def __init__(
            self,
            security: Security,
            price: float | int,
            quantity: float | int,
            side: Side,
            timestamp: int | float | datetime | None = None,
    ):
        self._value = 0
        self._data = TransactionData(
            security, side, quantity, price
        )
        self._timestamp = timestamp

    def __repr__(self):
        return (f"{self._data.side.name}: "
                f"{self._data.security.ticker} {self._data.quantity} @ {self._data.price}")

    @property
    def data(self):
        return self._data

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Security(data["security"]),
            Side[data["trade_type"]],
            data["quantity"],
            data["price"],
            data["timestamp"],
        )

    @classmethod
    def from_type(cls, data: TransactionData, timestamp: int | float | datetime | None = None):
        return cls(
            data.security,
            data.side,
            data.quantity,
            data.price,
            timestamp,
        )

    def to_dict(self):
        return {
            "security": self._data.security,
            "side": self._data.side,
            "quantity": float(self._data.quantity),
            "price": float(self._data.price),
            "timestamp": self._timestamp,
        }

    def serialize(self):
        return {
            "security": self._data.security.serialized(),
            "side": self._data.side.serialized(),
            "quantity": float(self._data.quantity),
            "price": float(self._data.price),
            "timestamp": self._timestamp.strftime("%Y-%m-%d %HH:%mm"),
        }
