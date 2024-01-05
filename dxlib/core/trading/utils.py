from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Side(Enum):
    BUY = 1
    SELL = -1

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Side):
            return self.value == other.value
        return False

    def __dict__(self):
        return self.value


@dataclass
class Signal:
    def __init__(self, side: Side, quantity: float, price: float | None = None):
        self.side = side
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return f"{self.side.name}: {self.quantity} @ {self.price}"

    def __dict__(self):
        return {
            "side": self.side.value,
            "quantity": self.quantity,
            "price": self.price,
        }
