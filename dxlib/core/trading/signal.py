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

    def to_dict(self) -> dict:
        return {
            "value": self.value
        }

    @classmethod
    def from_dict(cls, **kwargs) -> Side:
        return cls(kwargs["value"])


@dataclass
class Signal:
    def __init__(self, side: Side = Side.WAIT, quantity: float | None = None, price: float | None = None):
        self.side = side
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return f"{self.side.name}: {self.quantity} @ {self.price}"

    def __eq__(self, other):
        if isinstance(other, Signal):
            return self.side == other.side and self.quantity == other.quantity and self.price == other.price
        return False

    def __add__(self, other: Signal | float) -> Signal:
        if isinstance(other, Signal):
            return Signal(
                side=self.side,
                quantity=(self.quantity or 0) + other.quantity,
                price=self.price
            )
        elif isinstance(other, float):
            return Signal(
                side=self.side,
                quantity=(self.quantity or 0) + other,
                price=self.price
            )
        else:
            raise TypeError(f"Cannot add Signal with {type(other)}")

    def to_dict(self) -> dict:
        return {
            "side": self.side.to_dict(),
            "quantity": self.quantity,
            "price": self.price
        }

    @classmethod
    def from_dict(cls, **kwargs) -> Signal:
        return cls(
            side=Side.from_dict(
                **kwargs.get("side")
            ),
            quantity=kwargs.get("quantity"),
            price=kwargs.get("price")
        )
