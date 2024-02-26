from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..components.security import Security


@dataclass
class Transaction:
    def __init__(
        self,
        security: Security,
        quantity: float,
        price: float,
        execution_time: datetime | None = None,
        exchange: str | None = None,
    ):
        self.security = security
        self.quantity = quantity
        self.price = price
        self.execution_time = execution_time
        self.exchange = exchange

    def __repr__(self):
        return f"Transaction({self.security} {self.quantity} @ {self.price}, T={self.execution_time})"

    def __str__(self):
        return (
            f"{self.security} {self.quantity} @ {self.price}, T={self.execution_time}"
        )

    def to_dict(self):
        return {
            "security": self.security,
            "quantity": self.quantity,
            "price": self.price,
            "execution_time": self.execution_time,
            "exchange": self.exchange,
        }
