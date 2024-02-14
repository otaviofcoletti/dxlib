from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Side(Enum):
    BUY = 1
    WAIT = 0
    SELL = -1

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Side):
            return self.value == other.value
        return False

    def to_json(self):
        return self.value


@dataclass
class Signal:
    def __init__(self, side: Side = Side.WAIT, quantity: float | None = None, price: float | None = None):
        self.side = side
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return f"{self.side.name}: {self.quantity} @ {self.price}"

    def to_json(self):
        return {
            "side": self.side.value,
            "quantity": self.quantity,
            "price": self.price,
        }

    def __eq__(self, other):
        if isinstance(other, Signal):
            return self.side == other.side and self.quantity == other.quantity and self.price == other.price
        return False